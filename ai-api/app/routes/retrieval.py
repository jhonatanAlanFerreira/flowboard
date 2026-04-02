from fastapi import APIRouter
from app.models.request.retrieval_request import RetrievalRequest
from app.models.response.retrieval_response import RetrievalResponse
from app.services.retrieval_service import RetrievalService
from app.services.pattern_extraction_service import PatternExtractionService
from typing import List, Dict

router = APIRouter()
retrieval_service = RetrievalService()
pattern_extraction_service = PatternExtractionService()


@router.post(
    "/lists",
    summary="Retrieve relevant workspaces using semantic + keyword search",
    response_model=RetrievalResponse
)
def retrieve_workspaces(request: RetrievalRequest):
    """
    Performs hybrid search (semantic + keyword) filtered by user_id
    and returns top relevant workspaces.
    """

    query = request.query.strip()
    user_id = request.user_id

    workspace = retrieval_service.get_relevant_workspaces(query=query, user_id=user_id)
    
    lists = retrieval_service.get_relevant_lists_for_workspaces(workspace_ids=[ws['workspace_id'] for ws in workspace], query=query)

    return {"lists": lists}


@router.post("/patterns/extract")
def extract_patterns(lists: List[Dict]):
    results = pattern_extraction_service.extract_patterns_from_lists(
        lists_data=lists
    )

    return {
        "results": results
    }