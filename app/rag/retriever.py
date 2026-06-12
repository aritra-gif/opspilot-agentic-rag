from app.config import TOP_K
from app.llm.ollama_client import embed_texts
from app.rag.vector_store import get_collection


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    collection = get_collection(reset=False)

    query_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []

    for doc, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            {
                "text": doc,
                "metadata": metadata,
                "distance": distance,
                "similarity": 1 - distance,
            }
        )

    return retrieved