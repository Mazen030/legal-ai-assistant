from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    page_count: int
    chunk_count: int
    message: str


class QueryRequest(BaseModel):
    session_id: str
    question: str = Field(..., min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    sources: list[str] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)


class SessionInfo(BaseModel):
    session_id: str
    filename: str
    created_at: datetime
    message_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
