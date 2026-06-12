from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.

    Each node reads from and writes to this state.
    """

    question: str

    retrieved_chunks: list[dict[str, Any]]
    rag_context: str

    tool_plan: dict[str, Any]
    selected_tools: list[str]
    tool_outputs: dict[str, Any]

    evidence_summary: str

    final_answer: str

    missing_sections: list[str]
    answer_valid: bool

    quality_issues: list[str]
    answer_quality_ok: bool

    correction_applied: bool