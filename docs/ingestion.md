# Data Ingestion and Chunking

This document explains how Flowboard processes raw task data into searchable vector chunks, the separation of AI integration types, and how the semantic tagging system operates.

---

## 1. AI Integration Types

Flowboard utilizes RAG and Generative AI in three distinct ways:

---

## 1. AI Integration Types

Flowboard utilizes RAG and Generative AI in three distinct ways, depending on whether the user is querying existing data or generating new structures.

### 1. Contextual Q&A
Allows users to ask natural language questions about their existing tasks and progress.
*   **Example:** "What tasks are currently blocked in the Alpha project?" or "Summarize my progress for this week."
*   **Data Source:** Uses the **Task** chunks in the Weaviate Chunk Collection.

### 2. Workflow Workspace Generation
Predicts a structured pipeline of lists based on standard task states or operational patterns. 
*   **A Software Development workflow would look like:** 
    `Backlog` -> `In Development` -> `Peer Review` -> `In QA` -> `Done`
*   **Data Source:** Uses **List** chunks to identify recurring status patterns.

### 3. Collection Workspace Generation
Generates a structured categorization of lists for non-linear, topical information storage.
*   **A Video Game collection would look like:** 
    `Main Story Bosses`, `Secret Passages`, `Legendary Items`, `Side Quests`
*   **A Grocery Shopping collection would look like:** 
    `Produce`, `Dairy & Eggs`, `Frozen Goods`, `Household Items`
*   **Data Source:** Uses **Task** chunks to cluster relevant topical information.

---


---

## 2. Database and Vector Schema

The system maintains a unified record in MySQL while splitting data into specialized collections in Weaviate to optimize retrieval accuracy.

### MySQL (rag_chunks table)
Stores all three entity types for reference:
- task
- list
- workspace

### Weaviate (Vector Collections)
Data is split into two primary collections to avoid "Context Contamination":

---

## 2. Database and Vector Schema

The system maintains a unified record in MySQL while splitting data into specialized collections in Weaviate to optimize retrieval accuracy.

### MySQL (rag_chunks table)
Stores all three entity types for reference: `task`, `list`, and `workspace`.

### Weaviate (Vector Collections)
Data is split into two primary collections to ensure the AI uses the correct context for each specific task:

1. **Chunk Collection (Type: Task and List):**
   - **Task Chunks:** Used for **Contextual Q&A** (answering user questions) and for generating **Collection-style Workspaces**. Task content is the primary source of semantic meaning here.
   - **List Chunks:** Used exclusively for **Workflow Workspace** generation. Because list names in a workflow (e.g., "Blocked", "Done") represent *states* rather than topics, the tasks themselves are not semantically related to the list's purpose. The list names are the key unit of context.

2. **Workspace Collection:**
   - Stores only workspace-level data.
   - **Purpose:** When a user asks a question, a specialized agent first analyzes the prompt and returns possible workspace names. The system then performs a semantic search against this **Workspace Collection** to identify which specific workspaces should be used to filter the task data for the final answer.

---


---

## 3. Overview of the Ingestion & Tagging Flow

Data ingestion is strictly event-driven and asynchronous:

1. **User Action:** User creates/updates a Task, List, or Workspace.
2. **Laravel Event:** Backend stores the record in MySQL and triggers an event (e.g., `TaskCreated`).
3. **Chunk Creation:** A listener creates an entry in the Laravel `rag_chunks` table.
4. **Python Sync (Initial):** Laravel calls the FastAPI to vectorize the chunk and store it in the appropriate Weaviate collection.
5. **AI Semantic Tagging (Celery):** 
   - After the vector is stored, the Python side triggers the **Tagging Agent**.
   - The agent performs a semantic search for "Known Tags" already in Weaviate.
   - The agent prefers selecting from these existing tags or creates a new one if necessary.
6. **Final Sync:**
   - New tags are stored in Weaviate.
   - Python calls a Laravel endpoint to store new tags in MySQL and update the original `rag_chunk` metadata.
7. **Observability:** Every step is traceable via Arize Phoenix.

---


## 4. Chunking Strategy

### Content Format
Chunks are formatted as: `"List Name: Task Description"`

### Why exclude the Workspace Name?
The Workspace name is excluded from the vector content to prevent "Coincidence Bias." If a user mentions a Workspace name, we don't want every task in that workspace to receive an artificially high relevance score; we want the search to focus on the actual task content.

---


---

## 5. Implementation Detail: Event-Driven Synchronization

The ingestion and vector synchronization process is fully automated through Laravel Events. Every time a core entity is modified, an event is fired to update both the MySQL `rag_chunks` table and the Weaviate vector index.

### Event Structure
The system monitors 9 specific events across the primary domains:

```
$ app/Events/
├── List/
│   ├── TasklistCreated.php
│   ├── TasklistDeleted.php
│   └── TasklistUpdated.php
├── Task/
│   ├── TaskCreated.php
│   ├── TaskDeleted.php
│   └── TaskUpdated.php
└── Workspace/
    ├── WorkspaceCreated.php
    ├── WorkspaceDeleted.php
    └── WorkspaceUpdated.php
```

### Example: Task Creation
When a task is stored, the event is fired immediately after the database transaction, offloading the AI processing to the queue:

```php
public function store(StoreTaskRequest $request)
{
    $task = Task::create([...]);

    // This triggers the chunking, vectorization, and AI tagging pipeline
    event(new TaskCreated($task));

    return response()->json(['success' => true], 201);
}

