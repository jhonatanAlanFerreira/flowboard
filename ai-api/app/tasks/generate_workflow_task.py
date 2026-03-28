from app.services.generate_workflow_service import GenerateWorkflowService
from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.schemas.workspace import AIWorkspacePayload
import json

service = GenerateWorkflowService()
backend_client = BackendClient()

@celery.task
def generate_workflow_task(user_prompt: str, job_id: str):
    workspace_data = service.generate_workspace_llm(user_prompt)

    if isinstance(workspace_data, str):
        workspace_data = json.loads(workspace_data)

    payload = AIWorkspacePayload(
        job_id=job_id,
        workflow=workspace_data["workflow"]
    )

    backend_client.post_workspace(payload)