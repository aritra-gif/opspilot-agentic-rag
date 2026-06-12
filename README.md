# OpsPilot: Local Agentic RAG Incident Triage Assistant

OpsPilot is a local, open-source Agentic RAG assistant for DevOps/SRE incident triage.

The goal of this project is not just to build a basic "chat with docs" app. OpsPilot is designed around realistic production AI failure modes such as hallucination, weak retrieval, incorrect tool usage, rollback overclaiming, missing evidence, and inconsistent response formatting.

The system runs fully locally using Ollama, ChromaDB, LangGraph, FastAPI, and Gradio.

---

## Use Case

During incidents, engineers often need to quickly answer questions like:

- What changed recently?
- Which service is unhealthy?
- Are logs showing a known failure pattern?
- Is the dependency healthy?
- Should we rollback or keep investigating?
- Which runbook guidance applies?

OpsPilot simulates this workflow by combining:

- Internal runbook retrieval
- Mock log search
- Mock service health checks
- Mock deployment history
- Deterministic rollback guardrails
- LLM-based incident response generation
- Format and quality validation

---

## Tech Stack

- Python
- uv
- Ollama
- qwen2.5:3b
- nomic-embed-text
- ChromaDB
- LangGraph
- FastAPI
- Gradio
- Pydantic
- Rich

---

## Architecture

```text
User question
   ↓
LangGraph Agent
   ↓
Tool Planner
   ↓
RAG Retriever → ChromaDB → Runbook chunks
   ↓
Tools:
   - log_search
   - service_health
   - deployments
   ↓
Deterministic Evidence Summary
   ↓
Rollback Decision Guardrail
   ↓
Local LLM Answer Generation
   ↓
Format Validation
   ↓
Quality Validation
   ↓
Correction Node if needed
   ↓
Final Answer


## Deployment Note

OpsPilot is designed as a fully local/open-source AI system.

The main demo runs locally because it uses Ollama for local LLM inference. This avoids paid LLM APIs and keeps the project independent from proprietary model providers.

For sharing the project publicly:

- GitHub hosts the complete source code.
- The full AI workflow can be run locally with Ollama.
- A hosted demo can be added later using a lightweight Gradio/FastAPI deployment, but free hosting platforms may not reliably support local LLM inference workloads.
- If deployed to a free platform, the practical option is usually a lightweight demo mode or a Hugging Face Space, depending on available compute.