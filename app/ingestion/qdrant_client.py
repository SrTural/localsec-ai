from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid
from app.core.config import settings
from app.core.logger import logger


class QdrantManager:
    VECTOR_SIZE: int = 768

    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = settings.COLLECTION_NAME
        self._ensure_collection_exists()
        logger.info(f"QdrantManager hazirdir. Collection: {self.collection_name}")

    def _ensure_collection_exists(self):
        if not self.client.collection_exists(self.collection_name):
            logger.warning("Collection not found. Creating new one...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Collection {self.collection_name} created successfully.")
        else:
            logger.info(f"Collection {self.collection_name} already exists.")

    def insert_logs(self, parsed_logs: list, embeddings: list) -> int:
        if not parsed_logs or not embeddings:
            return 0
        points = []
        for log, vector in zip(parsed_logs, embeddings):
            if not log or not vector:
                continue
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user": log.get("user", "Unknown"),
                    "ip": log.get("ip", "Unknown"),
                    "event_type": log.get("event_type", "Other"),
                    "timestamp": log.get("timestamp", ""),
                    "hostname": log.get("hostname", ""),
                    "raw_message": log.get("message", ""),
                }
            ))
        if not points:
            return 0
        self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        logger.info(f"{len(points)} logs inserted into Qdrant.")
        return len(points)

    def search_logs(self, query_vector: list, limit: int = 5) -> list:
        if not query_vector:
            return []
        try:
            result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
            ).points
            logger.info(f"Search returned {len(result)} results.")
            return [hit.payload for hit in result]
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
