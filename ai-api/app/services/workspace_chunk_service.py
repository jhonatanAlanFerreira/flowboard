from typing import List
from weaviate.classes.query import Filter, MetadataQuery
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class WorkspaceService:
    def __init__(self):
        self.client = client
        self.class_name = "Workspace"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.collections.get(self.class_name)

    def upsert_workspace(
        self, chunk_id: int, user_id: int, workspace_id: int, name: str
    ):
        """
        Creates or updates a Workspace name vector.
        This is used for Stage 1: finding the workspace_id from an LLM hint.
        """
        name_norm = normalize_text(name)
        vector = self.model.encode(name_norm).tolist()

        workspace_id_str = str(workspace_id)
        data_object = {
            "workspace_id": workspace_id_str,
            "user_id": str(user_id),
            "name": name_norm,
            "chunk_id": str(chunk_id),
        }

        # Check if this workspace already exists
        response = self.collection.query.fetch_objects(
            filters=Filter.by_property("workspace_id").equal(workspace_id_str),
            limit=1,
            return_properties=[],
        )

        if response.objects:
            # Update existing workspace name/vector
            weaviate_uuid = response.objects[0].uuid
            self.collection.data.update(
                uuid=weaviate_uuid, properties=data_object, vector=vector
            )
            return {"action": "update", "id": workspace_id_str}
        else:
            # Create new
            self.collection.data.insert(properties=data_object, vector=vector)
            return {"action": "create", "id": workspace_id_str}

    def delete_workspace(self, workspace_id: int):
        """Delete workspace from Stage 1 index"""
        workspace_id_str = str(workspace_id)

        result = self.collection.data.delete_many(
            where=Filter.by_property("workspace_id").equal(workspace_id_str)
        )
        return result.matches > 0

    def get_workspace_candidates(self, user_id: int, user_prompt: str, limit: int = 10):
        """
        Performs a hybrid search on Workspace names to find the top candidates.
        Restricts results to the specific user executing the query.
        """
        user_id_str = str(user_id)
        prompt_norm = normalize_text(user_prompt)
        vector = self.model.encode(prompt_norm).tolist()

        response = self.collection.query.hybrid(
            query=prompt_norm,
            vector=vector,
            alpha=0.5,
            filters=Filter.by_property("user_id").equal(user_id_str),
            limit=limit,
            return_metadata=MetadataQuery(score=True),
            return_properties=["workspace_id", "name"],
        )

        return [
            {
                "workspace_id": obj.properties.get("workspace_id"),
                "name": obj.properties.get("name"),
                "search_score": obj.metadata.score,
            }
            for obj in response.objects
        ]
