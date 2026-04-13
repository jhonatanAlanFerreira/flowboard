import json
import pytest
from unittest.mock import MagicMock, call
from app.enums.chunk_type import ChunkType
from app.schemas.chunk import UpdateTagsPayload

from app.tasks.chunk_tasks import generate_tags_task, normalize_tag


@pytest.fixture
def mock_dependencies(mocker):
    """Fixture to mock all global state & external clients used in the file."""
    mock_span = MagicMock()
    mock_tracer = MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    mocker.patch("app.tasks.chunk_tasks.tracer", mock_tracer)
    
    mock_tag_service = mocker.patch("app.tasks.chunk_tasks.tagging_service")
    mock_chunk_service = mocker.patch("app.tasks.chunk_tasks.chunk_service")
    mock_tag_agent = mocker.patch("app.tasks.chunk_tasks.tag_agent")
    mock_backend_client = mocker.patch("app.tasks.chunk_tasks.backend_client")
    
    return {
        "span": mock_span,
        "tag_service": mock_tag_service,
        "chunk_service": mock_chunk_service,
        "tag_agent": mock_tag_agent,
        "backend_client": mock_backend_client
    }


def test_generate_tags_task_success(mock_dependencies):
    """Tests that the task executes the full pipeline correctly when given valid data."""
    deps = mock_dependencies
    
    chunk_id = 101
    text = "Write a unit test for Celery tasks"
    content = "Detailed content about celery"
    tasklist_id = 5
    workspace_id = 1
    user_id = 42
    
    deps["tag_service"].suggest_tags_for_text.return_value = ["python", "celery"]
    
    deps["tag_agent"].generate_tags.return_value = '{"tags": ["Unit Test ", "Celery !!"]}'
    deps["chunk_service"].create_or_update_chunk.return_value = {"status": "success"}

    generate_tags_task(chunk_id, text, content, tasklist_id, workspace_id, user_id)

    deps["tag_agent"].generate_tags.assert_called_once_with(text, ["python", "celery"])
    
    deps["chunk_service"].create_or_update_chunk.assert_called_once_with(
        chunk_id, content, tasklist_id, workspace_id, user_id, ChunkType.TASK.value
    )
    
    called_args, _ = deps["backend_client"].put_update_tags.call_args
    passed_payload = called_args[0]
    passed_chunk_id = called_args[1]
    
    assert isinstance(passed_payload, UpdateTagsPayload)
    
    assert passed_payload.tags == ["unit_test", "celery_"]
    assert passed_chunk_id == chunk_id
    
    deps["span"].set_attribute.assert_any_call("output.tags", ["Unit Test ", "Celery !!"])


def test_normalize_tag():
    """Tests the standalone regex helper function independently."""
    assert normalize_tag("  Hello World  ") == "hello_world"
    assert normalize_tag("Special@#Characters!") == "specialcharacters"
    assert normalize_tag("multiple   spaces  and-dashes") == "multiple_spaces_and_dashes"
    assert normalize_tag("UPPERCASE") == "uppercase"
