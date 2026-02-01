from typing import Callable
import ollama
from agents import function_tool


def make_similarity_search_tool(*, qdrant_client, collection_name: str) -> Callable:
    @function_tool
    def similarity_search(query: str) -> str:
        results = qdrant_client.query_points(
            collection_name=collection_name,
            query=ollama.embed(
                model="qwen3-embedding:0.6b",
                input=query,
            ).embeddings[0],
            limit=3,
            with_payload=True,
        )

        return str(results)

    return similarity_search
