from weaviate.classes.query import Filter
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.enums.chunk_type import ChunkType

client = get_weaviate_client()


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class ChunkService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.collections.get(self.class_name)

    def create_or_update_chunk(
        self,
        chunk_id: int,
        content: str,
        tasklist_id: int,
        workspace_id: int,
        user_id: int,
        chunk_type: ChunkType,
    ):
        """
        Create a new chunk or update an existing one in Weaviate.
        Stores chunk_id, tasklist_id, workspace_id, and vector embedding.
        """

        content_norm = normalize_text(content)
        vector = self.model.encode(content_norm).tolist()

        chunk_id_str = str(chunk_id)
        data_object = {
            "chunk_id": chunk_id_str,
            "tasklist_id": str(tasklist_id),
            "workspace_id": str(workspace_id),
            "user_id": str(user_id),
            "content": content_norm,
            "type": chunk_type,
        }

        # Check if chunk exists
        response = self.collection.query.fetch_objects(
            filters=Filter.by_property("chunk_id").equal(chunk_id_str),
            limit=1,
            return_properties=[],
        )

        if response.objects:
            # Update existing using the object's uuid
            self.collection.data.update(
                uuid=response.objects[0].uuid,
                properties=data_object,
                vector=vector,
            )
            return {"action": "update", "id": chunk_id_str}
        else:
            # Create new
            self.collection.data.insert(properties=data_object, vector=vector)
            return {"action": "create", "id": chunk_id_str}

    def delete_chunk(self, chunk_id: int):
        """Delete a single chunk by chunk_id using server-side filtering"""
        result = self.collection.data.delete_many(
            where=Filter.by_property("chunk_id").equal(str(chunk_id))
        )
        return result.matches > 0

    def delete_by_tasklist(self, tasklist_id: int):
        """Delete all chunks belonging to a tasklist in one batch"""
        result = self.collection.data.delete_many(
            where=Filter.by_property("tasklist_id").equal(str(tasklist_id))
        )
        return result.matches

    def delete_by_workspace(self, workspace_id: int):
        """Delete all chunks belonging to a workspace in one batch"""
        result = self.collection.data.delete_many(
            where=Filter.by_property("workspace_id").equal(str(workspace_id))
        )
        return result.matches
