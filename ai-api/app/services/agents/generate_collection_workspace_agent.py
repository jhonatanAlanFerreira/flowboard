from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.config import settings
import json


class GenerateCollectionWorkspaceAgent:
    SYSTEM_PROMPT = """
    You are a structured data generator. 
    Your goal is to expand a workspace based on a user prompt while maintaining the style and structure of their existing lists.

    STRICT RULES:
    - Return ONLY valid JSON (no markdown, no extra text).
    - If "REFERENCE PATTERNS" are provided, match the user's naming style and task depth.
    - If no patterns are provided, create a professional industry-standard structure.
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
        # Defaults for cold-start (new users)
        avg_lists = workspace_patterns.get("average_lists_per_workspace") or 6
        avg_tasks = workspace_patterns.get("average_tasks_per_list") or 6

        # Convert existing lists into a JSON string to preserve task integrity
        existing_lists = workspace_patterns.get("lists", [])
        formatted_patterns = []
        for lst in existing_lists:
            # Map each string task into the required object format for the example
            formatted_tasks = [
                {"description": task} if isinstance(task, str) else task
                for task in lst.get("tasks", [])
            ]
            formatted_patterns.append(
                {"name": lst.get("name"), "tasks": formatted_tasks}
            )
            patterns_str = json.dumps(existing_lists, indent=2)
        else:
            patterns_str = (
                "No existing patterns. Generate a logical structure from scratch."
            )

        full_prompt = f"""
      {self.SYSTEM_PROMPT}
      
      GOAL: Create at least {avg_lists} lists and at least {avg_tasks} tasks each.

      REFERENCE PATTERNS (Existing user structure):
      {patterns_str}

      USER TASK:
      {user_prompt}

      JSON:
      """

        agent_config = settings.collection_workspace_agent

        if agent_config.provider == "groq":
            return get_groq_json_completion(
                full_prompt,
                agent_config.model_name,
                agent_config.max_tokens,
                agent_config.temperature,
            )
        else:
            return get_local_json_completion(
                full_prompt, agent_config.max_tokens, agent_config.temperature
            )
