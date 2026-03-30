from pydantic import BaseModel

class WorkspaceRequest(BaseModel):
    prompt: str
    job_id: int