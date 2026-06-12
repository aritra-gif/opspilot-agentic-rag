import argparse
import json

from rich import print

from app.llm.ollama_client import chat
from app.rag.retriever import retrieve
from app.tools.deployments import get_recent_deployments
from app.tools.log_search import search_logs
from app.tools.service_health import check_service_health


SYSTEM_PROMPT = """
You are OpsPilot, a local DevOps incident triage assistant.

You are given two kinds of information:

1. Retrieved runbooks and policy documents:
   - These are guidance documents.
   - They are not live system evidence.

2. Tool outputs:
   - These are simulated live operational evidence.
   - You may cite logs, service health, and deployment data only when they appear in the tool outputs.

Rules:
- Do not invent facts.
- Do not overstate evidence.
- Separate runbook guidance from tool evidence.
- If the evidence is incomplete, say what is missing.
- Prefer mitigation steps that reduce customer impact.
- Keep the answer practical and incident-focused.
""".strip()


def build_rag_context(chunks: list[dict]) -> str:
    context_parts = []

    for index, item in enumerate(chunks, start=1):
        source = item["metadata"].get("source", "unknown")
        chunk_index = item["metadata"].get("chunk_index", "unknown")
        text = item["text"]

        context_parts.append(
            f"""
[Runbook Source {index}]
file: {source}
chunk: {chunk_index}
content:
{text}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)


def build_tool_context() -> dict:
    """
    For this first tool-augmented version, we call the tools deterministically.

    Later, LangGraph will decide which tools to call based on the user question.
    """
    return {
        "log_search": {
            "service": "checkout-api",
            "keyword": "PAYMENT_SERVICE_URL",
            "results": search_logs("checkout-api", "PAYMENT_SERVICE_URL"),
        },
        "service_health": {
            "checkout-api": check_service_health("checkout-api"),
            "payment-service": check_service_health("payment-service"),
            "orders-db": check_service_health("orders-db"),
        },
        "deployments": {
            "checkout-api": get_recent_deployments("checkout-api"),
        },
    }


def answer_question(question: str) -> str:
    retrieved = retrieve(question)
    rag_context = build_rag_context(retrieved)
    tool_context = build_tool_context()

    print("\n[bold cyan]Retrieved chunks:[/bold cyan]")
    for item in retrieved:
        source = item["metadata"].get("source")
        similarity = item["similarity"]
        print(f"- {source} | similarity={similarity:.3f}")

    print("\n[bold cyan]Tool evidence collected:[/bold cyan]")
    print(f"- log matches: {len(tool_context['log_search']['results'])}")
    print(f"- checkout-api health: {tool_context['service_health']['checkout-api']['status']}")
    print(f"- payment-service health: {tool_context['service_health']['payment-service']['status']}")
    print(f"- deployment records: {len(tool_context['deployments']['checkout-api']['deployments'])}")

    user_prompt = f"""
Question:
{question}

Retrieved runbook context:
{rag_context}

Tool outputs:
{json.dumps(tool_context, indent=2)}

Answer with this exact format:

Likely root cause:
Evidence from tools:
Relevant runbook guidance:
Recommended next steps:
Rollback recommendation:
Missing information:
Confidence:
Sources and tools used:
""".strip()

    response = chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str)
    args = parser.parse_args()

    answer = answer_question(args.question)

    print("\n[bold green]OpsPilot Tool-Augmented Answer:[/bold green]\n")
    print(answer)


if __name__ == "__main__":
    main()