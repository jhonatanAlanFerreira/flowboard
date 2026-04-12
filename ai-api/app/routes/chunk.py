from fastapi import APIRouter, HTTPException
from app.services.chunk_service import ChunkService
from app.models.request.list_chunk_request import ListChunkPayload
from app.models.request.workspace_request import WorkspacePayload
from app.services.workspace_chunk_service import WorkspaceService

router = APIRouter()
chunk_service = ChunkService()
workspace_chunk_service = WorkspaceService()

@router.delete("/chunks/{chunk_id}", summary="Delete a chunk by ID")
async def delete_chunk(chunk_id: int):
    """
    Deletes a chunk from Weaviate corresponding to the given chunk_id (MySQL task ID)
    """
    success = chunk_service.delete_chunk(chunk_id)
    if success:
        return {"status": "ok", "message": f"Chunk {chunk_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found")


@router.delete("/chunks/tasklist/{tasklist_id}", summary="Delete all chunks for a tasklist")
async def delete_chunks_by_tasklist(tasklist_id: int):
    """
    Deletes all chunks in Weaviate that belong to the given tasklist_id
    """
    deleted_count = chunk_service.delete_by_tasklist(tasklist_id)
    if deleted_count > 0:
        return {"status": "ok", "message": f"Deleted {deleted_count} chunks for tasklist {tasklist_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"No chunks found for tasklist {tasklist_id}")


@router.delete("/chunks/workspace/{workspace_id}", summary="Delete all chunks for a workspace")
async def delete_chunks_by_workspace(workspace_id: int):
    """
    Deletes all chunks in Weaviate that belong to the given workspace_id
    """
    workspace_chunk_service.delete_workspace(workspace_id)
    deleted_count = chunk_service.delete_by_workspace(workspace_id)
    if deleted_count > 0:
        return {"status": "ok", "message": f"Deleted {deleted_count} chunks for workspace {workspace_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"No chunks found for workspace {workspace_id}")
    
@router.post("/chunks/list", summary="Create chunks for a list")
async def create_list_chunks(request: ListChunkPayload):
    """
    Creates RAG chunks for a list.
    """
    content = request.content.strip()
    chunk_id = request.chunk_id
    tasklist_id = request.tasklist_id
    workspace_id = request.workspace_id
    user_id = request.user_id

    try:
        chunking_res = chunk_service.create_or_update_chunk(chunk_id, content, tasklist_id, workspace_id, user_id, "list")

        return {"status": "ok", "message": f"Chunk {chunking_res['id']} deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chunks/workspaces", summary="Index or Update a Workspace Name")
async def create_or_update_workspace(request: WorkspacePayload):
    """
    Creates or updates the vector for a Workspace Name.
    """
    try:
        workspace_chunk_service.upsert_workspace(
            chunk_id=request.chunk_id,
            user_id=request.user_id,
            workspace_id=request.workspace_id, 
            name=request.name
        )
        return {"status": "ok", "workspace_id": request.workspace_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))