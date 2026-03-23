# Flowboard

Flowboard is a full-stack project management application built with **Angular**, **Laravel**, and **Python**, designed to support **multiple users and multiple workspaces**. It features a **drag-and-drop interface** for task and column management, **LLM-powered content generation** via prompt engineering, and ongoing exploration of **RAG (Retrieval-Augmented Generation)** for enhanced context-aware capabilities. The project is **containerized with Docker** to ensure a consistent development environment.

It supports:

- Multiple users
- Multiple workspaces per user
- Boards with lists and tasks
- Tasks can be marked as **done**
- Sort completed tasks **first or last**
- Search tasks by content
- Drag & drop for lists and tasks (Kanban-style)
- **AI-generated workspaces** (lists, tasks, and structure)
- Docker-based local development
- **Fully local AI** (no external APIs required)

---

## Screenshots & Demos

### 🤖 AI Workspace Generation - Board – Lists & Tasks (Drag & Drop)

![AI Workspace Generation](screenshots/ai_workspace_generate.gif)

> The AI analyzes a natural-language description and generates a complete workspace structure (lists + tasks).  
> The frontend handles async polling and automatically resumes generation after refresh or re-login.

### Login - Board – Lists & Tasks (Drag & Drop)

![Login - Board – Lists & Tasks (Drag & Drop)](screenshots/login_drag_drop.gif)

---

## Tech Stack

### Core

- Backend: **Laravel (PHP)**
- Frontend: **Angular**
- Database: **MySQL**
- Authentication: **JWT**
- Infrastructure: **Docker & Docker Compose**

### AI

- AI API: **Python (FastAPI)**
- LLM Runtime: **llama.cpp**
- Model format: **GGUF**
- Model execution: **Fully local / offline**

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

## Requirements

- Docker
- Docker Compose

No local PHP, Node, Python, or MySQL installation is required.

---

## Environment Configuration

### 1. Root `.env`

Create a `.env` file in the root folder (same level as `docker-compose.yml`).

```
APP_PORT=4200
MYSQL_PORT=3306
BACKEND_PORT=8000
AI_API_PORT=8001

# Absolute path inside the container to the model file
MODEL_PATH=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

### 2. Backend environment (Laravel)

Inside `backend/flowboard`:

```
cp .env.example .env
```

Important variables:

```
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost

DB_CONNECTION=mysql
DB_HOST=dev-mysql
DB_PORT=3306
DB_DATABASE=flowboard
DB_USERNAME=root
DB_PASSWORD=root

JWT_SECRET=
```

---

### 3. Frontend configuration

Create the runtime config file:

    frontend/flowboard/public/config/config.json

You can configure the backend API in two ways:

#### Option A --- Backend on the same machine (recommended for LAN)

Use only the port:

```json
{
  "apiBaseUrl": ":8001"
}
```

In this mode, the application will automatically use the same IP/host
that was used to access the frontend in the browser.

Example:

If you open the frontend at:

    http://192.168.1.50:4200

The API base URL will automatically resolve to:

    http://192.168.1.50:8001

---

#### Option B --- Backend on a different machine

Use the full URL:

```json
{
  "apiBaseUrl": "http://192.168.0.20:8001"
}
```

In this case, the frontend will always call that exact address,
regardless of how it was accessed.

---

Choose the option that matches your infrastructure setup.

---

## AI Setup (Local LLM)

### 1. Download a GGUF model

Recommended (balanced quality/performance):

**Mistral 7B Instruct (Q4_K_M)**

Download from Hugging Face:
https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

File:

```
mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

### 2. Place the model

Create the `models` folder at the project root and place the model inside:

```
models/
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

### 3. Configure model path

Ensure your root `.env` points to the correct path:

```
MODEL_PATH=/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

The AI API runs **fully offline** and loads the model at startup.

---

## Build & Run

From the root folder:

```
docker compose up --build
```

Generate Laravel keys:

```
docker exec -it dev-laravel php artisan key:generate
docker exec -it dev-laravel php artisan jwt:secret
```

Run migrations:

```
docker exec -it dev-laravel php artisan migrate
```

---

## Access

- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- AI API: http://localhost:8001

---
