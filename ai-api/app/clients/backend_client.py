import requests
import os
from app.schemas.workspace import AIWorkspacePayload

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