from fastapi import APIRouter
from app.tasks.chunk_tasks import generate_tags_task
from app.models.request.tagging_request import TaggingRequest
from app.models.response.tagging_response import TaggingResponse

router = APIRouter()

@router.post("/", response_model=TaggingResponse)
def generate_tags(request: TaggingRequest):
    text = request.text.strip()
    content = request.content.strip()
    chunk_id = request.chunk_id
    tasklist_id = request.tasklist_id
    workspace_id = request.workspace_id

    # Queue Celery task
    generate_tags_task.delay(
        chunk_id,
        text,
        content,
        tasklist_id,
        workspace_id
    )

    return {"status": "queued"}