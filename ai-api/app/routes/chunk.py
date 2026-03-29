from fastapi import APIRouter, HTTPException
from app.services.chunk_service import ChunkService

router = APIRouter()
chunk_service = ChunkService()

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
    deleted_count = chunk_service.delete_by_workspace(workspace_id)
    if deleted_count > 0:
        return {"status": "ok", "message": f"Deleted {deleted_count} chunks for workspace {workspace_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"No chunks found for workspace {workspace_id}")