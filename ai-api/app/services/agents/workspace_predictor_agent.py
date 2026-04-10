import json
from typing import Dict, List
from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.observability.phoenix import get_tracer
from app.config import settings

tracer = get_tracer()

class WorkspacePredictorAgent:
    """
    Analyzes the user's prompt to predict target workspaces before any retrieval happens.
    """

    SYSTEM_PROMPT = """
    You are a Workspace Predictor Agent for a task management app. 
    Your job is to analyze a user's question and determine if they are asking about a specific Workspace from a provided list.

    CRITERIA FOR WORKSPACE PREDICTION:
    - Look for explicit mentions of project names, team names, or distinct work areas.
    - If a user mentions a concept that strongly correlates to a workspace name in the provided list, identify it.

    STRICT RULES:
    - If the user is asking a broad question across all their data (e.g., "What are my tasks today?", "Show me my high priority items"), the `workspace_hint` should be null.
    - You must return a confidence score between 0.0 and 1.0 indicating how sure you are that the user's query targets the predicted workspace.
    - Return a clean JSON according to the schema provided.
    """

    def predict_workspace_intent(self, user_prompt: str, available_workspaces: List[Dict]) -> Dict:
        """
        Analyzes the user prompt against available workspaces to extract a target workspace hint.
        """
        with tracer.start_as_current_span("agent.predict_workspace_intent") as span:
            
            span.set_attribute("input.user_prompt", user_prompt)
            span.set_attribute("input.available_workspaces", json.dumps(available_workspaces))
            
            # Format the list of available workspaces for the LLM context
            workspaces_input = "\n".join([
                f"ID: {ws.get('workspace_id')} | Name: {ws.get('name')}" 
                for ws in available_workspaces
            ])

            full_prompt = f"""
            {self.SYSTEM_PROMPT}

            AVAILABLE WORKSPACES FOR THIS USER:
            {workspaces_input}

            USER QUESTION:
            "{user_prompt}"

            JSON SCHEMA:
            {{
                "workspace_hint": "string or null",
                "predicted_workspace_id": "string or null",
                "confidence_score": float,
                "reasoning": "string"
            }}
            """

            span.set_attribute("llm.prompt", full_prompt)
            
            agent_config = settings.workspace_predictor_agent
            
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

            # Safely handle string responses
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except Exception:
                    response = {
                        "workspace_hint": None,
                        "predicted_workspace_id": None,
                        "confidence_score": 0.0,
                        "reasoning": "Failed to parse LLM JSON response"
                    }

            span.set_attribute("output.prediction", json.dumps(response))
            
            return response
