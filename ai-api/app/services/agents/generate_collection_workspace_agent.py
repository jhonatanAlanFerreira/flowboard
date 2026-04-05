from app.llm import get_llm
from app.grammars.collection_workspace import WORKSPACE_JSON_GRAMMAR

class GenerateCollectionWorkspaceAgent:
    
  def __init__(self):
    self.llm = get_llm()

  SYSTEM_PROMPT = """
  You are a backend service that generates structured data.

  STRICT RULES:
  - Return ONLY valid JSON
  - NO explanations
  - NO markdown
  - NO comments
  - NO extra text before or after JSON
  - NO trailing commas

  SIZE REQUIREMENTS (MANDATORY):
  - Create AT LEAST 6 lists
  - Each list MUST contain AT LEAST 6 tasks
  - Prefer more lists and tasks when possible
  - Tasks must be specific and non-duplicated

  JSON SCHEMA (must match exactly):

  {
    "workspace": {
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
    "workspace": null,
    "error": "missing_information"
  }
  """


  def generate_workspace_llm(self, user_prompt: str) -> str:
      full_prompt = f"""
        {self.SYSTEM_PROMPT}

        USER TASK:
        {user_prompt}

        JSON:
      """

      result = self.llm(
          full_prompt,
          temperature=0.2,
          max_tokens=1200,
          grammar=WORKSPACE_JSON_GRAMMAR
      )

      return result["choices"][0]["text"].strip()