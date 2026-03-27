from pydantic import BaseModel

class WorkspaceRequest(BaseModel):
    prompt: str