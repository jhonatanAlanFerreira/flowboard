# Retrieval Strategy: Collection Generation

This document details the Python-side logic for retrieving and scoring data used in **Collection Workspace Generation**.

---

## 1. Two-Stage Retrieval Process

Unlike a simple search, the Collection strategy uses a "Broad-to-Narrow" approach:
1. **Workspace Discovery:** Find the best workspaces that match the user's topical prompt.
2. **List Extraction:** Extract the specific task lists within those workspaces that contain the highest density of relevant information.

---

## 2. Stage 1: Workspace Ranking Logic

The system performs a **Hybrid Search** (Semantic + Keyword) on the "Chunk" collection, filtered by `user_id` and `type="task"`.

### Mathematical Scoring (`rank_workspaces`)
Since a workspace might contain dozens of matching tasks, Python calculates a weighted score to rank the workspace as a whole:

**Formula:**
`Final Score = Max(Similarity Scores) + Weight * log(1 + Match Count)`

- **Max Score:** Ensures the workspace contains at least one highly relevant piece of data.
- **Logarithmic Weight:** Rewards workspaces that have a higher volume of matches (density) but uses a log scale to prevent large workspaces from completely dominating smaller, more precise ones.

### Selection Filters
Before proceeding, candidates must pass two quality gates:
1. **Absolute Threshold:** Chunks must meet a minimum similarity score (e.g., 0.6).
2. **Relative Threshold:** Chunks must be within a specific percentage of the best-performing result to ensure context consistency.

---

## 3. Stage 2: List Scoping (`get_relevant_lists_for_workspaces`)

Once the best workspaces are identified, the system zooms into the **Tasklists** within those specific workspaces.

- **Constraint:** Weaviate is queried using a `contains_any` filter on the `workspace_id` list obtained in Stage 1.
- **Aggregation:** Matches are grouped by `tasklist_id`.

### Advanced Metrics (`compute_features`)
For each list, the system calculates several "features" used for the final ranking:
- **Relevance:** The average similarity of all chunks in the list.
- **Volume:** The total number of matches in the list.
- **Concentration:** How "packed" the relevant chunks are within that specific list structure.

---

## 4. Why This Works
By using **Hybrid Search (Alpha)**, the system balances the LLM's understanding of meaning (semantic) with the user's specific terminology (keyword).

- **High Alpha:** Favors semantic meaning (e.g., searching for "Productivity" finds "Efficiency").
- **Low Alpha:** Favors exact words (e.g., searching for "Boss" finds "Boss").

The final output is a set of `ScoredTaskList` DTOs sent to Laravel, which then performs the "Hydration" and "Pattern Extraction" steps described in the Orchestration docs.

---

## 5. Observability
This entire process is instrumented with **OpenTelemetry**. In **Arize Phoenix**, you can inspect:
- `input.query`: The user's raw prompt.
- `retrieval.workspace_match_count`: How many chunks were found per workspace.
- `selection.thresholds`: The specific cut-off points used for that request.
