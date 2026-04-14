from unittest.mock import patch
from app.tasks.rank_and_generate_task import rank_and_generate_task
from app.schemas.data_question import ScoredChunk, DataQuestionResponse


@patch("app.tasks.rank_and_generate_task.data_question_scoring_service")
@patch("app.tasks.rank_and_generate_task.data_question_reranker_agent")
@patch("app.tasks.rank_and_generate_task.data_question_generator_agent")
@patch("app.tasks.rank_and_generate_task.backend_client")
def test_rank_and_generate_task_success(
    mock_backend, mock_generator, mock_reranker, mock_scoring
):
    raw_chunks = [
        {
            "chunk_id": "c1",
            "content": "test",
            "workspace_id": "ws1",
            "workspace_name": "ws",
            "search_score": 0.5,
            "done": False,
            "found_in_both": False,
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    mock_scored = [ScoredChunk.model_construct(chunk_id="c1", content="test")]
    mock_scoring.score_and_rank_chunks.return_value = mock_scored
    mock_reranker.rerank_tasks.return_value = mock_scored
    mock_generator.generate_final_answer.return_value = DataQuestionResponse(
        markdown_answer="answer", citations=["c1"]
    )

    rank_and_generate_task("prompt", "job1", raw_chunks)

    mock_backend.complete_data_question.assert_called_once()


@patch("app.tasks.rank_and_generate_task.data_question_scoring_service")
@patch("app.tasks.rank_and_generate_task.data_question_reranker_agent")
@patch("app.tasks.rank_and_generate_task.data_question_generator_agent")
@patch("app.tasks.rank_and_generate_task.backend_client")
def test_rank_and_generate_task_empty_chunks(
    mock_backend, mock_generator, mock_reranker, mock_scoring
):
    mock_scoring.score_and_rank_chunks.return_value = []
    mock_reranker.rerank_tasks.return_value = []
    mock_generator.generate_final_answer.return_value = DataQuestionResponse(
        markdown_answer="none", citations=[]
    )

    rank_and_generate_task("prompt", "job2", [])
    mock_backend.complete_data_question.assert_called_once()
