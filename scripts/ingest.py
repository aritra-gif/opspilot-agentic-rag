import hashlib
from pathlib import Path

from rich import print

from app.config import DOCS_DIR
from app.llm.ollama_client import embed_texts
from app.rag.chunker import chunk_text
from app.rag.vector_store import get_collection


def stable_id(source: str, chunk_index: int, text: str) -> str:
    raw = f"{source}:{chunk_index}:{text}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def ingest_docs() -> None:
    collection = get_collection(reset=True)

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    md_files = list(Path(DOCS_DIR).rglob("*.md"))

    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {DOCS_DIR}")

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append(
                {
                    "source": str(path.relative_to(DOCS_DIR)),
                    "chunk_index": index,
                }
            )
            ids.append(stable_id(str(path), index, chunk))

    print(f"[bold cyan]Embedding {len(documents)} chunks...[/bold cyan]")

    embeddings = embed_texts(documents)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"[bold green]Ingested {len(documents)} chunks into Chroma.[/bold green]")


if __name__ == "__main__":
    ingest_docs()