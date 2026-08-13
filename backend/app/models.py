import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

def gen_ticket_id():
    return "IT-" + uuid.uuid4().hex[:6].upper()

class KBArticle(Base):
    __tablename__ = "kb_articles"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    body = Column(Text, nullable=False)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=gen_ticket_id)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    device = Column(String, nullable=False)
    has_image = Column(Boolean, default=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    priority_reason = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")
    ai_response = Column(Text, nullable=True)
    resolved_by_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    kb_matches = relationship("TicketKBMatch", back_populates="ticket", cascade="all, delete-orphan")

class TicketKBMatch(Base):
    __tablename__ = "ticket_kb_matches"
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    ticket_id = Column(String, ForeignKey("tickets.id"))
    kb_article_id = Column(String, ForeignKey("kb_articles.id"))
    score = Column(Float, default=0.0)
    ticket = relationship("Ticket", back_populates="kb_matches")
    article = relationship("KBArticle")
    @property
    def title(self):
        return self.article.title if self.article else ""

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
