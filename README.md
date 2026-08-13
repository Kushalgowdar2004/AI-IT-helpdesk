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

🧩 Backend Components
main.py

Main FastAPI application.

* It provides API endpoints for:

Health checking
Knowledge-base articles
Ticket creation
Ticket listing
Individual ticket retrieval
AI assistant communication
Helpdesk metrics

The application also initializes the database and builds the knowledge-base index during startup.

models.py

Contains SQLAlchemy database models for the application's persistent data.

* The database stores information such as:

Tickets
Knowledge-base articles
Ticket/knowledge-base relationships
schemas.py

Contains Pydantic request and response schemas used to validate API requests and responses.

database.py

* Handles:

SQLite database configuration
SQLAlchemy engine
Database sessions
Database dependencies
ai_pipeline.py

* Contains the AI processing pipeline used for:

Ticket analysis
Categorization
Priority determination
Troubleshooting response generation
AI-assisted resolution
rag.py

Implements the knowledge retrieval functionality.

The RAG system retrieves relevant knowledge-base articles before the AI processing stage.

seed_kb.py

Loads and seeds the IT knowledge-base content into the database.

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

📌 Current Project Status
Implemented
 Responsive IT Helpdesk dashboard
 AI Assistant interface
 Suggested IT questions
 Ticket submission
 Ticket management
 Ticket status handling
 AI-assisted ticket analysis
 Priority classification
 Knowledge-base retrieval
 53 knowledge-base articles
 SQLite database
 SQLAlchemy ORM
 FastAPI backend
 REST APIs
 Swagger API documentation
 Netlify frontend deployment
 Render backend deployment
 FastAPI backend
 REST APIs
 Swagger API documentation
 Netlify frontend deployment
 Render backend deployment
