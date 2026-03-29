from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()

class ChunkService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def create_or_update_chunk(self, chunk_id: int, content: str):
        vector = self.model.encode(content).tolist()
        chunk_id_str = str(chunk_id)

        # Check if chunk exists
        existing = (
            self.client.query
            .get(self.class_name, ["chunk_id"])
            .with_where({"path": ["chunk_id"], "operator": "Equal", "valueText": chunk_id_str})
            .with_limit(1)
            .do()
        )
        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        if hits:
            # Update existing chunk
            weaviate_uuid = hits[0]["_additional"]["id"]
            self.client.data_object.update(
                data_object={"chunk_id": chunk_id_str},
                class_name=self.class_name,
                uuid=weaviate_uuid,
                vector=vector
            )
            return {"action": "update", "id": chunk_id_str}

        else:
            # Create new chunk
            self.client.data_object.create(
                data_object={"chunk_id": chunk_id_str},
                class_name=self.class_name,
                vector=vector
            )
            return {"action": "create", "id": chunk_id_str}