from fastapi import APIRouter
from app.models.request.workspace_request import WorkspaceRequest
from app.models.response.workspace_response import WorkflowResponse
from app.tasks.generate_workflow_task import generate_workflow_task

router = APIRouter()

@router.post(
    "/generate-workspace",
    response_model=WorkflowResponse,
    summary="Generate a workspace using AI",
    status_code=202
)
def generate_workspace(request: WorkspaceRequest):
    """
    Queues an AI job to generate a full workspace structure
    (task lists and tasks) based on the provided prompt.

    This endpoint does not generate the workspace immediately.
    It schedules a background job and returns a queued status.
    """
    prompt = request.prompt.strip()
    job_id = request.job_id

    generate_workflow_task.delay(prompt, job_id)

    return {"status": "queued"}