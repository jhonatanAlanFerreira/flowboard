from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.observability.phoenix import get_tracer
from app.services.workspace_chunk_service import WorkspaceService
from app.services.agents.workspace_predictor_agent import WorkspacePredictorAgent
import json

tracer = get_tracer()
backend_client = BackendClient()
workspace_service = WorkspaceService()
workspace_predictor_agent = WorkspacePredictorAgent()

@celery.task
def search_strategist_task(prompt: str, user_id: int):
    with tracer.start_as_current_span("search_strategist") as span:
        
        span.set_attribute("input.prompt", prompt)
        span.set_attribute("input.user_id", str(user_id))

        try:
            user_workspaces = workspace_service.get_workspace_candidates(user_id, prompt)
            
            span.set_attribute("service.workspaces_source", json.dumps(user_workspaces))

            agent_output = workspace_predictor_agent.predict_workspace_intent(
                prompt, 
                user_workspaces
            )

            span.set_attribute("agent.output_prediction", json.dumps(agent_output))

            return {
                "status": "ok",
                "predicted_workspace": agent_output,
                "prompt": prompt
            }

        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise e
