from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .database import Base, engine, SessionLocal, get_db
from .rag import kb_index
from .seed_kb import seed_kb
from .ai_pipeline import analyze_ticket, chat_reply

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI IT Helpdesk API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_kb(db)
        kb_index.build(db.query(models.KBArticle).all())
        print(f"Knowledge base index built with {len(kb_index.articles)} articles.")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "ai_mode": "anthropic" if __import__('app.ai_pipeline', fromlist=['ANTHROPIC_API_KEY']).ANTHROPIC_API_KEY else "local-rag"}

@app.get("/api/kb")
def list_kb(db: Session = Depends(get_db)):
    return [{"id": a.id, "title": a.title, "category": a.category, "body": a.body} for a in db.query(models.KBArticle).all()]

@app.post("/api/tickets", response_model=schemas.TicketOut)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    matches = kb_index.retrieve(payload.title + " " + payload.description, k=3)
    result = analyze_ticket(payload.title, payload.description, payload.department, payload.device, matches, payload.image_base64, payload.image_media_type)
    resolved = bool(result.get("resolved"))
    priority = result.get("priority", "Medium")
    status = "resolved" if resolved else ("escalated" if priority == "High" else "open")
    ticket = models.Ticket(
        title=payload.title, description=payload.description, department=payload.department, device=payload.device,
        has_image=payload.has_image, category=result.get("category", "Other"), priority=priority,
        priority_reason=result.get("priority_reason"), status=status, ai_response=result.get("response"), resolved_by_ai=resolved,
    )
    db.add(ticket); db.flush()
    for m in matches:
        db.add(models.TicketKBMatch(ticket_id=ticket.id, kb_article_id=m.id, score=m.score))
    db.commit(); db.refresh(ticket)
    return ticket

@app.get("/api/tickets", response_model=list[schemas.TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).all()

@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/api/metrics", response_model=schemas.MetricsOut)
def metrics(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all(); total = len(tickets)
    open_ct = sum(t.status == "open" for t in tickets); resolved_ct = sum(t.status == "resolved" for t in tickets); escalated_ct = sum(t.status == "escalated" for t in tickets)
    cats = {}; priorities = {}
    for t in tickets:
        cats[t.category] = cats.get(t.category, 0) + 1; priorities[t.priority] = priorities.get(t.priority, 0) + 1
    match_count = db.query(func.count(models.TicketKBMatch.id)).scalar() or 0
    return schemas.MetricsOut(total=total, open=open_ct, resolved=resolved_ct, escalated=escalated_ct,
        auto_resolved_pct=round(resolved_ct / total * 100, 1) if total else 0, category_breakdown=cats,
        priority_breakdown=priorities, avg_kb_matches_per_ticket=round(match_count / total, 2) if total else 0)

@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == payload.session_id).order_by(models.ChatMessage.created_at.asc()).all()
    history_dict = [{"role": h.role, "content": h.content} for h in history]
    history_dict.append({"role": "user", "content": payload.message})
    # Use recent conversation context for retrieval so follow-up questions stay grounded.
    retrieval_query = " ".join(m["content"] for m in history_dict[-4:] if m["role"] == "user")
    matches = kb_index.retrieve(retrieval_query, k=3)
    reply = chat_reply(history_dict, matches)
    db.add(models.ChatMessage(session_id=payload.session_id, role="user", content=payload.message))
    db.add(models.ChatMessage(session_id=payload.session_id, role="assistant", content=reply))
    db.commit()
    return schemas.ChatResponse(reply=reply, kb_matches=[{"kb_article_id": m.id, "title": m.title, "score": m.score} for m in matches])
