from fastapi import APIRouter
from app.tasks.search_strategist_task import search_strategist_task
from app.models.request.search_strategist_request import SearchStrategistRequest
from app.models.request.search_strategist_request import ProcessAnswerRequest
from app.tasks.rank_and_generate_task import rank_and_generate_task
from app.models.request.search_strategist_request import HydratedChunk
from typing import List

router = APIRouter()


@router.post(
    "/",
)
def search_strategist(request: SearchStrategistRequest):
    user_id = request.user_id
    prompt = request.prompt
    ai_job_id = request.ai_job_id

    search_strategist_task.delay(prompt, user_id, ai_job_id)

    return {"status": "queued"}


@router.post(
    "/process-answer", summary="Receive hydrated tasks and generate final answer"
)
def process_answer(request: ProcessAnswerRequest):
    """
    Receives the fully hydrated tasks from Laravel and queues
    the Celery task for re-ranking and answering the user's question.
    """
    ai_job_id = request.ai_job_id
    prompt = request.prompt
    chunks_data = [chunk.model_dump(mode="json") for chunk in request.chunks]

    rank_and_generate_task.delay(prompt, ai_job_id, chunks_data)

    return {"status": "queued", "ai_job_id": ai_job_id}
