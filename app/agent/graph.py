import json
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agent.evidence import summarize_tool_outputs
from app.agent.prompts import TRIAGE_SYSTEM_PROMPT
from app.agent.response_validator import (
    find_missing_sections,
    find_quality_issues,
    is_quality_acceptable,
    is_valid_answer,
)
from app.agent.source_footer import ensure_tool_footer
from app.agent.state import AgentState
from app.agent.tool_planner import plan_tools
from app.llm.ollama_client import chat
from app.rag.retriever import retrieve
from app.tools.deployments import get_recent_deployments
from app.tools.log_search import search_logs
from app.tools.service_health import check_service_health


def build_rag_context(chunks: list[dict[str, Any]]) -> str:
    context_parts = []

    for item in chunks:
        source = item["metadata"].get("source", "unknown")
        chunk_index = item["metadata"].get("chunk_index", "unknown")
        text = item["text"]

        context_parts.append(
            f"""
SOURCE FILE: {source}
CHUNK INDEX: {chunk_index}

CONTENT:
{text}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)


def retrieve_context_node(state: AgentState) -> AgentState:
    question = state["question"]

    retrieved_chunks = retrieve(question)
    rag_context = build_rag_context(retrieved_chunks)

    return {
        "retrieved_chunks": retrieved_chunks,
        "rag_context": rag_context,
    }


def plan_tools_node(state: AgentState) -> AgentState:
    question = state["question"]
    tool_plan = plan_tools(question)

    return {
        "tool_plan": tool_plan,
        "selected_tools": tool_plan["tools"],
    }


def collect_tool_evidence_node(state: AgentState) -> AgentState:
    tool_plan = state["tool_plan"]

    service = tool_plan["service"]
    log_keyword = tool_plan["log_keyword"]

    service_health = {
        service: check_service_health(service),
    }

    if service == "checkout-api":
        service_health["payment-service"] = check_service_health("payment-service")
        service_health["orders-db"] = check_service_health("orders-db")

    tool_outputs = {
        "tool_plan": tool_plan,
        "log_search": {
            "tool_name": "log_search",
            "service": service,
            "keyword": log_keyword,
            "results": search_logs(service, log_keyword),
        },
        "service_health": {
            "tool_name": "service_health",
            "results": service_health,
        },
        "deployments": {
            "tool_name": "deployments",
            "service": service,
            "results": get_recent_deployments(service),
        },
    }

    return {
        "tool_outputs": tool_outputs,
    }


def summarize_evidence_node(state: AgentState) -> AgentState:
    tool_outputs = state.get("tool_outputs", {})
    evidence_summary = summarize_tool_outputs(tool_outputs)

    return {
        "evidence_summary": evidence_summary,
    }


def generate_answer_node(state: AgentState) -> AgentState:
    question = state["question"]
    rag_context = state.get("rag_context", "")
    evidence_summary = state.get("evidence_summary", "")
    tool_outputs = state.get("tool_outputs", {})

    user_prompt = f"""
Question:
{question}

Retrieved runbook context:
{rag_context}

Deterministic evidence summary:
{evidence_summary}

Raw tool outputs for reference:
{json.dumps(tool_outputs, indent=2)}

Answer with this exact format:

Likely root cause:
Evidence from tools:
Relevant runbook guidance:
Recommended next steps:
Rollback recommendation:
Missing information:
Confidence:
Sources and tools used:

Source citation rules:
- Cite actual filenames such as checkout_runbook.md or deployment_troubleshooting.md.
- Cite actual tool names such as log_search, service_health, or deployments.
- Do not cite vague labels like "Runbook Source 1", "Runbook Source 2", or "Source 4".
- For rollback recommendation, follow the deterministic ROLLBACK DECISION exactly.
- If ROLLBACK DECISION status is prepare_rollback, say prepare rollback only. Do not say rollback is fully recommended.
- If recommending or preparing rollback, mention the previous stable version only if it appears in the deployments tool output.
- Do not say logs show error rate. Logs show log lines. Service health shows error rate.
""".strip()

    final_answer = chat(
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    final_answer = ensure_tool_footer(
        answer=final_answer,
        selected_tools=state.get("selected_tools", []),
    )

    return {
        "final_answer": final_answer,
    }


def validate_answer_node(state: AgentState) -> AgentState:
    final_answer = state.get("final_answer", "")
    evidence_summary = state.get("evidence_summary", "")
    selected_tools = state.get("selected_tools", [])

    missing_sections = find_missing_sections(final_answer)
    answer_valid = is_valid_answer(final_answer)

    quality_issues = find_quality_issues(
        answer=final_answer,
        evidence_summary=evidence_summary,
        selected_tools=selected_tools,
    )

    answer_quality_ok = is_quality_acceptable(
        answer=final_answer,
        evidence_summary=evidence_summary,
        selected_tools=selected_tools,
    )

    return {
        "missing_sections": missing_sections,
        "answer_valid": answer_valid,
        "quality_issues": quality_issues,
        "answer_quality_ok": answer_quality_ok,
    }


def correct_answer_node(state: AgentState) -> AgentState:
    answer_valid = state.get("answer_valid", False)
    answer_quality_ok = state.get("answer_quality_ok", False)
    missing_sections = state.get("missing_sections", [])
    quality_issues = state.get("quality_issues", [])

    if answer_valid and answer_quality_ok:
        return {
            "correction_applied": False,
        }

    question = state["question"]
    original_answer = state.get("final_answer", "")
    rag_context = state.get("rag_context", "")
    evidence_summary = state.get("evidence_summary", "")

    correction_prompt = f"""
The previous answer is missing required sections or has quality issues.

Question:
{question}

Missing sections:
{missing_sections}

Quality issues:
{quality_issues}

Retrieved runbook context:
{rag_context}

Deterministic evidence summary:
{evidence_summary}

Previous answer:
{original_answer}

Rewrite the full answer using this exact format and include every heading:

Likely root cause:
Evidence from tools:
Relevant runbook guidance:
Recommended next steps:
Rollback recommendation:
Missing information:
Confidence:
Sources and tools used:

Correction rules:
- Preserve factual claims from the evidence only.
- Do not invent facts.
- For rollback, follow the ROLLBACK DECISION from the deterministic evidence summary exactly.
- If rollback status is prepare_rollback, say prepare rollback only. Do not say rollback is fully recommended.
- Do not say the error rate remained above 5% for more than 10 minutes unless the evidence summary says that.
- Cite actual filenames and tool names only.
- Sources and tools used must explicitly include every selected tool: log_search, service_health, and deployments when they were selected.
""".strip()

    corrected_answer = chat(
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": correction_prompt},
        ],
        temperature=0.1,
    )

    corrected_answer = ensure_tool_footer(
        answer=corrected_answer,
        selected_tools=state.get("selected_tools", []),
    )

    corrected_missing_sections = find_missing_sections(corrected_answer)
    corrected_answer_valid = is_valid_answer(corrected_answer)

    corrected_quality_issues = find_quality_issues(
        answer=corrected_answer,
        evidence_summary=evidence_summary,
        selected_tools=state.get("selected_tools", []),
    )

    corrected_answer_quality_ok = is_quality_acceptable(
        answer=corrected_answer,
        evidence_summary=evidence_summary,
        selected_tools=state.get("selected_tools", []),
    )

    return {
        "final_answer": corrected_answer,
        "missing_sections": corrected_missing_sections,
        "answer_valid": corrected_answer_valid,
        "quality_issues": corrected_quality_issues,
        "answer_quality_ok": corrected_answer_quality_ok,
        "correction_applied": True,
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve_context", retrieve_context_node)
    graph.add_node("plan_tools", plan_tools_node)
    graph.add_node("collect_tool_evidence", collect_tool_evidence_node)
    graph.add_node("summarize_evidence", summarize_evidence_node)
    graph.add_node("generate_answer", generate_answer_node)
    graph.add_node("validate_answer", validate_answer_node)
    graph.add_node("correct_answer", correct_answer_node)

    graph.add_edge(START, "retrieve_context")
    graph.add_edge("retrieve_context", "plan_tools")
    graph.add_edge("plan_tools", "collect_tool_evidence")
    graph.add_edge("collect_tool_evidence", "summarize_evidence")
    graph.add_edge("summarize_evidence", "generate_answer")
    graph.add_edge("generate_answer", "validate_answer")
    graph.add_edge("validate_answer", "correct_answer")
    graph.add_edge("correct_answer", END)

    return graph.compile()