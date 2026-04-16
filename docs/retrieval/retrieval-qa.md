# Retrieval Strategy: Contextual Q&A (The Assistant)

This document explains the "Search Strategist" logic used to answer user questions about their own data. It uses a two-pass retrieval system: Workspace Prediction followed by Hybrid Search.

---

## 1. The Search Strategist Flow

When a user asks a question, the system does not search all tasks immediately. Instead, it follows this asynchronous lifecycle:

1. **Discovery:** Python retrieves the top 10 Workspace candidates from Weaviate based on the user's prompt.
2. **Intent Prediction:** The `WorkspacePredictorAgent` analyzes the prompt and the candidates to decide if the user is asking about a *specific* workspace or *all* workspaces.
3. **Multi-Pass Retrieval:** 
   - **Targeted Search:** If an intent is predicted with high confidence, the system searches specifically inside that workspace.
   - **Global Fallback:** Simultaneously, a global search is performed to ensure no relevant tasks from other areas are missed.
4. **Hydration & Re-ranking:** Laravel enriches the found chunks with MySQL data (dates, status, names), and a final LLM agent generates the answer.

---

## 2. Workspace Prediction Logic

Before searching for tasks, the system tries to "narrow the field."

### Get Workspace Candidates
Python performs a hybrid search on the **Workspace Collection** (filtered by `user_id`). It looks for workspace names that semantically match the user's question.

### The Predictor Agent
The `WorkspacePredictorAgent` receives the prompt and the list of candidate workspace names. It returns:
- `predicted_workspace_id`: The ID of the workspace it thinks the user is talking about.
- `confidence_score`: How sure the agent is (0.0 to 1.0).

---

## 3. Targeted vs. Global Search (`retrieve_chunks_for_question`)

The system handles the retrieval differently based on the agent's confidence:

### Case A: High Confidence (Above Threshold)
The system executes two parallel searches:
1. **Targeted:** A search limited strictly to the `predicted_workspace_id`.
2. **Fallback:** A smaller global search across all the user's data.
3. **Merge:** If a chunk is found in both, it is flagged (`found_in_both = True`), boosting its importance for the final answer.

### Case B: Low Confidence
The system executes a **Pure Global Search**. It ignores the prediction and searches across every task the user owns to find the best matches.

---

## 4. Laravel Data Hydration

Once Python finds the relevant `chunk_ids`, it calls a Laravel endpoint to "hydrate" the results. Laravel adds critical business context that isn't stored in the vector database:
- **Task Status:** Is the task `done`?
- **Timeline:** The `created_at` timestamp.
- **Breadcrumbs:** The actual human-readable `workspace_name`.

This enriched data is then sent back to the Python `process-answer` route for the final LLM generation.

---

## 5. Observability (Arize Phoenix)

Because this strategy uses an agent *before* a search, monitoring is vital:
- `agent.output_prediction`: Check if the agent correctly identified the workspace the user mentioned.
- `input.confidence`: See if your `confidence_threshold` in `config.py` is too high or too low.
- `service.question_retrieval`: View the breakdown of Targeted vs. Global hits.


---

## 4. Scoring and Heuristic Ranking (`score_and_rank_chunks`)

Once Laravel hydrates the tasks with business metadata, Python applies a multi-factor scoring formula to determine which chunks are truly the most relevant.

### The Scoring Formula
`Final Score = Base Search Score + Status Weight + Retrieval Boost + Recency Boost`

- **Base Search Score:** The raw similarity score from Weaviate.
- **Status Weight:** The system prioritizes incomplete tasks (`not_done_weight`) over completed ones, assuming users usually ask about active work.
- **Double Retrieval Boost:** If a chunk was found in both the *Targeted* and *Global* searches, it receives a significant priority boost.
- **Recency Boost:** Uses a decaying boost based on the task's age:
  - **Recent:** (e.g., < 7 days) Highest boost.
  - **Mid-range:** (e.g., < 30 days) Moderate boost.
  - **Old:** No boost.

---

## 5. Re-ranking and Final Generation

After the mathematical scoring, the top candidates undergo a final qualitative check before being presented to the user.

### LLM Re-ranking (`rerank_tasks`)
The system passes the top candidates to the `data_question_reranker_agent`. 
- **The Goal:** The LLM evaluates the tasks semantically against the prompt to ensure the "Top 5" aren't just mathematically relevant, but actually answer the user's specific intent.
- **The Filter:** It removes any noise that the vector search might have captured by mistake.

### Final Answer Generation (`generate_final_answer`)
The top 5 re-ranked chunks are sent to the final generator.
- **Output:** A structured `markdown_answer`.
- **Citations:** The agent returns a list of `chunk_ids` used to generate the answer, providing transparency and allowing the user to verify the source data.

---

## 6. Closing the Loop: Laravel Completion

Once the answer is ready, Python calls the internal Laravel route `POST /internal/ai/data-question/complete/{jobId}`.

### Data Storage:
Laravel updates the `AIJob` record in MySQL:
1. **Status:** Marked as `done`.
2. **Metadata:** Stores the `markdown_answer` and the `source_chunk_ids` (citations).
3. **UI Sync:** The frontend (Angular) polls this record or receives a notification to display the final response to the user.

---

## 7. Configuration Hyperparameters

All weights used in the scoring phase are configurable in `ai-api/app/config.py`:
- `not_done_weight` / `done_weight`
- `double_retrieval_boost`
- `recent_days_threshold` / `recent_days_boost`
