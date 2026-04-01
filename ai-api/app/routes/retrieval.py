from fastapi import APIRouter
from app.models.request.retrieval_request import RetrievalRequest
from app.models.response.retrieval_response import RetrievalResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()
service = RetrievalService()


@router.post(
    "/",
    response_model=RetrievalResponse,
    summary="Retrieve relevant workspaces using semantic + keyword search"
)
def retrieve_workspaces(request: RetrievalRequest):
    """
    Performs hybrid search (semantic + keyword) filtered by user_id
    and returns top relevant workspaces.
    """

    query = request.query.strip()
    user_id = request.user_id

    results = service.search(query=query, user_id=user_id)

    return {
        "results": results
    }