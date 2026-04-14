from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.config import settings
from app.observability.phoenix import get_tracer
from typing import List, Dict

tracer = get_tracer()


class GenerateWorkflowWorkspaceAgent:
    SYSTEM_PROMPT = """
    You are a structural workspace generator.
    Your goal is to build columns for a board where tasks move from state to state.

    STATE-BASED EXAMPLES:
    - Standard: [To Do, In Progress, Blocked, Done]
    - Development: [Backlog, Ready for Dev, In Review, QA, Deployed]
    - Sales: [Lead, Contacted, Negotiation, Won, Lost]

    STRICT RULES:
    - Return ONLY valid JSON.
    - Focus on PROGRESSION (state-to-state movement). Avoid static categories like "Bosses" or "Equipment".
    - Analyze the "REFERENCE WORKFLOWS" to match the user's specific terminology style.

    JSON SCHEMA:
    {{
      "workspace": {{
        "name": string,
        "lists": [
          {{
            "name": string,
          }}
        ]
      }}
    }}
    """

    def generate_workspace_llm(
        self, user_prompt: str, selected_workflow_lists: List[Dict]
    ) -> dict:
        with tracer.start_as_current_span(
            "service.generate_workflow_workspace"
        ) as span:
            # Format the dictionary list into a context string
            if selected_workflow_lists:
                context_parts = []
                for ws in selected_workflow_lists:
                    lists_str = ", ".join(ws.get("lists", []))
                    context_parts.append(f"- Example Workflow: [{lists_str}]")
                reference_str = "REFERENCE WORKFLOWS (Match this style):\n" + "\n".join(
                    context_parts
                )

                # Use the average count from the actual selected workflows
                avg_lists = sum(
                    len(ws.get("lists", [])) for ws in selected_workflow_lists
                ) // len(selected_workflow_lists)
            else:
                reference_str = (
                    "REFERENCE WORKFLOWS: None provided. Use your best judgment."
                )
                avg_lists = 4

            span.set_attribute("input.user_prompt", user_prompt)
            span.set_attribute("input.reference_count", len(selected_workflow_lists))

            full_prompt = f"""
            {self.SYSTEM_PROMPT}
            
            USER REQUEST: "{user_prompt}"

            {reference_str}

            TARGET AVERAGE LISTS: {avg_lists}

            JSON:
            """

            span.set_attribute("llm.prompt", full_prompt)

            agent_config = settings.collection_workspace_agent

            if agent_config.provider == "groq":
                return get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature,
                )
            else:
                return get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature,
                )
