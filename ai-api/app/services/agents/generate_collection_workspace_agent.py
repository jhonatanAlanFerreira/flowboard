from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.config import settings

class GenerateCollectionWorkspaceAgent:

    SYSTEM_PROMPT = """
    You are a structured data generator. 
    Your goal is to expand a workspace based on a user prompt while maintaining the style and structure of their existing lists.

    STRICT RULES:
    - Return ONLY valid JSON (no markdown, no extra text).
    - Use the provided "REFERENCE PATTERNS" to match the user's naming style and task depth.
    - Do not duplicate existing tasks or list names provided in the patterns.

    JSON SCHEMA:
    {{
      "workspace": {{
        "name": string,
        "lists": [
          {{
            "name": string,
            "tasks": [
              {{ "description": string }}
            ]
          }}
        ]
      }}
    }}
    """

    def generate_workspace_llm(self, user_prompt: str, workspace_patterns: dict) -> str:
        # Convert the dictionary of existing lists into a readable string for the LLM
        patterns_str = ""
        for lst in workspace_patterns.get("lists", []):
            tasks_preview = ", ".join(lst.get("tasks", []))
            patterns_str += f"- List: {lst.get('name')} (Examples: {tasks_preview})\n"

        full_prompt = f"""
        {self.SYSTEM_PROMPT}
        
        Create at least {workspace_patterns.get("average_lists_per_workspace")} lists 
        and at least {workspace_patterns.get("average_tasks_per_list")} tasks each.

        REFERENCE PATTERNS (Existing user structure):
        {patterns_str}

        USER TASK:
        {user_prompt}

        JSON:
        """

        if settings.collection_workspace_agent.provider == "groq":
            return get_groq_json_completion(
                full_prompt,
                settings.collection_workspace_agent.model_name,
                settings.collection_workspace_agent.max_tokens,
                settings.collection_workspace_agent.temperature
            )
        else:
            return get_local_json_completion(
                full_prompt,
                settings.collection_workspace_agent.max_tokens,
                settings.collection_workspace_agent.temperature
            )