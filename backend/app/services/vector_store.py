"""Qdrant vector store service for pattern embeddings."""

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

COLLECTION_NAME = "patterns"
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small


class VectorStoreService:
    """Service for managing pattern embeddings in Qdrant."""

    def __init__(self, host: str, port: int):
        """Initialize Qdrant client.

        Args:
            host: Qdrant server host.
            port: Qdrant server port.
        """
        self.client = QdrantClient(host=host, port=port)
        self._collection_name = COLLECTION_NAME

    def ensure_collection(self) -> bool:
        """Create collection if it doesn't exist.

        Returns:
            True if collection exists or was created successfully.
        """
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self._collection_name for c in collections):
                self.client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
            return True
        except Exception:
            return False

    def health_check(self) -> bool:
        """Check if Qdrant is accessible.

        Returns:
            True if Qdrant is healthy.
        """
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def upsert_pattern(
        self,
        pattern_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        """Store or update pattern embedding with metadata.

        Args:
            pattern_id: Unique identifier for the pattern.
            vector: Embedding vector (1536 dimensions).
            payload: Metadata for filtering (paper_id, paper_type, etc.).
        """
        self.client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=pattern_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def delete_pattern(self, pattern_id: str) -> None:
        """Delete a pattern from the vector store.

        Args:
            pattern_id: Unique identifier for the pattern to delete.
        """
        self.client.delete(
            collection_name=self._collection_name,
            points_selector=[pattern_id],
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter_conditions: dict | None = None,
    ) -> list[dict]:
        """Search for similar patterns.

        Args:
            query_vector: Query embedding vector.
            limit: Maximum number of results.
            filter_conditions: Optional Qdrant filter conditions.

        Returns:
            List of matching patterns with scores.
        """
        response = self.client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=limit,
            query_filter=filter_conditions,
        )
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in response.points
        ]

    def get_collection_info(self) -> dict | None:
        """Get collection statistics.

        Returns:
            Collection info dict or None if not accessible.
        """
        try:
            info = self.client.get_collection(self._collection_name)
            return {
                "name": self._collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
            }
        except UnexpectedResponse:
            return None
