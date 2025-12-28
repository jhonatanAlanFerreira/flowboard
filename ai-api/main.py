from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
import os
import json

app = FastAPI()

llm = Llama(
    model_path=os.environ["MODEL_PATH"],
    n_ctx=4096,
    n_threads=8
)

class WorkspaceRequest(BaseModel):
    prompt: str


SYSTEM_PROMPT = """
You are a backend service that generates structured data.

STRICT RULES:
- Return ONLY valid JSON
- NO explanations
- NO markdown
- NO comments
- NO extra text before or after JSON
- NO trailing commas

JSON SCHEMA (must match exactly):

{
  "workflow": {
    "name": string,
    "lists": [
      {
        "name": string,
        "tasks": [
          { "description": string }
        ]
      }
    ]
  }
}

If there is not enough information, return EXACTLY:

{
  "error": "missing_information",
  "message": "ask a clear follow-up question"
}
"""


@app.post("/generate-workspace")
def generate_workspace(data: WorkspaceRequest):
    full_prompt = f"""
{SYSTEM_PROMPT}

USER TASK:
{data.prompt}

JSON:
"""

    result = llm(
        full_prompt,
        temperature=0.2,
        max_tokens=1200
    )

    raw_output = result["choices"][0]["text"].strip()

    # ---- SAFETY NET: JSON validation ----
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
