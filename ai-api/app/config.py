from typing import Literal, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ==========================================
# LLM Configurations
# ==========================================


class BaseLLMConfig(BaseModel):
    """Common fields for all LLM calls"""

    max_tokens: int = 1024
    temperature: float = 0.1


class LocalLLMConfig(BaseLLMConfig):
    provider: Literal["local"] = "local"
    n_ctx: int = 1024
    n_threads: int = 8


class GroqLLMConfig(BaseLLMConfig):
    provider: Literal["groq"] = "groq"
    model_name: str


LLMConfig = Union[LocalLLMConfig, GroqLLMConfig]


# ==========================================
# Service Configurations
# ==========================================


class CollectionPatternConfig(BaseModel):
    """
    Adjustable numbers for the CollectionPatternExtractionService class.
    """

    similarity_threshold: float = Field(
        default=0.5, description="Threshold for token-overlap similarity between tags."
    )
    top_k_tags: int = Field(
        default=3, description="Default top K diverse tags to extract per list."
    )
    min_score: float = Field(
        default=0.0, description="Default minimum score to filter chunks."
    )

    # Feature extraction and scoring weights
    top_scores_limit: int = Field(
        default=3,
        description="Number of top scores to consider for relevance calculation.",
    )
    relevance_weight: float = Field(
        default=0.6, description="Weight applied to tag relevance in the final score."
    )
    freq_norm_weight: float = Field(
        default=0.25,
        description="Weight applied to normalized frequency in the final score.",
    )
    coverage_weight: float = Field(
        default=0.15, description="Weight applied to chunk coverage in the final score."
    )


class CollectionRetrievalConfig(BaseModel):
    """
    Adjustable numbers and settings for the CollectionRetrievalService class.
    """

    class_name: str = Field(
        default="Chunk", description="The Weaviate class name used for retrieval."
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="The SentenceTransformer model used for vector encoding.",
    )

    # get_relevant_workspaces parameters
    workspace_retrieval_top_k: int = Field(
        default=50, description="Default retrieval limit for workspace candidates."
    )
    workspace_hybrid_alpha: float = Field(
        default=0.5,
        description="Hybrid search alpha (0 = keyword, 1 = vector) for workspaces.",
    )

    # get_relevant_lists_for_workspaces parameters
    list_retrieval_top_k: int = Field(
        default=5, description="Default retrieval limit for final list results."
    )
    list_hybrid_alpha: float = Field(
        default=0.8,
        description="Hybrid search alpha (0 = keyword, 1 = vector) for lists.",
    )


class CollectionScoringConfig(BaseModel):
    """
    Adjustable numbers and scoring weights for the CollectionScoringService class.
    """

    # rank_workspaces parameters
    workspace_log_weight: float = Field(
        default=0.1,
        description="Multiplier for the log of match counts in workspace scoring.",
    )

    # rank_lists and feature extraction parameters
    feature_top_k: int = Field(
        default=3,
        description="Number of top scores to consider for list relevance calculation.",
    )
    relevance_threshold: float = Field(
        default=0.7,
        description="Minimum score to consider a chunk 'relevant' for volume counts.",
    )

    # List scoring weights
    relevance_weight: float = Field(
        default=0.6, description="Weight applied to relevance in the final list score."
    )
    volume_norm_weight: float = Field(
        default=0.25,
        description="Weight applied to normalized volume in the final list score.",
    )
    concentration_weight: float = Field(
        default=0.15,
        description="Weight applied to concentration in the final list score.",
    )


class CollectionWorkspaceSelectionConfig(BaseModel):
    """
    Adjustable numbers and scoring weights for the CollectionWorkspaceSelectionService class.
    """

    # Filtering thresholds
    min_similarity: float = Field(
        default=0.8,
        description="Minimum absolute similarity score to retain a candidate.",
    )
    relative_threshold: float = Field(
        default=0.8,
        description="Minimum fraction of the top score to retain a candidate.",
    )
    limit: int = Field(
        default=5, description="Maximum number of candidates to return after sorting."
    )

    # Rescoring weights
    similarity_weight: float = Field(
        default=0.6, description="Weight applied to the base similarity score."
    )
    recency_weight: float = Field(
        default=0.15, description="Weight applied to the recency score."
    )
    structure_weight: float = Field(
        default=0.25, description="Weight applied to the structure score."
    )

    # Mock data placeholders (for future signals)
    default_recency_score: float = Field(
        default=0.5, description="Placeholder score for recency signal."
    )
    default_structure_score: float = Field(
        default=0.5, description="Placeholder score for structure signal."
    )


