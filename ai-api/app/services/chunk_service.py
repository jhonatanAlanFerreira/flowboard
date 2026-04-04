from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()

def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class ChunkService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def create_or_update_chunk(
            self, 
            chunk_id: int, 
            content: str, 
            tasklist_id: int, 
            workspace_id: int, 
            user_id: int,
            type: str):
        """
        Create a new chunk or update an existing one in Weaviate.
        Stores chunk_id, tasklist_id, workspace_id, and vector embedding.
        """
        
        content_norm = normalize_text(content)
        vector = self.model.encode(content_norm).tolist()

        chunk_id_str = str(chunk_id)
        tasklist_id_str = str(tasklist_id)
        workspace_id_str = str(workspace_id)
        user_id_str = str(user_id)

        data_object = {
            "chunk_id": chunk_id_str,
            "tasklist_id": tasklist_id_str,
            "workspace_id": workspace_id_str,
            "user_id": user_id_str,
            "content": content_norm,
            "type": type
        }

        # Check if chunk exists and request _additional.id
        existing = (
            self.client.query
            .get(self.class_name, ["chunk_id"])
            .with_where({
                "path": ["chunk_id"],
                "operator": "Equal",
                "valueText": chunk_id_str
            })
            .with_additional(["id"])
            .with_limit(1)
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        if hits:
            # Update existing chunk
            weaviate_uuid = hits[0]["_additional"]["id"]
            self.client.data_object.update(
                data_object=data_object,
                class_name=self.class_name,
                uuid=weaviate_uuid,
                vector=vector
            )
            return {"action": "update", "id": chunk_id_str}

        else:
            # Create new chunk
            self.client.data_object.create(
                data_object=data_object,
                class_name=self.class_name,
                vector=vector
            )
            return {"action": "create", "id": chunk_id_str}

    def delete_chunk(self, chunk_id: int):
        """Delete a single chunk by chunk_id"""
        chunk_id_str = str(chunk_id)

        existing = (
            self.client.query
            .get(self.class_name, ["chunk_id"])
            .with_where({
                "path": ["chunk_id"],
                "operator": "Equal",
                "valueText": chunk_id_str
            })
            .with_additional(["id"])
            .with_limit(1)
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        if hits:
            weaviate_uuid = hits[0]["_additional"]["id"]
            self.client.data_object.delete(class_name=self.class_name, uuid=weaviate_uuid)
            return True
        return False

    def delete_by_tasklist(self, tasklist_id: int):
        """Delete all chunks belonging to a tasklist"""
        tasklist_id_str = str(tasklist_id)

        existing = (
            self.client.query
            .get(self.class_name, ["chunk_id"])
            .with_where({
                "path": ["tasklist_id"],
                "operator": "Equal",
                "valueText": tasklist_id_str
            })
            .with_additional(["id"])
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        for hit in hits:
            weaviate_uuid = hit["_additional"]["id"]
            self.client.data_object.delete(class_name=self.class_name, uuid=weaviate_uuid)

        return len(hits)

    def delete_by_workspace(self, workspace_id: int):
        """Delete all chunks belonging to a workspace"""
        workspace_id_str = str(workspace_id)

        existing = (
            self.client.query
            .get(self.class_name, ["chunk_id"])
            .with_where({
                "path": ["workspace_id"],
                "operator": "Equal",
                "valueText": workspace_id_str
            })
            .with_additional(["id"])
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        for hit in hits:
            weaviate_uuid = hit["_additional"]["id"]
            self.client.data_object.delete(class_name=self.class_name, uuid=weaviate_uuid)

        return len(hits)