from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.graph import build_graph
from app.config import APP_NAME


class TriageRequest(BaseModel):
    question: str


class TriageResponse(BaseModel):
    answer: str
    tool_plan: dict[str, Any]
    selected_tools: list[str]
    answer_valid: bool
    answer_quality_ok: bool
    missing_sections: list[str]
    quality_issues: list[str]
    correction_applied: bool


app = FastAPI(
    title=APP_NAME,
    description="Local Agentic RAG assistant for DevOps incident triage",
    version="0.1.0",
)

graph = build_graph()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": APP_NAME,
    }


@app.post("/triage", response_model=TriageResponse)
def triage_incident(request: TriageRequest) -> TriageResponse:
    result = graph.invoke(
        {
            "question": request.question,
        }
    )

    return TriageResponse(
        answer=result.get("final_answer", ""),
        tool_plan=result.get("tool_plan", {}),
        selected_tools=result.get("selected_tools", []),
        answer_valid=result.get("answer_valid", False),
        answer_quality_ok=result.get("answer_quality_ok", False),
        missing_sections=result.get("missing_sections", []),
        quality_issues=result.get("quality_issues", []),
        correction_applied=result.get("correction_applied", False),
    )