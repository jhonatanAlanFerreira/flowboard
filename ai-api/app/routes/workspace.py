from fastapi import APIRouter
from app.models.request.workspace_request import WorkspaceRequest
from app.models.response.workspace_response import WorkflowResponse
from app.tasks.generate_workflow_task import generate_workflow_task

router = APIRouter()

@router.post("/generate-workspace", response_model=WorkflowResponse)
def generate_workspace(request: WorkspaceRequest):
    prompt = request.prompt.strip()

    generate_workflow_task.delay(prompt)

    return {"status": "queued"}