# Flowboard

**Flowboard** is a full-stack, AI-powered project management platform built with **Angular**, **Laravel**, and **Python**, designed to support **multiple users and workspaces at scale**.
It features an intuitive **drag-and-drop interface** for managing tasks and workflows, enhanced by **semantic tagging** and **LLM-based content generation** to streamline organization and productivity.
The platform includes **AI-driven workspace generation**, capable of creating new workspaces based on **user patterns and behavior**, enabling a more personalized and adaptive experience.
It also leverages **RAG (Retrieval-Augmented Generation)** for context-aware task suggestions and smarter content generation.
The entire system is fully **containerized with Docker**, ensuring a consistent, scalable, and easy-to-deploy development environment.

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

### AI

- AI-generated workspaces (lists, tasks, structure)  
- Fully local LLM (no external APIs)
- Async processing with queue workers

---

## Status

This project is currently under active development.  
Core systems like chunking, embeddings, and retrieval are implemented, while RAG-based generation is in progress.

---

## Screenshots & Demos

### AI Workspace Generation

![AI Workspace Generation](screenshots/ai_workspace_generate.gif)

> The AI analyzes a natural-language description and generates a complete workspace structure (lists + tasks).  
> The frontend handles async polling and resumes generation after refresh or re-login.

---

### Login & Board Interaction

![Login - Board](screenshots/login_drag_drop.gif)

---

## Tech Stack

### Core

- Backend: **Laravel (PHP)**  
- Frontend: **Angular**  
- Database: **MySQL**  
- Authentication: **JWT**  
- Infrastructure: **Docker & Docker Compose**

### AI

- API: **FastAPI (Python)**  
- LLM Runtime: **llama.cpp**  
- Model format: **GGUF**  
- Execution: **Fully local / offline**

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

## 3. Download LLM Model

Recommended:

**Mistral 7B Instruct (Q4_K_M)**

https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

File:

```
mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 4. Place Model

```
models/
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 5. Configure Model Path

Update the root .env file (same level as docker-compose.yml):

```
MODEL_PATH=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

## 6. Start the Full Development Environment

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