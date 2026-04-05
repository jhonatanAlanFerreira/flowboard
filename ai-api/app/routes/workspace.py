from fastapi import APIRouter
from app.models.request.collection_workspace_request import CollectionWorkspaceRequest
from app.tasks.generate_collection_workspace_task import generate_collection_workspace_task

router = APIRouter()

@router.post(
    "/generate-workspace/collection",
    # response_model=WorkflowResponse,
    summary="Generate a workspace using AI",
    status_code=202
)
def generate_collection_workspace(request: CollectionWorkspaceRequest):
    """
    Queues an AI job to generate a full workspace structure
    (task lists and tasks) based on the provided prompt.

    This endpoint does not generate the workspace immediately.
    It schedules a background job and returns a queued status.
    """
    prompt = request.prompt.strip()
    job_id = request.job_id

    generate_collection_workspace_task.delay(prompt, job_id)

    return {"status": "queued"}