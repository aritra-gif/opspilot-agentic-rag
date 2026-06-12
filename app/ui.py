import json
from typing import Any

import gradio as gr
import requests


API_URL = "http://127.0.0.1:8000/triage"


def triage_incident(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter an incident question.", "{}"

    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=300,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()

    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to the FastAPI backend. "
            "Make sure uvicorn is running on http://127.0.0.1:8000.",
            "{}",
        )
    except requests.exceptions.Timeout:
        return "The request timed out. The local model may still be generating.", "{}"
    except requests.exceptions.HTTPError as exc:
        return f"API error: {exc}\n\n{response.text}", "{}"

    answer = data.get("answer", "No answer returned.")

    trace = {
        "tool_plan": data.get("tool_plan", {}),
        "selected_tools": data.get("selected_tools", []),
        "answer_valid": data.get("answer_valid"),
        "answer_quality_ok": data.get("answer_quality_ok"),
        "missing_sections": data.get("missing_sections", []),
        "quality_issues": data.get("quality_issues", []),
        "correction_applied": data.get("correction_applied"),
    }

    return answer, json.dumps(trace, indent=2)


demo = gr.Interface(
    fn=triage_incident,
    inputs=gr.Textbox(
        label="Incident question",
        placeholder="Example: Checkout API is returning 500 errors right after deployment. What should I check first?",
        lines=4,
    ),
    outputs=[
        gr.Markdown(label="OpsPilot answer"),
        gr.Code(label="Agent trace", language="json"),
    ],
    title="OpsPilot: Local Agentic RAG Incident Triage Assistant",
    description=(
        "Ask a DevOps/SRE incident question. OpsPilot retrieves runbooks, "
        "calls tools, summarizes evidence, applies rollback guardrails, "
        "and validates the final answer."
    ),
)


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)