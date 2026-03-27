from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

from app.services.llm.workspace_generator import WorkspaceGenerator

router = APIRouter()

workspace_generator = WorkspaceGenerator()

class WorkspaceRequest(BaseModel):
    prompt: str


@router.post("/generate-workspace")
def generate_workspace(data: WorkspaceRequest):
    raw_output = workspace_generator.generate_workspace_llm(data.prompt)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "invalid_json_from_model",
                "raw_output": raw_output
            }
        )

    return parsed