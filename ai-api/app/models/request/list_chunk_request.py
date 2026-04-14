from pydantic import BaseModel


class ListChunkPayload(BaseModel):
    content: str
    chunk_id: int
    tasklist_id: int
    workspace_id: int
    user_id: int
