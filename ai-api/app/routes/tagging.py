from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.llm.tagging_service import TaggingService
from app.tasks import generate_tags_task

router = APIRouter()

tagging_service = TaggingService()

class TaggingRequest(BaseModel):
    text: str
    known_tags: List[Dict]
    chunk_id: int


class TaggingResponse(BaseModel):
    status: str


@router.post("/", response_model=TaggingResponse)
def generate_tags(request: TaggingRequest):
    text = request.text.strip()
    known_tags = request.known_tags
    chunk_id = request.chunk_id

    generate_tags_task.delay(
        chunk_id,
        text,
        known_tags
    )

    return {"status": "queued"}