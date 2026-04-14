from fastapi import APIRouter
from app.models.request.retrieval_collection_request import RetrievalCollectionRequest
from app.models.response.retrieval_collection_response import RetrievalCollectionResponse
from app.models.request.retrieval_workflow_request import RetrievalWorkflowRequest
from app.models.response.retrieval_workflow_response import RetrievalWorkflowResponse
from typing import List
from app.models.request.patterns_extract_request import TaskListInput 
from app.models.response.patterns_extract_reponse import ExtractPatternsResponse
from app.services.workflow.workflow_retrieval_service import WorkflowRetrievalService
from app.services.collection.collection_retrieval_service import CollectionRetrievalService
from app.services.collection.collection_pattern_extraction_service import CollectionPatternExtractionService
from app.schemas.workspace import WorkspaceResult
from app.schemas.chunk import ScoredTaskList

router = APIRouter()

collection_retrieval_service = CollectionRetrievalService()
workflow_retrieval_service = WorkflowRetrievalService()
collection_pattern_extraction_service = CollectionPatternExtractionService()


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

    workspaces: List[WorkspaceResult] = collection_retrieval_service.get_relevant_workspaces(query, user_id)
    lists: List[ScoredTaskList] = collection_retrieval_service.get_relevant_lists_for_workspaces(workspace_ids=[ws.workspace_id for ws in workspaces], query=query)
    
    return RetrievalCollectionResponse(lists=[
        {
            **l.model_dump(exclude={"features"}), 
            **l.features.model_dump()            
        } 
        for l in lists
    ])

@router.post(
    "/workflow/workspaces",
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

    workspaces = workflow_retrieval_service.get_relevant_workspaces(query, user_id)
    return {"workspaces": workspaces}

@router.post("/patterns/extract/collection", response_model=ExtractPatternsResponse)
def extract_patterns(lists: List[TaskListInput]):
    results = collection_pattern_extraction_service.extract_patterns_from_lists(
        lists_data=lists
    )

    return {
        "results": results
    }