class DataQuestionRetrievalConfig(BaseModel):
    """
    Adjustable numbers and search limits for the DataQuestionRetrievalService class.
    """

    class_name: str = Field(
        default="Chunk", description="The Weaviate class name used for retrieval."
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="The SentenceTransformer model used for vector encoding.",
    )

    # Search logic thresholds
    confidence_threshold: float = Field(
        default=0.5,
        description="Confidence score threshold to trigger targeted workspace searches.",
    )
    hybrid_alpha: float = Field(
        default=0.7, description="Hybrid search alpha (0 = keyword, 1 = vector)."
    )

    # Search limits
    targeted_search_limit: int = Field(
        default=20,
        description="Chunk limit when performing a targeted search inside a specific workspace.",
    )
    global_fallback_limit: int = Field(
        default=10,
        description="Chunk limit when falling back to a global search after a targeted search.",
    )
    pure_global_limit: int = Field(
        default=50,
        description="Chunk limit when only performing a global search (confidence below threshold).",
    )


class DataQuestionScoringConfig(BaseModel):
    """
    Adjustable numbers and scoring weights for the DataQuestionScoringService class.
    """

    default_limit: int = Field(
        default=15, description="Default top K items to return after ranking."
    )

    # Status weights
    not_done_weight: float = Field(
        default=0.2, description="Bonus applied to tasks that are not yet completed."
    )
    done_weight: float = Field(
        default=-0.5, description="Penalty applied to tasks that are already completed."
    )

    # Overlap weight
    double_retrieval_boost: float = Field(
        default=0.3,
        description="Bonus applied if found in both targeted and global search.",
    )

    # Recency decay thresholds and weights
    recent_days_threshold: int = Field(
        default=7, description="Day limit to consider a task highly recent."
    )
    recent_days_boost: float = Field(
        default=0.3,
        description="Bonus applied to tasks created within the highly recent threshold.",
    )

    mid_days_threshold: int = Field(
        default=30, description="Day limit to consider a task moderately recent."
    )
    mid_days_boost: float = Field(
        default=0.15,
        description="Bonus applied to tasks created within the moderately recent threshold.",
    )


class WorkflowWorkspaceSelectionConfig(BaseModel):
    """
    Adjustable numbers and scoring weights for the WorkflowWorkspaceSelectionService class.
    """

    # Filtering thresholds
    min_similarity: float = Field(
        default=0.3,
        description="Minimum absolute similarity score to retain a candidate.",
    )
    relative_threshold: float = Field(
        default=0.6,
        description="Minimum fraction of the top score to retain a candidate.",
    )
    limit: int = Field(
        default=5, description="Maximum number of candidates to return after sorting."
    )

    # Rescoring weights
    similarity_weight: float = Field(
        default=0.6, description="Weight applied to the base similarity score."
    )
    recency_weight: float = Field(
        default=0.15, description="Weight applied to the recency score."
    )
    structure_weight: float = Field(
        default=0.25, description="Weight applied to the structure score."
    )

    # Mock data placeholders (for future signals)
    default_recency_score: float = Field(
        default=0.5, description="Placeholder score for recency signal."
    )
    default_structure_score: float = Field(
        default=0.5, description="Placeholder score for structure signal."
    )


class WorkflowScoringConfig(BaseModel):
    """
    Adjustable numbers and scoring weights for the WorkflowScoringService class.
    """

    workspace_log_weight: float = Field(
        default=0.1,
        description="Multiplier for the log of match counts in workflow workspace scoring.",
    )


# ==========================================
# Master Settings
# ==========================================


class Settings(BaseSettings):
    # Agents
    tagging_agent: LLMConfig = LocalLLMConfig(max_tokens=80, temperature=0.3)

    collection_workspace_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=2048, temperature=0.1
    )

    workflow_workspace_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=2048, temperature=0.1
    )

    workflow_refiner_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=400, temperature=0.0
    )

    workspace_predictor_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=300, temperature=0.0
    )

    data_question_reranker_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=400, temperature=0.0
    )

    data_question_generator_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", max_tokens=400, temperature=0.0
    )

    # Services
    collection_pattern_extraction: CollectionPatternConfig = CollectionPatternConfig()
    collection_retrieval: CollectionRetrievalConfig = CollectionRetrievalConfig()
    collection_scoring: CollectionScoringConfig = CollectionScoringConfig()
    collection_workspace_selection: CollectionWorkspaceSelectionConfig = (
        CollectionWorkspaceSelectionConfig()
    )
    data_question_retrieval: DataQuestionRetrievalConfig = DataQuestionRetrievalConfig()
    data_question_scoring: DataQuestionScoringConfig = DataQuestionScoringConfig()
    workflow_workspace_selection: WorkflowWorkspaceSelectionConfig = (
        WorkflowWorkspaceSelectionConfig()
    )
    workflow_scoring: WorkflowScoringConfig = WorkflowScoringConfig()


settings = Settings()
