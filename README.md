# OpsPilot: Local Agentic RAG Incident Triage Assistant

OpsPilot is a local, open-source Agentic RAG assistant for DevOps/SRE incident triage.

The goal of this project is not just to build a basic "chat with docs" app. OpsPilot is designed around realistic production AI failure modes such as hallucination, weak retrieval, incorrect tool usage, rollback overclaiming, missing evidence, and inconsistent response formatting.

The system runs fully locally using Ollama, ChromaDB, LangGraph, FastAPI, and Gradio.

---

## Use Case

During incidents, engineers often need to quickly answer questions like:

* What changed recently?
* Which service is unhealthy?
* Are logs showing a known failure pattern?
* Is the dependency healthy?
* Should we rollback or keep investigating?
* Which runbook guidance applies?

OpsPilot simulates this workflow by combining:

* Internal runbook retrieval
* Mock log search
* Mock service health checks
* Mock deployment history
* Deterministic rollback guardrails
* LLM-based incident response generation
* Format and quality validation

---

## Tech Stack

* Python
* uv
* Ollama
* qwen2.5:3b
* nomic-embed-text
* ChromaDB
* LangGraph
* FastAPI
* Gradio
* Pydantic
* Rich

---

## Architecture

```text
User question
   ↓
LangGraph Agent
   ↓
Tool Planner
   ↓
RAG Retriever -> ChromaDB -> Runbook chunks
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
```

---

## Key Features

### Local LLM

OpsPilot uses Ollama for local inference. No paid LLM APIs are required.

### RAG Pipeline

Markdown runbooks are chunked, embedded using `nomic-embed-text`, and stored in ChromaDB.

### Tool Calling

The agent can call mock production tools:

* `log_search`
* `service_health`
* `deployments`

### Evidence Separation

The system separates:

* Runbook guidance
* Log evidence
* Service health evidence
* Deployment evidence
* Rollback decision logic

This reduces hallucination and prevents the model from claiming evidence it has not actually seen.

### Rollback Guardrail

Rollback decisions are handled by deterministic Python logic instead of relying only on the LLM.

Example:

```text
Error rate is 8.7%, but only 6 minutes have passed since deployment.
Status: prepare_rollback
```

### Validation

The agent validates:

* Required answer sections
* Evidence contradictions
* Rollback overclaiming
* Missing tool traceability

If the answer fails validation, the graph can correct it.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aritra-gif/opspilot-agentic-rag.git
cd opspilot-agentic-rag
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Pull Ollama models

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

### 4. Create `.env`

Copy `.env.example` to `.env`.

For Windows CMD:

```cmd
copy .env.example .env
```

For macOS/Linux:

```bash
cp .env.example .env
```

---

## Ingest Documents

```bash
uv run python -m scripts.ingest
```

---

## Run Agent from CMD

```bash
uv run python -m scripts.run_agent "Checkout API is returning 500 errors right after deployment. What should I check first?"
```

---

## Run FastAPI Backend

```bash
uv run uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Run Gradio UI

In a second terminal:

```bash
uv run python -m app.ui
```

Open:

```text
http://127.0.0.1:7860
```

---

## Demo Commands

Run the agent from the terminal:

```bash
uv run python -m scripts.run_agent "Checkout API is returning 500 errors right after deployment. What should I check first?"
```

Run the API backend:

```bash
uv run uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

Test the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Test the triage endpoint on macOS/Linux/Git Bash:

```bash
curl -X POST "http://127.0.0.1:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{"question":"Checkout API is returning 500 errors right after deployment. What should I check first?"}'
```

Test the triage endpoint on Windows CMD:

```cmd
curl -X POST "http://127.0.0.1:8000/triage" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Checkout API is returning 500 errors right after deployment. What should I check first?\"}"
```

Run the Gradio UI:

```bash
uv run python -m app.ui
```

---

## Run Evaluations

```bash
uv run python -m scripts.evaluate_agent
```

Current evaluation result:

```text
passed: 4/4
failed: 0/4
pass rate: 1.0
```

Evaluation report is saved to:

```text
data/eval/eval_results.json
```

---

## Example Query

```text
Checkout API is returning 500 errors right after deployment. What should I check first?
```

Expected agent behavior:

* Retrieve relevant runbooks
* Identify `checkout-api`
* Search logs for `PAYMENT_SERVICE_URL`
* Check service health
* Inspect deployment history
* Prepare rollback if needed
* Validate final response

---

## Example API Response Fields

The `/triage` endpoint returns:

```json
{
  "answer": "Final incident triage answer",
  "tool_plan": {
    "service": "checkout-api",
    "log_keyword": "PAYMENT_SERVICE_URL",
    "tools": ["log_search", "service_health", "deployments"]
  },
  "selected_tools": ["log_search", "service_health", "deployments"],
  "answer_valid": true,
  "answer_quality_ok": true,
  "missing_sections": [],
  "quality_issues": [],
  "correction_applied": false
}
```

---

## Production Failure Modes Addressed

* Hallucinated evidence
* Runbook guidance mistaken as live evidence
* Rollback overclaiming
* Missing required response sections
* Weak source traceability
* Tool output not reflected in answer
* Inconsistent answer format
* Evaluation gaps

---

## Deployment Note

OpsPilot is designed as a fully local/open-source AI system.

The main demo runs locally because it uses Ollama for local LLM inference. This avoids paid LLM APIs and keeps the project independent from proprietary model providers.

For sharing the project publicly:

* GitHub hosts the complete source code.
* The full AI workflow can be run locally with Ollama.
* A hosted demo can be added later using a lightweight Gradio/FastAPI deployment, but free hosting platforms may not reliably support local LLM inference workloads.
* If deployed to a free platform, the practical option is usually a lightweight demo mode or a Hugging Face Space, depending on available compute.

---

## Project Status

This project currently includes:

* Local RAG pipeline
* LangGraph agent workflow
* Mock production tools
* FastAPI backend
* Gradio UI
* Evaluation suite
* Validation and correction guardrails
