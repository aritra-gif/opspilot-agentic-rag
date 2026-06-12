import argparse

from rich import print

from app.llm.ollama_client import chat
from app.rag.retriever import retrieve


SYSTEM_PROMPT = """
You are OpsPilot, a local DevOps incident triage assistant.

You are answering using retrieved internal runbooks and policy documents.

Important distinction:
- Retrieved runbooks are guidance, not live system evidence.
- Do not claim that logs, metrics, deployments, or health checks were inspected unless the provided context contains actual log lines, metric values, deployment records, or health-check output.
- If a runbook says something "may show" or "can indicate", preserve that uncertainty.
- Use phrases like "the runbook suggests checking..." instead of "logs show..." unless real logs are provided.

Rules:
- Use only the provided retrieved context.
- Do not invent facts.
- Do not overstate evidence.
- If the context is insufficient, clearly say what is missing.
- Give practical incident triage steps.
- Mention the source files used.
- Keep the answer clear, direct, and operational.
""".strip()


def build_context(chunks: list[dict]) -> str:
    context_parts = []

    for index, item in enumerate(chunks, start=1):
        source = item["metadata"].get("source", "unknown")
        chunk_index = item["metadata"].get("chunk_index", "unknown")
        text = item["text"]

        context_parts.append(
            f"""
[Source {index}]
file: {source}
chunk: {chunk_index}
content:
{text}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)


def answer_question(question: str) -> str:
    retrieved = retrieve(question)

    print("\n[bold cyan]Retrieved chunks:[/bold cyan]")
    for item in retrieved:
        source = item["metadata"].get("source")
        similarity = item["similarity"]
        print(f"- {source} | similarity={similarity:.3f}")

    context = build_context(retrieved)

    user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Answer with this exact format:

Likely diagnosis:
Evidence from retrieved documents:
Recommended next steps:
Missing information:
Confidence:
Sources:
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

    print("\n[bold green]OpsPilot Answer:[/bold green]\n")
    print(answer)


if __name__ == "__main__":
    main()