from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from typing import List, Dict
from app.observability.phoenix import get_tracer
from app.config import settings
import json

tracer = get_tracer()

class WorkflowRefinerAgent:
    """
    Validates workspaces and returns them in the original list-of-dictionaries format.
    """

    SYSTEM_PROMPT = """
    You are a Strict Workflow Classifier. Your job is to separate "Status-based Workflows" from "Topic-based Categories."

    CRITERIA FOR A VALID WORKFLOW:
    - The lists MUST imply a task moving from one stage to another.
    - Typical names: "To Do, Doing, Done", "Backlog, In Progress, Review", "Phase 1, Phase 2, Launch".
    - Look for verbs or progressive nouns.

    CRITERIA FOR REJECTION (NOT A WORKFLOW):
    - The lists are just topics or categories (e.g., "Bosses, Charms, Skills").
    - The lists are informational folders (e.g., "Nutrition, Hydration, Gym Routine").
    - There is no clear "start to finish" progression.

    STRICT RULES:
    - If a workspace looks like a Kanban board or a Project Roadmap, ACCEPT IT.
    - Return ONLY the workspace_id for valid workflows in JSON.
    """


    def filter_workflow_workspaces(self, workspaces_data: List[Dict]) -> List[Dict]:
        with tracer.start_as_current_span("service.filter_workflow_workspaces") as span:
            
            span.set_attribute("input.workspaces_data", workspaces_data)
            
            # Format the multi-workspace input for the LLM
            workspaces_input = "\n".join([
                f"ID: {ws.get('workspace_id')} | Lists: {ws.get('lists')}" 
                for ws in workspaces_data
            ])

            full_prompt = f"""
            {self.SYSTEM_PROMPT}

            WORKSPACES TO EVALUATE:
            {workspaces_input}

            JSON SCHEMA:
            {{ "valid_workspace_ids": ["string"] }}
            """

            span.set_attribute("llm.prompt", full_prompt)
            agent_config = settings.workflow_refiner_agent
            
            if agent_config.provider == "groq":
                response = get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )
            else:
                response = get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )

            if isinstance(response, str):
                    try:
                        response = json.loads(response)
                    except:
                        response = {}

            valid_ids = response.get('valid_workspace_ids', [])
            valid_id_set = set(map(str, valid_ids))

            filtered_workspaces = [
                ws for ws in workspaces_data 
                if str(ws.get('workspace_id')) in valid_id_set
            ]

            span.set_attribute("output.filtered_workspaces", json.dumps(filtered_workspaces))
            
            return filtered_workspaces