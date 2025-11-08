from sentence_transformers import SentenceTransformer
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers"""

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        Returns: List of floats (embedding vector)
        """
        if self.model is None:
            self._load_model()

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        Returns: List of embeddings
        """
        if self.model is None:
            self._load_model()

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        if self.model is None:
            self._load_model()

        return self.model.get_sentence_embedding_dimension()


# Global embedding service instance
embedding_service = EmbeddingService()
