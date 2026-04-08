from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.observability.phoenix import get_tracer
from app.services.agents.generate_workflow_workspace_agent import GenerateWorkflowWorkspaceAgent
from app.schemas.workspace import AIWorkspacePayload
from app.services.agents.refine_workflow_lists import WorkflowRefinerAgent
import json
from typing import List

tracer = get_tracer()
generator_agent = GenerateWorkflowWorkspaceAgent()
backend_client = BackendClient()
workflow_refiner_agent = WorkflowRefinerAgent()

@celery.task
def generate_workflow_workspace_task(user_prompt: str, job_id: str, workspace_patterns: dict):
    with tracer.start_as_current_span("workflow_workspace_generation") as span:

        span.set_attribute("job.id", job_id)
        span.set_attribute("input.prompt", user_prompt)
        span.set_attribute("input.workspace_patterns", json.dumps(workspace_patterns))

        try:
            # Select only relevant lists
            selectedWorkflowLists = workflow_refiner_agent.filter_workflow_workspaces(workspace_patterns.get('workflowLists'))
            
            # Generate workflow via LLM
            workspace_data = generator_agent.generate_workspace_llm(user_prompt, selectedWorkflowLists)
            source_workspace_ids: List[int] = [int(ws['workspace_id']) for ws in selectedWorkflowLists]
            
            if isinstance(workspace_data, str):
                workspace_data = json.loads(workspace_data)

            workspace = workspace_data.get("workspace")

            span.set_attribute("output.workspace_present", workspace is not None)

            if workspace:
                span.set_attribute("output.workspace.name", workspace.get("name"))

                lists = workspace.get("lists", [])
                span.set_attribute("output.workspace.lists_count", len(lists))

            # Build payload
            payload = AIWorkspacePayload(
                job_id=job_id,
                workspace=workspace,
                source_workspace_ids=source_workspace_ids
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