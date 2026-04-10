from fastapi import APIRouter
from app.tasks.search_strategist_task import search_strategist_task
from app.models.request.search_strategist_request import SearchStrategistRequest

router = APIRouter()

@router.post(
    "/",
)
def search_strategist(request: SearchStrategistRequest):
    user_id = request.user_id
    prompt = request.prompt

    search_strategist_task.delay(prompt, user_id)

    return {"status": "queued"}