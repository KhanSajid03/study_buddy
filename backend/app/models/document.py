from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base
from pgvector.sqlalchemy import Vector


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size = Column(BigInteger, nullable=False)  # in bytes
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)  # 0: pending, 1: processing, 2: completed, -1: failed

    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(filename='{self.filename}', user_id={self.user_id})>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)

    # Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(doc_id={self.document_id}, chunk_index={self.chunk_index})>"
