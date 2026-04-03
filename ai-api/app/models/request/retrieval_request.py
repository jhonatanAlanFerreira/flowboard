from pydantic import BaseModel
from enum import Enum

class WorkspaceType(str, Enum):
    workflow = "workflow"
    collection = "collection"

class RetrievalRequest(BaseModel):
    query: str
    user_id: int
    type: WorkspaceType