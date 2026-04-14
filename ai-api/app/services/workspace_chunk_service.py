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
        user_id_str = str(user_id)
        chunk_id_str = str(chunk_id)

        data_object = {
            "workspace_id": workspace_id_str,
            "user_id": user_id_str,
            "name": name_norm,
            "chunk_id": chunk_id_str,
        }

        # Check if this workspace already exists
        existing = (
            self.client.query.get(self.class_name, ["workspace_id"])
            .with_where(
                {
                    "path": ["workspace_id"],
                    "operator": "Equal",
                    "valueText": workspace_id_str,
                }
            )
            .with_additional(["id"])
            .with_limit(1)
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        if hits:
            # Update existing workspace name/vector
            weaviate_uuid = hits[0]["_additional"]["id"]
            self.client.data_object.update(
                data_object=data_object,
                class_name=self.class_name,
                uuid=weaviate_uuid,
                vector=vector,
            )
            return {"action": "update", "id": workspace_id_str}
        else:
            # Create new workspace entry
            self.client.data_object.create(
                data_object=data_object, class_name=self.class_name, vector=vector
            )
            return {"action": "create", "id": workspace_id_str}

    def delete_workspace(self, workspace_id: int):
        """Delete workspace from Stage 1 index"""
        workspace_id_str = str(workspace_id)

        existing = (
            self.client.query.get(self.class_name, ["workspace_id"])
            .with_where(
                {
                    "path": ["workspace_id"],
                    "operator": "Equal",
                    "valueText": workspace_id_str,
                }
            )
            .with_additional(["id"])
            .with_limit(1)
            .do()
        )

        hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])

        if hits:
            weaviate_uuid = hits[0]["_additional"]["id"]
            self.client.data_object.delete(
                class_name=self.class_name, uuid=weaviate_uuid
            )
            return True
        return False

    def get_workspace_candidates(self, user_id: int, user_prompt: str, limit: int = 10):
        """
        Performs a hybrid search on Workspace names to find the top candidates.
        Restricts results to the specific user executing the query.
        """
        user_id_str = str(user_id)
        prompt_norm = normalize_text(user_prompt)

        vector = self.model.encode(prompt_norm).tolist()

        query = (
            self.client.query.get(self.class_name, ["workspace_id", "name"])
            .with_hybrid(query=prompt_norm, vector=vector, alpha=0.5)
            .with_where(
                {"path": ["user_id"], "operator": "Equal", "valueText": user_id_str}
            )
            .with_limit(limit)
            .with_additional(["score"])
            .do()
        )

        hits = query.get("data", {}).get("Get", {}).get(self.class_name, [])

        candidates = []
        for hit in hits:
            candidates.append(
                {
                    "workspace_id": hit.get("workspace_id"),
                    "name": hit.get("name"),
                    "search_score": hit.get("_additional", {}).get("score"),
                }
            )

        return candidates
