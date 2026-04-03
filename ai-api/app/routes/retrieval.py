from fastapi import APIRouter
from app.models.request.retrieval_collection_request import RetrievalCollectionRequest
from app.models.response.retrieval_collection_response import RetrievalCollectionResponse
from app.models.request.retrieval_workflow_request import RetrievalWorkflowRequest
from app.models.response.retrieval_workflow_response import RetrievalWorkflowResponse
from typing import List
from app.models.request.patterns_extract_request import TaskListInput 
from app.models.response.patterns_extract_reponse import ExtractPatternsResponse
from app.services.collection.retrieval_collection_service import RetrievalCollectionService
from app.services.workflow.retrieval_workflow_service import RetrievalWorkflowService
from app.services.collection.pattern_extraction_collection_service import PatternExtractionCollectionService

router = APIRouter()
retrieval_collection_service = RetrievalCollectionService()
retrieval_workflow_service = RetrievalWorkflowService()
pattern_extraction_collection_service = PatternExtractionCollectionService()


@router.post(
    "/collection/workspaces-lists",
    summary="Retrieve relevant workspaces using semantic + keyword search for collections workspaces",
    response_model=RetrievalCollectionResponse
)
def retrieve_workspaces(request: RetrievalCollectionRequest):
    """
    Performs hybrid search (semantic + keyword) filtered by user_id
    and returns top relevant workspaces from a collection workspace type.
    """

    query = request.query.strip()
    user_id = request.user_id

    workspaces = retrieval_collection_service.get_relevant_workspaces(query, user_id)
    lists = retrieval_collection_service.get_relevant_lists_for_workspaces(workspace_ids=[ws['workspace_id'] for ws in workspaces], query=query)
    return {"lists": lists}

@router.post(
    "/workflow/workspaces-lists",
    summary="Retrieve relevant workspaces using semantic + keyword search for workflow workspaces",
    response_model=RetrievalWorkflowResponse
)
def retrieve_workspaces(request: RetrievalWorkflowRequest):
    """
    Performs hybrid search (semantic + keyword) filtered by user_id
    and returns top relevant workspaces from a workflow workspace type.
    """

    query = request.query.strip()
    user_id = request.user_id

    workspaces = retrieval_workflow_service.get_relevant_workspaces(query, user_id)
    return {"workspaces": workspaces}

@router.post("/patterns/extract/collection", response_model=ExtractPatternsResponse)
def extract_patterns(lists: List[TaskListInput]):
    results = pattern_extraction_collection_service.extract_patterns_from_lists(
        lists_data=[l.model_dump() for l in lists]
    )

    return {
        "results": results
    }