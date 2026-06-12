# OpsPilot Project Explanation

## Short Explanation

OpsPilot is a fully local Agentic RAG assistant for DevOps incident triage. It uses Ollama for local LLM inference, ChromaDB for runbook retrieval, LangGraph for agent workflow orchestration, and FastAPI/Gradio for API and UI access.

The assistant can retrieve internal runbooks, inspect mock operational evidence such as logs, service health, and deployment history, then generate a grounded incident triage response with rollback guardrails and validation checks.

## Interview Explanation

I built OpsPilot as a production-style Agentic RAG project instead of a basic chatbot.

The system starts with a user incident question, retrieves relevant runbook chunks from ChromaDB, plans which tools are needed, calls tools like log search, service health, and deployment history, summarizes the evidence, applies deterministic rollback decision logic, and then generates a final answer using a local Ollama model.

A major focus of the project was handling real-world GenAI failure modes. For example, I added guardrails to prevent the model from treating runbook guidance as live evidence, overclaiming rollback recommendations, skipping required answer sections, or failing to mention tools used. I also added an evaluation suite to test multiple incident scenarios and verify tool planning, answer format, and answer quality.

## Technical Highlights

* Built a local RAG pipeline using Ollama embeddings and ChromaDB.
* Used LangGraph to structure the agent workflow into retrieval, tool planning, evidence collection, summarization, answer generation, validation, and correction nodes.
* Added mock production tools for log search, service health checks, and deployment history.
* Implemented deterministic rollback guardrails to prevent unsafe LLM recommendations.
* Added response validation for missing sections, factual contradictions, and tool traceability.
* Exposed the agent through FastAPI and a Gradio UI.
* Created an evaluation suite with multiple incident scenarios and a JSON evaluation report.

## One-Minute Pitch

OpsPilot is a local Agentic RAG incident triage assistant for DevOps and SRE use cases. It does more than retrieve documents. It combines runbook retrieval with operational tool outputs like logs, service health, and deployment history.

The project uses LangGraph to create a structured agent workflow and includes production-style guardrails such as evidence separation, rollback decision logic, answer validation, correction flow, and evaluation cases.

I built it this way because real AI systems fail not only because retrieval is poor, but because models can overstate evidence, skip required structure, or make unsafe recommendations. OpsPilot demonstrates how to make an Agentic RAG system more reliable and auditable.

## Resume Bullet Options

* Built OpsPilot, a fully local Agentic RAG assistant for DevOps incident triage using Ollama, ChromaDB, LangGraph, FastAPI, and Gradio.
* Implemented RAG-based runbook retrieval with mock operational tools for log search, service health checks, and deployment history inspection.
* Designed a LangGraph workflow with tool planning, evidence summarization, rollback guardrails, response validation, and correction nodes.
* Added deterministic rollback decision logic to prevent unsafe LLM-generated rollback recommendations.
* Created an evaluation suite to validate service detection, tool selection, response format, and answer quality across incident scenarios.

## LinkedIn Project Summary

I built OpsPilot, a local Agentic RAG assistant for DevOps incident triage.

The project uses Ollama for local LLM inference, ChromaDB for runbook retrieval, LangGraph for agent orchestration, and FastAPI/Gradio for API and UI access.

What makes it different from a basic RAG chatbot is the production-style workflow. OpsPilot retrieves runbooks, calls mock operational tools, summarizes evidence, applies rollback guardrails, validates the final answer, and runs evaluation cases to catch failures.

The focus was not just on getting an answer, but making the answer grounded, traceable, and safer for incident-response use cases.
