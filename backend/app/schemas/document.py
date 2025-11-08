from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    file_type: str
    file_size: int
    upload_date: datetime
    processed: int
    chunk_count: Optional[int] = 0

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    chunk_text: str
    page_number: Optional[int]

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[int]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str


class ChatMessage(BaseModel):
    role: str
    content: str
