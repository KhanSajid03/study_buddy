from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.document import QueryRequest, QueryResponse
from app.utils.auth import get_current_user
from app.services.rag_service import rag_service

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def query_documents(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Query documents using RAG"""
    try:
        result = await rag_service.query(
            db=db,
            user=current_user,
            query=query_request.query,
            top_k=query_request.top_k,
            document_ids=query_request.document_ids,
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            query=result["query"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )
