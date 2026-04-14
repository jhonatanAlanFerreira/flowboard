import requests
import os
from app.schemas.workspace import AIWorkspacePayload
from app.schemas.chunk import UpdateTagsPayload
from app.schemas.data_question import RetrievedChunk
from typing import List


class BackendClient:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL")
        self.headers = {
            "X-AI-SECRET": os.getenv("AI_API_SECRET"),
            "Accept": "application/json",
        }

    def post_workspace(self, payload: AIWorkspacePayload):
        url = f"{self.base_url}/api/internal/ai/workspaces"

        response = requests.post(url, json=payload.model_dump(), headers=self.headers)

        response.raise_for_status()
        return response

    def put_update_tags(self, payload: UpdateTagsPayload, chunk_id: int):
        url = f"{self.base_url}/api/internal/ai/chunk/{chunk_id}/tags"

        response = requests.put(url, json=payload.model_dump(), headers=self.headers)

        response.raise_for_status()
        return response

    def hydrate_data_question_retrieval(
        self, payload: List[RetrievedChunk], ai_job_id: int
    ):
        url = f"{self.base_url}/api/internal/ai/data-question-hydrate/{ai_job_id}"

        response = requests.put(
            url, json=[chunk.model_dump() for chunk in payload], headers=self.headers
        )

        response.raise_for_status()
        return response

    def complete_data_question(
        self, ai_job_id: str, markdown_answer: str, citations: List[str]
    ):
        """
        Sends the final generated answer and source citations back to Laravel.
        """
        ai_job_id_str = str(ai_job_id)
        url = f"{self.base_url}/api/internal/ai/data-question-complete/{ai_job_id_str}"

        payload = {"markdown_answer": markdown_answer, "citations": citations}

        response = requests.put(url, json=payload, headers=self.headers)

        response.raise_for_status()
        return response
