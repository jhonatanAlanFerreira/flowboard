from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.config import settings
import json


class GenerateCollectionWorkspaceAgent:
    SYSTEM_PROMPT = """
      You are a structured data generator.

      Generate a workspace based on the user request.

      STRICT RULES:
      - Return ONLY valid JSON.
      - If patterns are provided, follow them strictly.
      - Do NOT generate generic or vague tasks.

      PATTERN RULES:
      - Copy the structure of the patterns (lists, grouping, naming).
      - Match the level of detail and tone of tasks.
      - If tasks in patterns have multiple parts, replicate that structure.

    JSON SCHEMA:
    {
      "workspace": {
        "name": "string",
        "lists": [
          {
            "name": "string",
            "tasks": [
              { "description": "string" }
            ]
          }
        ]
      }
    }
    """

    def generate_workspace_llm(self, user_prompt: str, workspace_patterns: dict) -> str:
        avg_lists = workspace_patterns.get("average_lists_per_workspace") or 6
        avg_tasks = workspace_patterns.get("average_tasks_per_list") or 6
        existing_lists = workspace_patterns.get("lists", [])

        if existing_lists:
            formatted_patterns = []
            for lst in existing_lists:
                tasks = [
                    {"description": t} if isinstance(t, str) else t
                    for t in lst.get("tasks", [])
                ]
                unique_tasks = list({t["description"]: t for t in tasks}.values())
                formatted_patterns.append(
                    {"name": lst.get("name"), "tasks": unique_tasks}
                )

            patterns_str = json.dumps(formatted_patterns, indent=2)
        else:
            patterns_str = (
                "No existing patterns. Generate a logical structure from scratch."
            )

        full_prompt = f"""
        {self.SYSTEM_PROMPT}
        
        GOAL: Create ~{avg_lists} lists and ~{avg_tasks} tasks each.
        
        USER REQUEST: {user_prompt}

        REFERENCE PATTERNS (Style guide):
        {patterns_str}

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
