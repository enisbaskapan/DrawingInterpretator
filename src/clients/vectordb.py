from qdrant_client import QdrantClient


class VectorClientProvider:
    def __init__(self, *, url: str):
        self._client = QdrantClient(url=url)

    @property
    def client(self) -> QdrantClient:
        return self._client
