# Flowboard

Flowboard is a full-stack project management application built with **Angular**, **Laravel**, and **Python**, designed to support **multiple users and multiple workspaces**.

It features a **drag-and-drop interface** for task and column management and includes **AI-powered workspace generation**, with ongoing exploration of **RAG (Retrieval-Augmented Generation)** for context-aware capabilities.

The project is fully **containerized with Docker**, allowing a consistent and simple setup.

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

### AI (Optional)

- AI-generated workspaces (lists, tasks, structure)  
- Fully local LLM (no external APIs)  
- Async processing with queue workers  

---

## Screenshots & Demos

### 🤖 AI Workspace Generation

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

### AI (Optional)

- API: **FastAPI (Python)**  
- LLM Runtime: **llama.cpp**  
- Model format: **GGUF**  
- Execution: **Fully local / offline**

---

## Project Structure

```
.
├── backend/
│   └── flowboard/
│       ├── .env.example                 # Laravel environment example
│       └── ...                          # Laravel source files
├── frontend/
│   └── flowboard/
│       ├── public/
│       │   └── config/
│       │       └── config.example.json  # Frontend runtime config example
│       └── ...                          # Angular source files
├── ai-api/
│   ├── main.py                          # AI API (FastAPI + llama.cpp)
│   └── requirements.txt
├── models/
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
├── docker-compose.yml
├── .env.example                         # Docker environment example
```

---

# Getting Started (Core App)

The application is designed to work **without AI by default**.

This means you can run the full frontend + backend stack without needing to download any model or run the AI services.

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

## 4. Run Core App

```
docker compose up -d
```

This will start:

- MySQL  
- Laravel backend  
- Angular frontend

⏳ Wait for Laravel to be ready

Before generating the keys, check the container logs:

```
docker logs -f dev-laravel
```

✅ You should wait until you see something like:

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

## Access

- Frontend: http://localhost:4200  
- Backend: http://localhost:8000  

---

# 🤖 AI Setup (Optional)

The AI system is **completely optional** and runs separately using Docker profiles.

## Why Local LLM?

Flowboard uses a **local LLM** to:

- Avoid API rate limits  
- Eliminate usage costs  
- Ensure privacy (no external calls)  
- Allow unlimited experimentation  

---

## 1. Download Model

Recommended:

**Mistral 7B Instruct (Q4_K_M)**

https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

File:

```
mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 2. Place Model

```
models/
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 3. Configure Model Path

Update the root .env file (same level as docker-compose.yml):

```
MODEL_PATH=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

## 4. Run AI Services

```
docker compose --profile ai --profile workers up -d
```

This enables:

- AI API (FastAPI + llama.cpp)  
- Queue workers (for async processing)  

---

## AI Access

- AI API: http://localhost:8001

---

## Notes

- The app works fully **without AI**  
- AI features require both:
  - `ai` profile  
  - `workers` profile  
- Queue is required for async AI generation  
