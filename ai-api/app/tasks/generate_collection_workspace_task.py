from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.schemas.workspace import AIWorkspacePayload
from app.services.agents.generate_collection_workspace_agent import (
    GenerateCollectionWorkspaceAgent,
)
from app.observability.phoenix import get_tracer
import json

tracer = get_tracer()
generator_agent = GenerateCollectionWorkspaceAgent()
backend_client = BackendClient()


@celery.task
def generate_collection_workspace_task(
    user_prompt: str, job_id: str, workspace_patterns: dict
):
    with tracer.start_as_current_span("collection_workspace_generation") as span:
        span.set_attribute("job.id", job_id)
        span.set_attribute("input.prompt", user_prompt)
        span.set_attribute("input.workspace_patterns", json.dumps(workspace_patterns))

        try:
            # Generate workflow via LLM
            workspace_data = generator_agent.generate_workspace_llm(
                user_prompt, workspace_patterns
            )

            if isinstance(workspace_data, str):
                workspace_data = json.loads(workspace_data)

            workspace = workspace_data.get("workspace")

            span.set_attribute("output.workspace_present", workspace is not None)

            if workspace:
                span.set_attribute("output.workspace.name", workspace.get("name"))

                lists = workspace.get("lists", [])
                span.set_attribute("output.workspace.lists_count", len(lists))

                # Count total tasks
                total_tasks = sum(len(l.get("tasks", [])) for l in lists)
                span.set_attribute("output.workspace.tasks_count", total_tasks)

            # Build payload
            payload = AIWorkspacePayload(job_id=job_id, workspace=workspace)

            # Send to backend
            backend_client.post_workspace(payload)

            span.set_attribute("status", "success")

        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))

            if "workspace_data" in locals():
                span.set_attribute("error.raw_output", str(workspace_data))

            raise
