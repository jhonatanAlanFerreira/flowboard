# AI Orchestration

This document describes how Flowboard orchestrates data retrieval and LLM generation to create new workspaces.

---

## 1. The Orchestration Logic

The `RetrievalOrchestratorService` acts as the brain on the Laravel side. It determines which retrieval strategy to use based on the `WorkspaceType`.

### Collection Workspace Flow

The Collection flow uses a multi-stage process to extract "Topic Clusters" rather than just individual tasks.

1. **Intelligent Retrieval (`retrieveLists`)**
   Laravel calls the Python `/retrieval/collection/workspaces-lists` endpoint. Python returns a ranked set of lists with complex scoring metrics:
   - **Relevance:** How well the list content matches the user prompt.
   - **Volume & Concentration:** Measures how many relevant chunks are packed into a single list.
   - **Score:** A weighted combination of vector similarity and list density.

2. **Data Hydration (`hydrateChunks`)**
   Since the Python vector search returns only IDs and scores, Laravel "hydrates" this data:
   - It fetches the `RagChunk` models from MySQL.
   - **Task Extraction:** It isolates the `task_description` (removing the list prefix used for vectorization).
   - **Metadata Injection:** It attaches existing AI-generated tags to each chunk.

3. **Pattern Extraction (`extractPatternsFromCollectionWorkspace`)**
   The hydrated data (Chunks + Descriptions + Tags) is sent back to Python. 
   - **Tag Ranking:** Python ranks the tags based on their occurrence and relevance to the prompt.
   - **Pattern Mapping:** For each high-ranking tag, Python selects the "best representative task."
   - **Result:** Laravel receives an `ExtractPatternsResponseDTO` containing a mapping of Tags to Tasks, which acts as the semantic blueprint for the new workspace.

4. **Generation Context**
   Finally, these patterns are bundled and sent to the LLM to generate a cohesive workspace structure (Lists and Tasks) that matches the discovered patterns.


### Workflow Workspace Flow 
The Workflow flow identifies structural patterns (list sequences) by analyzing how workspaces are organized into stages.

1. **Intelligent Workspace Retrieval (`retrieveWorkspaces`)**
   Laravel queries the Python `/retrieval/workflow/workspaces` endpoint. 
   - **Target Data:** Python focuses exclusively on **chunks typed as "list"** within the collection. 
   - **Logic:** Because the list name (e.g., "In Progress") represents the operational state, Python uses these specific chunks to calculate workspace relevancy.
   - **Scoring Strategy:** Python returns a ranked list of workspaces based on:
     - **Match Count:** How many list-type chunks within a workspace hit the search criteria.
     - **Max Score:** The highest similarity score found among the lists in that workspace.
     - **Final Score:** A weighted ranking used to identify the "Best Structural Examples."

2. **Structural Extraction (`getListsFromWorkspaces`)**
   Laravel takes the top-ranked workspace IDs and retrieves their actual structure from the MySQL `workspaces` and `tasklists` tables:
   - **List Harvesting:** It plucks the names of every list associated with those workspaces.
   - **Structure Mapping:** It maps these list names back to the `WorkspaceListsDTO`.

3. **Context Statistics (`buildGenerationContext`)**
   The final step prepares a statistical blueprint for the LLM:
   - **Pattern Aggregation:** Collects all retrieved list names across the best workspace examples.
   - **Average Density Calculation:** Laravel calculates the `average_lists_per_workspace`.
   - **Result:** A `WorkflowContextDTO` is created, providing the LLM with the most common list names and the expected "length" of the workflow.

4. **Generation Context**
   The LLM uses the frequency of list names and the density metadata to generate a logically sequenced pipeline.

---

## 2. The Generation Lifecycle (Async)

Generation is a multi-step process involving Laravel, Redis, and Celery.

### Phase A: Request & Orchestration
1. User hits `POST /ai/workspaces`.
2. Laravel calls the `Orchestrator` to gather context (Weaviate search).
3. The `WorkspaceGeneratorAgent` builds the final payload.

### Phase B: Python Generation (Celery)
1. Laravel sends a POST request to `/generate-workspace/{type}`.
2. Since this uses an LLM (Groq or Local), the Python API offloads the task to a **Celery Worker**.
3. Laravel returns a "Processing" status to the UI immediately.

### Phase C: The "Callback" (Final Storage)
1. Once the Celery worker finishes the generation, Python needs to save the results back to the main database.
2. Python calls the internal Laravel route: `POST /internal/ai/workspaces`.
3. Laravel receives the generated lists/tasks and stores them in MySQL.

---

## 3. Debugging and Observability

### Debugging Retrieval
To see what context the AI is "seeing" without actually generating a workspace, use the debug route:
- **Route:** `POST /api/ai/retrieval`
- **Controller:** `AIRetrievalController`
- **Output:** Returns raw scores and retrieved chunks from Weaviate.

### Traceability
All orchestrations (both the retrieval calls and the final generation) are automatically traced in **Arize Phoenix** (http://localhost:6006). Use this to check:
- Execution time of Weaviate queries.
- Prompt content sent to the LLM.
- Success/Failure of the Python callback to Laravel.

---

## 4. Internal API Security
The route `/internal/ai/workspaces` is protected by the `ai` middleware. Only the Python AI service is authorized to post data back to this endpoint to prevent external data injection.
