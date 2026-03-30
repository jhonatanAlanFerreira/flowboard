from app.services.agents.generate_workflow_agent import GenerateWorkflowAgent
from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.schemas.workspace import AIWorkspacePayload
from app.observability.phoenix import get_tracer
import json

tracer = get_tracer()
generator_agent = GenerateWorkflowAgent()
backend_client = BackendClient()

@celery.task
def generate_workflow_task(user_prompt: str, job_id: str):
    with tracer.start_as_current_span("workflow_generation") as span:

        span.set_attribute("job.id", job_id)
        span.set_attribute("input.prompt", user_prompt)

        try:
            # Generate workflow via LLM
            workspace_data = generator_agent.generate_workspace_llm(user_prompt)

            span.set_attribute("raw.llm_output", workspace_data)

            if isinstance(workspace_data, str):
                workspace_data = json.loads(workspace_data)

            workflow = workspace_data.get("workflow")

            span.set_attribute("output.workflow_present", workflow is not None)

            if workflow:
                span.set_attribute("output.workflow.name", workflow.get("name"))

                lists = workflow.get("lists", [])
                span.set_attribute("output.workflow.lists_count", len(lists))

                # Count total tasks
                total_tasks = sum(len(l.get("tasks", [])) for l in lists)
                span.set_attribute("output.workflow.tasks_count", total_tasks)

            # Build payload
            payload = AIWorkspacePayload(
                job_id=job_id,
                workflow=workflow
            )

            # Send to backend
            backend_client.post_workspace(payload)

            span.set_attribute("status", "success")

        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))

            if 'workspace_data' in locals():
                span.set_attribute("error.raw_output", str(workspace_data))

            raise