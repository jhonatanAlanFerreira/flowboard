from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.config import settings
from app.observability.phoenix import get_tracer

tracer = get_tracer()

class GenerateWorkflowWorkspaceAgent:

    SYSTEM_PROMPT = """
    You are a structural workspace generator.
    Your goal is to build the structure of a workspace based on a user prompt and a set of refined workflow lists.

    STRICT RULES:
    - Return ONLY valid JSON.
    - Use the "REFINED LISTS" provided as example for the column structure.
    - For every list, the "tasks" array MUST be empty [].
    - Create a professional name for the workspace based on the user prompt.
    - Aim for the "Target Average" number of lists provided in the context.

    JSON SCHEMA:
    {
      "workspace": {
        "name": "string",
        "lists": [
          {
            "name": "string",
            "tasks": []
          }
        ]
      }
    }
    """

    def generate_workspace_llm(self, user_prompt: str, workspace_patterns: dict) -> dict:
        with tracer.start_as_current_span("service.generate_workflow_workspace") as span:
            
            # Extract patterns
            refined_lists = workspace_patterns.get("lists", [])
            avg_lists = workspace_patterns.get("average_lists_per_workspace")
            
            span.set_attribute("input.user_prompt", user_prompt)
            span.set_attribute("input.refined_lists", refined_lists)
            span.set_attribute("input.target_average", avg_lists)

            full_prompt = f"""
            {self.SYSTEM_PROMPT}
            
            USER REQUEST: "{user_prompt}"

            REFINED LISTS (Use these as your structural basis):
            {", ".join(refined_lists)}

            TARGET AVERAGE LISTS PER WORKSPACE: {avg_lists}

            JSON:
            """

            span.set_attribute("llm.prompt", full_prompt)

            agent_config = settings.collection_workspace_agent
            
            if agent_config.provider == "groq":
                return get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )
            else:
                return get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )
