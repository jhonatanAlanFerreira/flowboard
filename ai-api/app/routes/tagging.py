from fastapi import APIRouter
from app.tasks.chunk_tasks import generate_tags_task
from app.models.request.tagging_request import TaggingRequest
from app.models.response.tagging_response import TaggingResponse

router = APIRouter()


@router.post(
    "/", response_model=TaggingResponse, summary="Queue tag generation for a chunk"
)
def generate_tags(request: TaggingRequest):
    """
    Receives text and metadata, then queues a background task
    to generate semantic tags using AI.
    """
    text = request.text.strip()
    content = request.content.strip()
    chunk_id = request.chunk_id
    tasklist_id = request.tasklist_id
    workspace_id = request.workspace_id
    user_id = request.user_id

    generate_tags_task.delay(
        chunk_id, text, content, tasklist_id, workspace_id, user_id
    )

    return {"status": "queued"}
