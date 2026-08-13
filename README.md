# AI IT Helpdesk — Improved Local-First Full Stack

A responsive employee helpdesk portal backed by FastAPI, SQLAlchemy, SQLite, TF-IDF/cosine RAG, and a deterministic local assistant. Anthropic is optional and disabled by default.

## Run on Windows

### Backend
```powershell
cd backend
py -3.10 -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend
Open a second terminal:
```powershell
cd frontend
python -m http.server 5500
```
Open `http://localhost:5500`.

API docs: `http://127.0.0.1:8000/docs`

## AI mode

The assistant is local-first. `ENABLE_ANTHROPIC=false` means no external API call is made. The assistant uses the seeded KB and TF-IDF + cosine similarity. Set `ENABLE_ANTHROPIC=true` and provide a valid key only if you explicitly want Claude.

## Main features
- Full-screen responsive dashboard
- Ticket creation with category/priority/status and RAG match trail
- Local-first AI chat with greetings, grounded troubleshooting, and follow-up context
- Knowledge-base view
- Optional screenshot upload support through the existing ticket API
- FastAPI Swagger docs
- SQLite by default


## Expanded knowledge base

The improved version contains 53 KB articles across Network, Hardware, Windows & OS, Software, Access & Accounts, Email & Collaboration, and Security. Existing databases are upgraded by inserting only missing KB IDs, so restarting the backend does not duplicate existing articles.
