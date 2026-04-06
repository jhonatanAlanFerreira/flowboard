from fastapi import APIRouter
from app.models.request.collection_workspace_request import CollectionWorkspaceRequest
from app.tasks.generate_collection_workspace_task import generate_collection_workspace_task

router = APIRouter()

@router.post(
    "/generate-workspace/collection",
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

    workspace_patterns = {
    "lists": [lst.model_dump() for lst in request.lists],
    "average_tasks_per_list": request.average_tasks_per_list,
    "average_lists_per_workspace": request.average_lists_per_workspace
    }

    generate_collection_workspace_task.delay(prompt, job_id, workspace_patterns)

    return {"status": "queued"}