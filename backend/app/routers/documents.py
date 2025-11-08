from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path

from app.models.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse
from app.utils.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/documents", tags=["Documents"])

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def get_file_type(filename: str) -> str:
    """Determine file type from filename"""
    extension = filename.lower().split(".")[-1]
    if extension == "pdf":
        return "pdf"
    elif extension in ["docx", "doc"]:
        return "docx"
    elif extension == "txt":
        return "txt"
    else:
        raise ValueError(f"Unsupported file type: {extension}")


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and process a document"""
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB}MB",
        )

    # Check user's total storage
    user_total_storage = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .with_entities(db.func.sum(Document.file_size))
        .scalar()
        or 0
    )

    max_storage_per_user = 3 * 1024 * 1024 * 1024  # 3GB
    if user_total_storage + file_size > max_storage_per_user:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Storage limit exceeded (3GB per user)",
        )

    # Validate file type
    try:
        file_type = get_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Create user directory
    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    Path(user_dir).mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = os.path.join(user_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}",
        )

    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        processed=1,  # Processing
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Process document in background (for production, use Celery or similar)
    try:
        processor = DocumentProcessor()
        chunks = processor.process_document(file_path, file_type)

        # Generate embeddings and store chunks
        for chunk_text, page_num, chunk_idx in chunks:
            # Generate embedding
            embedding = embedding_service.embed_text(chunk_text)

            # Create chunk
            chunk = DocumentChunk(
                document_id=document.id,
                user_id=current_user.id,
                chunk_index=chunk_idx,
                chunk_text=chunk_text,
                page_number=page_num,
                embedding=embedding,
            )
            db.add(chunk)

        # Update document status
        document.processed = 2  # Completed
        db.commit()

    except Exception as e:
        # Mark as failed
        document.processed = -1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )

    # Get chunk count
    chunk_count = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .count()
    )

    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        upload_date=document.upload_date,
        processed=document.processed,
        chunk_count=chunk_count,
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all documents for the current user"""
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.upload_date.desc())
        .all()
    )

    response = []
    for doc in documents:
        chunk_count = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == doc.id)
            .count()
        )
        response.append(
            DocumentResponse(
                id=doc.id,
                user_id=doc.user_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                upload_date=doc.upload_date,
                processed=doc.processed,
                chunk_count=chunk_count,
            )
        )

    return response


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific document"""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    chunk_count = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .count()
    )

    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        upload_date=document.upload_date,
        processed=document.processed,
        chunk_count=chunk_count,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document"""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file from filesystem
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    # Delete from database (chunks will be cascade deleted)
    db.delete(document)
    db.commit()

    return None
