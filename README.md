# Flowboard

Flowboard is a full-stack, AI-powered project management platform built with Angular, Laravel, and Python, designed to support multiple users and workspaces at scale.

It features an intuitive drag-and-drop interface for managing tasks and workflows, enhanced by semantic tagging and LLM-based content generation. The platform includes AI-driven workspace generation, capable of creating new workspaces based on user patterns and behavior for a personalized experience.

By leveraging RAG (Retrieval-Augmented Generation), Flowboard can answer natural language questions about user data and tasks, providing context-aware suggestions and smart content generation. The entire system is fully containerized with Docker, ensuring a consistent, scalable, and easy-to-deploy development environment.

---

---

## Features

- Multiple users  
- Multiple workspaces per user  
- Boards with lists and tasks  
- Tasks can be marked as **done**  
- Sort completed tasks **first or last**  
- Search tasks by content  
- Drag & drop for lists and tasks (Kanban-style)  
- Move lists and tasks across workspaces
- Docker-based local development  

### AI Features

- Smart Workspace Generation
  Automatically scaffolds entire workspaces, including lists, tasks, and structural organization, based on user-defined goals or historical patterns.
- Contextual RAG Assistant
  Allows users to ask natural language questions about their tasks and workspaces, providing context-aware answers using indexed data.
- Hybrid LLM Orchestration
  Supports fully local execution via llama.cpp or high-speed generation using the Groq API, configurable via the central AI settings (ai-api/app/config.py).
- Event-Driven Async Processing
  Offloads heavy AI computations (tagging, generation, and chunking) to background queue workers for a responsive, non-blocking UI experience.

---

### Core
- Backend: Laravel (PHP)
- Frontend: Angular
- Database: MySQL & Redis 
- Queue Management: Laravel Queue Workers & Celery (Python)
- Infrastructure: Docker & Docker Compose

### AI and RAG
- AI API: FastAPI (Python)
- Vector Database: Weaviate (Used for semantic search and task chunk storage)
- LLM Runtime: llama.cpp (Local) & Groq API (Cloud Hybrid)
- Observability: Arize Phoenix (Trace/Eval)

---

## Environment & Configuration Files

```
.
├── backend/
│   └── flowboard/
│       ├── .env.example                 # Laravel environment example
│       ├── .env.testing.example         # Laravel environment for testing example
│       └── ...                          # Laravel source files
├── frontend/
│   └── flowboard/
│       ├── public/
│       │   └── config/
│       │       └── config.example.json  # Frontend runtime config example
│       └── ...                          # Angular source files
├── ai-api/
│   └── app/
│       ├── main.py                      # AI API (FastAPI + llama.cpp)
|       ├── config.py                    # AI Scoring, Thresholds, and Provider config
│       └── ...                          # AI source files
├── models/
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
├── docker-compose.yml
├── .env.example                         # Docker environment example
```

---

# Getting Started (Core App)

## Requirements

- Docker  
- Docker Compose  

---

## 1. Environment Configuration

Create a `.env` file in the root:

```
cp .env.example .env
```

---

## 2. Backend Setup

```
cp backend/flowboard/.env.example backend/flowboard/.env
```

```
cp backend/flowboard/.env.testing.example backend/flowboard/.env.testing
```

---

## 3. Frontend Config

Create the runtime config file:

    frontend/flowboard/public/config/config.json

You can configure the backend API in two ways:

#### Option A --- Backend on the same machine (recommended for LAN)

Use only the port:

```json
{
  "apiBaseUrl": ":8000"
}
```

In this mode, the application will automatically use the same IP/host
that was used to access the frontend in the browser.

Example:

If you open the frontend at:

    http://192.168.1.50:4200

The API base URL will automatically resolve to:

    http://192.168.1.50:8000

---

#### Option B --- Backend on a different machine

Use the full URL:

```json
{
  "apiBaseUrl": "http://192.168.0.20:8000"
}
```

In this case, the frontend will always call that exact address,
regardless of how it was accessed.

---

Choose the option that matches your infrastructure setup.

---

## 4. LLM Configuration (Local & Cloud Hybrid)

Flowboard uses a hybrid AI approach. You should configure both a local model and a Groq API key for the best experience.

### A. Local Model Setup (Recommended for Tagging)
The local LLM handles background tasks like semantic tagging and chunking. 

1. Download the Recommended Model:
   Mistral 7B Instruct v0.2 (Q4_K_M) from HuggingFace (TheBloke).
   File: mistral-7b-instruct-v0.2.Q4_K_M.gguf

2. Place the Model:
   Move the file to the project directory:
   models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

3. Update Root .env:
   Ensure the MODEL_PATH matches the filename:
   MODEL_PATH=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

### B. Groq API Setup (Required for Fast Generation)
Using a local LLM for final workspace and answer generation can be very slow on consumer hardware. Recommend using Groq for these tasks.

1. Get an API Key: Create a free key at https://groq.com
2. Update Root .env:
   GROQ_API_KEY=your_api_key_here

Note: You can toggle which provider handles specific tasks inside "ai-api/app/config.py".


## 5. Start the Full Development Environment

Run:
```
    docker compose up -d
```

This will start the following services:

- **mysql8.0** – relational database  
- **flowboard-laravel** – main backend (API & business logic)  
- **flowboard-angular** – frontend application  
- **flowboard-ai-api** – AI service (LLM integration & orchestration)  
- **flowboard-ai-worker** – background worker for AI tasks (tagging, generation, RAG processing)  
- **flowboard-queue** – queue processor for async jobs  
- **redis7** – caching and queue broker  
- **weaviate** – vector database for semantic search / RAG  
- **phoenix** – observability and tracing for LLM workflows  

 Wait for Laravel to be ready

Before generating the keys, check the container logs:

```
docker logs -f dev-laravel
```

 You should wait until you see something like:

```
Starting Laravel development server: http://0.0.0.0:8000
```

Generate keys:

```
docker exec -it dev-laravel php artisan key:generate
```

```
docker exec -it dev-laravel php artisan jwt:secret
```

```
docker exec -it dev-laravel php artisan jwt:secret --env=testing
```

Run migrations:

```
docker exec -it dev-laravel php artisan migrate
```

---

## Run Tests

```
docker exec -it dev-laravel php artisan test
```

```
docker exec -it dev-angular ng test
```

```
docker exec -it dev-ai-api python -m pytest
```

## Commands

### Create missing chunks

```
docker exec -it dev-laravel php artisan tasks:chunk-missing
```

#### For a specific user

```
docker exec -it dev-laravel php artisan tasks:chunk-missing --user_id=123
```

#### Preview mode: logs only the number of missing chunks, does not execute the process

```
docker exec -it dev-laravel php artisan tasks:chunk-missing --preview
```

or

```
docker exec -it dev-laravel php artisan tasks:chunk-missing --user_id=123 --preview
```

## Access

- Frontend: http://localhost:4200
- Backend: http://localhost:8000
- Phoenix: http://localhost:6006

---