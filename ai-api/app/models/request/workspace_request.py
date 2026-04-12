from pydantic import BaseModel

class WorkspacePayload(BaseModel):
    workspace_id: int
    chunk_id: int
    name: str
    user_id: int
