# Project Overview

This project is a full-stack AI-powered resume helper chatbot built using FastAPI, Docker, and LLM integrations. The application allows users to interact with a chatbot through a web-based chat interface, upload resume PDFs, and receive AI-generated responses such as detected skills and suggested skill gaps based on current job market data.

The project combines:

- A frontend FastAPI service for the chat UI
- A backend FastAPI service for AI processing
- Week 2 AI components (`find_skill_gaps.py`, `prompt_model.py`)
- Docker containerization and orchestration using Docker Compose

The system follows a microservices architecture where the frontend and backend are separated into independent services communicating over a Docker network.

---

# Setup Instructions

## Prerequisites

Ensure the following tools are installed:

Python 3.14.*
uv 0.8.*
Docker Desktop


## Clone the Repository

```bash
git clone https://github.com/jacey111/42kl-data-ai
cd week3
```


## Environment Variables

Create a `.env` file at the root of the project.

Example:

```env
BACKEND_URL=http://backend:8001/chat
GOOGLE_API_KEY=your_google_api_key
OLLAMA_URL=http://host.docker.internal:11434
```

A `.env.example` file is also provided.

Do not commit your .env into Git.


# Running with Docker Compose

Build and start all services:

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:8000
```

Backend:

```text
http://localhost:8001
```

Press Ctrl+C to stop services


# Manual Local Setup

## Frontend

```bash
cd frontend

uv venv
uv sync

uv run uvicorn src.app:app --reload
```


## Backend

```bash
cd backend

uv venv
uv sync

uv run uvicorn src.app:app --reload --port 8001
```

---

# Usage

## Chat Interaction

Users can:

- Type text messages
- Upload resume PDFs
- Send both together

The frontend converts uploaded PDF files into extracted text before forwarding the data to the backend.


## Example Workflow

1. Run both frontend and backend together in different terminal:
uv run uvicorn src.app:app --reload --port 8000
uv run uvicorn src.app:app --reload --port 8001


2. Open:
http://127.0.0.1:8000
OR
http://localhost:8000


3. Upload a PDF resume

4. Enter a prompt such as:
Analyze my resume skill gaps

5. Receive chatbot responses such as:
Detected resume skills:
python, sql, fastapi

Suggested skill gaps:
docker, kubernetes, aws

---

# API / Function Reference

# Frontend

## GET /

Serves the main chat page using Jinja templates.

### Response

HTML page containing:

- Chat history
- PDF file upload
- User input
- Send button

## POST /chat

Receives:

- User message
- Uploaded PDF file

Extracts PDF text and forwards the request to the backend.

### Form Data

| Field   | Type   | Description         |
| ------- | ------ | ------------------- |
| message | string | User chat message   |
| pdf     | file   | Optional PDF resume |

---

# Backend

## POST /chat

Processes user prompts and AI-related logic.

### Expected JSON Payload
{
  "message": "Analyze my resume",
  "resume_text": "Extracted PDF text..."
}

### Example Response
{
  "response": "Detected resume skills: python, sql..."
}

---

# Frontend JavaScript Functions

## sendMessage()

Responsibilities:

- Collect user input
- Handle PDF uploads
- Send requests to `/chat`
- Display chatbot responses dynamically

---

## addMessage()

Responsibilities:

- Render messages into chat history
- Differentiate user and bot message styling

---

# Data / Assumptions

## Data Structure

Frontend and backend communicate using JSON.

Example:
{
  "message": "Analyze my resume",
  "resume_text": "Resume contents..."
}

---

# Assumptions

## PDF Uploads

- PDFs are expected to contain extractable text
- Scanned/image-only PDFs may not extract properly


## Resume Skill Matching

- Skill matching uses deterministic regex matching
- Aliases are manually maintained
- There may still be inconsistent skill naming not covered in aliases


## AI Model Assumptions

- AI responses depend on external/local LLM availability
- Ollama must be running locally if using local models
- Gemini API requires a valid API key


# Data Flow

1. User sends message from browser
2. Frontend receives request
3. Optional PDF text extraction occurs
4. Frontend sends JSON payload to backend
5. Backend processes prompt using Week 2 AI modules
6. Backend returns JSON response
7. Frontend renders chatbot reply

---

# Testing

# Frontend

- Sending text messages
- Uploading PDFs
- Upload cancellation
- Chat rendering
- Scroll behavior
- Enter-to-send functionality


# Backend 

Tested while browsering frontend, and get response from chatbot


# Docker 

- Frontend communicates with backend through Docker network
- `BACKEND_URL=http://backend:8001/chat`
- Containers build and run correctly using:
docker compose up --build


# Deterministic Skill Gap Testing

- Checked aliases in `market_skills` and expanded the `ALIASES` dictionary accordingly
- Ensured all resume skills appear in `resume_skills`
- Ensured skills already detected in resumes do not appear in `gaps`
- Ensured `gaps` only contain skills from `market_skills`
- Reduced duplicate naming issues to minimize false skill gaps

---

# Limitations

- AI responses may occasionally be inconsistent
- Local LLMs may fail under heavy load
- Batch size tuning affects performance and reliability
- Large prompts or large batches may increase response latency, cause invalid JSON responses, or consume excessive RAM or CPU resources
- Scanned PDFs without selectable text may fail extraction
- Very large PDFs may slow response times
- Missing user authentication
- Don't have a database storage for conversations

---

# Architecture Reflection

# Design Choices

Why you chose a microservices architecture (frontend/backend separation). Explain the benefits of containerizing each service with Docker.

**Answer:**
I chose a microservices architecture by separating the frontend and backend to improve modularity and maintainability. The frontend handles the user interface, while the backend processes AI-related tasks. Docker was used to containerize each service so the application can run consistently across different environments and operating systems. Docker Compose also simplifies deployment by allowing both services to run together with a single command.

---

# Trade-offs

What you chose to prioritize (e.g., ease of deployment with Docker Compose vs. performance, simplicity of the chat interface vs. advanced features).

**Answer:**
The project prioritizes simplicity, reproducibility, and ease of deployment over advanced scalability or performance optimizations. Docker Compose makes setup straightforward, but it is less scalable than production orchestration tools. Regex-based skill matching was chosen instead of embedding-based semantic matching to ensure deterministic and reproducible outputs, although this reduces flexibility in understanding similar skill names. The frontend was also kept lightweight using Bootstrap and vanilla JavaScript to reduce complexity.

---

# Improvements

What you would change or extend if given more time (e.g., using a more robust frontend framework, adding a database to store chat history, deploying the application to the cloud).

**Answer:**
Given more time, I would improve the system by adding embedding-based semantic similarity to better detect related skills and reduce manual alias handling. I would also migrate the frontend to a framework such as React for better scalability and user experience. Additional improvements could include storing chat history in a database, implementing streaming AI responses, optimizing PDF processing, and deploying the application to a cloud platform with CI/CD support.
