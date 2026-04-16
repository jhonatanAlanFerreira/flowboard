# AI Configuration Guide

This document serves as a reference for the hyperparameters, scoring weights, and LLM settings defined in `ai-api/app/config.py`.

---

## 1. LLM Provider Configuration

Flowboard supports a hybrid model approach. You can toggle providers globally or per agent.

### Local LLM (llama.cpp)
- **n_ctx**: Context window size (Default: 1024).
- **n_threads**: Number of CPU threads dedicated to inference (Default: 8).
- **temperature**: Controls randomness (Default: 0.1 for high precision).

### Groq LLM (Cloud)
- **model_name**: The specific model used (e.g., `llama3-70b-8192` or `mixtral-8x7b-32768`).
- **Use Case**: Recommended for final workspace and answer generation due to speed.

---

## 2. Collection Strategy Settings

### Pattern Extraction
- **similarity_threshold (0.5)**: Minimum overlap required to group similar tags.
- **top_k_tags (3)**: How many diverse categories the agent extracts per list.
- **relevance_weight (0.6)**: Priority given to how well a tag matches the user prompt.

### Retrieval & Selection
- **workspace_hybrid_alpha (0.5)**: Balanced keyword/vector search for finding workspaces.
- **min_similarity (0.7)**: Hard floor for candidates; anything below this is discarded.
- **relative_threshold (0.8)**: If the best match is 1.0, results below 0.8 are ignored.

---

## 3. Data Question (Q&A) Settings

These settings control the "Assistant" behavior and how it ranks your personal data.

### Search Thresholds
- **confidence_threshold (0.5)**: Minimum confidence required from the Workspace Predictor to trigger a "Targeted Search" inside a specific workspace.
- **hybrid_alpha (0.7)**: Favors semantic meaning over exact keywords to catch conceptual matches.

### Heuristic Scoring Weights
These values are added to the base vector similarity score:
- **not_done_weight (+0.2)**: Boosts active tasks.
- **done_weight (-0.5)**: Penalizes finished tasks in the final answer.
- **double_retrieval_boost (+0.3)**: Bonus if a task is found in both targeted and global search.

### Recency Boosts
- **recent_days_boost (+0.3)**: Applied to tasks created within the last 7 days.
- **mid_days_boost (+0.15)**: Applied to tasks created within the last 30 days.

---

## 4. Workflow Strategy Settings

- **min_similarity (0.3)**: The workflow strategy has a lower threshold than others to allow for a broader range of structural "state" matches (e.g., matching "Development" to "Coding").
- **workspace_log_weight (0.1)**: Multiplier for the density boost; ensures workspaces with more matching list-chunks are ranked higher.

---

## How to Adjust
1. Open `ai-api/app/config.py`.
2. Locate the relevant `Config` class (e.g., `DataQuestionScoringConfig`).
3. Update the `default` value.
4. Restart the `dev-ai-api` and `dev-ai-worker` containers to apply changes.
