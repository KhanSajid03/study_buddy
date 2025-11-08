from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import httpx
import os
from dotenv import load_dotenv

from app.models.document import DocumentChunk
from app.models.user import User
from app.services.embedding_service import embedding_service

load_dotenv()


class RAGService:
    """Service for RAG query processing"""

    def __init__(self):
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")

    async def retrieve_relevant_chunks(
        self,
        db: Session,
        user_id: int,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[Dict]:
        """
        Retrieve relevant document chunks using vector similarity search
        """
        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)

        # Build filter conditions
        filters = [DocumentChunk.user_id == user_id]
        if document_ids:
            filters.append(DocumentChunk.document_id.in_(document_ids))

        # Query using pgvector's cosine distance
        # Note: Using <=> operator for cosine distance (1 - cosine similarity)
        chunks = (
            db.query(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .filter(and_(*filters))
            .filter(DocumentChunk.embedding.isnot(None))
            .order_by("distance")
            .limit(top_k)
            .all()
        )

        # Format results
        results = []
        for chunk, distance in chunks:
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "text": chunk.chunk_text,
                    "page_number": chunk.page_number,
                    "similarity": 1 - distance,  # Convert distance to similarity
                }
            )

        return results

    def build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            page_info = f", Page {chunk['page_number']}" if chunk["page_number"] else ""
            context_parts.append(
                f"[Source {i}]{page_info}:\n{chunk['text']}\n"
            )

        return "\n".join(context_parts)

    def build_prompt(self, query: str, context: str) -> str:
        """Build the prompt for the LLM"""
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context.

Context from documents:
{context}

User question: {query}

Instructions:
1. Answer the question using ONLY the information from the provided context
2. Include citations using [Source X] format when referencing specific information
3. If the context doesn't contain enough information to answer the question, say so
4. Be concise and accurate

Answer:"""
        return prompt

    async def call_openai(
        self, api_key: str, model: str, prompt: str
    ) -> str:
        """Call OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def call_anthropic(
        self, api_key: str, model: str, prompt: str
    ) -> str:
        """Call Anthropic API"""
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
            data = {
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"]
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def call_custom_endpoint(
        self, endpoint: str, api_key: Optional[str], model: str, prompt: str
    ) -> str:
        """Call custom LLM endpoint (OpenAI-compatible)"""
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{endpoint}/v1/chat/completions",
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Custom endpoint error: {str(e)}")

    async def generate_answer(
        self, user: User, prompt: str
    ) -> str:
        """Generate answer using user's configured LLM"""
        provider = user.preferred_llm_provider or self.default_llm_provider
        model = user.preferred_model or self.default_model

        if provider == "openai":
            api_key = user.openai_api_key
            if not api_key:
                raise Exception("OpenAI API key not configured")
            return await self.call_openai(api_key, model, prompt)

        elif provider == "anthropic":
            api_key = user.anthropic_api_key
            if not api_key:
                raise Exception("Anthropic API key not configured")
            return await self.call_anthropic(api_key, model, prompt)

        elif provider == "custom":
            endpoint = user.custom_llm_endpoint
            api_key = user.custom_llm_api_key
            if not endpoint:
                raise Exception("Custom LLM endpoint not configured")
            return await self.call_custom_endpoint(endpoint, api_key, model, prompt)

        else:
            raise Exception(f"Unsupported LLM provider: {provider}")

    async def query(
        self,
        db: Session,
        user: User,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> Dict:
        """
        Process RAG query
        Returns: Dict with answer and sources
        """
        # Retrieve relevant chunks
        chunks = await self.retrieve_relevant_chunks(
            db, user.id, query, top_k, document_ids
        )

        if not chunks:
            return {
                "answer": "I don't have any relevant documents to answer this question. Please upload documents first.",
                "sources": [],
                "query": query,
            }

        # Build context and prompt
        context = self.build_context(chunks)
        prompt = self.build_prompt(query, context)

        # Generate answer
        answer = await self.generate_answer(user, prompt)

        # Format sources
        sources = []
        for i, chunk in enumerate(chunks, 1):
            sources.append(
                {
                    "source_number": i,
                    "document_id": chunk["document_id"],
                    "page_number": chunk["page_number"],
                    "text_snippet": chunk["text"][:200] + "..."
                    if len(chunk["text"]) > 200
                    else chunk["text"],
                    "similarity": round(chunk["similarity"], 4),
                }
            )

        return {"answer": answer, "sources": sources, "query": query}


# Global RAG service instance
rag_service = RAGService()
