# Retrieval Strategy: Workflow Generation

This document details the Python-side logic for retrieving and scoring workspaces to act as structural templates for **Workflow Generation**.

---

## 1. Structural Retrieval Logic

The Workflow strategy assumes that the "operational state" of a project is best described by its list names (e.g., "To Do", "In Progress"). Therefore, the retrieval focuses on list metadata rather than individual task descriptions.

### Targeted Search
The system performs a **Hybrid Search** on the `Chunk` collection with a strict filter:
- **Filter:** `user_id == current_user` AND **`type == "list"`**.
- **Alpha (0.5):** An equal balance between semantic meaning and exact keyword matching.

By isolating `type: list`, the search ensures that if a user asks for a "Software Dev" workflow, the AI looks for workspaces that already contain lists with similar names, ignoring the specific tasks inside them.

---

## 2. Workspace Scoring Strategy (`rank_workspaces`)

When multiple list chunks from the same workspace match the query, the system uses a **Density-Boosted Max Score** to rank the workspace's relevance.

### The Formula:
`Final Score = Max(Similarity Scores) + Weight * log(1 + Match Count)`

- **Max Score:** Identifies the strongest individual match (e.g., a list named "Development" perfectly matching the prompt).
- **Match Count (Density):** Rewards workspaces that have multiple relevant lists. If a workspace has "Backlog", "Dev", and "QA" all matching the "Software" prompt, it receives a higher structural rank than a workspace with only one match.
- **Logarithmic Scaling:** Using `math.log(1 + count)` ensures that a workspace with 20 lists doesn't unfairly overpower a highly relevant workspace with only 5 lists.

---

## 3. Selection and Quality Gates

The `WorkflowSelectionService` applies two layers of filtering to ensure the LLM only receives high-quality structural examples:

1. **Absolute Threshold (`_filter_min_similarity`):**
   Removes any workspace where even the best-matching list fails to meet the `min_similarity` floor (defined in `config.py`).
   
2. **Relative Threshold (`_filter_relative_to_best`):**
   Calculates the gap between the top-scoring workspace and others. If the top result has a score of 1.0 and a secondary result has 0.4, the latter may be discarded to keep the context "pure" and focused on the most relevant patterns.

---

## 4. Output to Laravel

The result is a collection of `WorkspaceResult` DTOs. Laravel then uses these IDs to:
1. Harvest the exact list names from the MySQL `tasklists` table.
2. Calculate the average number of lists to guide the LLM on the expected "length" of the new workflow.

---

## 5. Observability (Arize Phoenix)

Key metrics to monitor for Workflow retrieval:
- `retrieval.workspace_match_count`: Shows how many lists per workspace hit the query.
- `selection.count_after_relative`: Indicates how aggressive the filtering was for a specific prompt.
- `output.top_results`: The final list of workspace IDs that will serve as the structural "blueprint."
