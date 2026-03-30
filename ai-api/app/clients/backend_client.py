import requests
import os
from app.schemas.workspace import AIWorkspacePayload
from app.schemas.chunk import UpdateTagsPayload

class BackendClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL")
        self.headers = {"X-AI-SECRET": os.getenv("AI_API_SECRET")}

    def post_workspace(self, payload: AIWorkspacePayload):
        url = f"{self.base_url}/api/internal/ai/workspaces"

        response = requests.post(
            url,
            json=payload.model_dump(),
            headers=self.headers
        )

        response.raise_for_status()
        return response
    
    def put_update_tags(self, payload: UpdateTagsPayload, chunk_id: int):
        url = f"{self.base_url}/api/internal/ai/chunk/{chunk_id}/tags"

        response = requests.put(
            url,
            json=payload.model_dump(),
            headers=self.headers
        )

        response.raise_for_status()
        return response