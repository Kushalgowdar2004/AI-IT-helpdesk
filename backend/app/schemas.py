from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(min_length=2)
    department: str = "Engineering"
    device: str = "Company laptop — Windows"
    has_image: bool = False
    image_base64: Optional[str] = None
    image_media_type: Optional[str] = None

class KBMatchOut(BaseModel):
    kb_article_id: str
    title: str
    score: float
    class Config:
        from_attributes = True

class TicketOut(BaseModel):
    id: str
    title: str
    description: str
    department: str
    device: str
    category: str
    priority: str
    priority_reason: Optional[str]
    status: str
    ai_response: Optional[str]
    resolved_by_ai: bool
    created_at: datetime
    kb_matches: List[KBMatchOut] = []
    class Config:
        from_attributes = True

class MetricsOut(BaseModel):
    total: int
    open: int
    resolved: int
    escalated: int
    auto_resolved_pct: float
    category_breakdown: dict
    priority_breakdown: dict
    avg_kb_matches_per_ticket: float

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)

class ChatResponse(BaseModel):
    reply: str
    kb_matches: List[KBMatchOut] = []
