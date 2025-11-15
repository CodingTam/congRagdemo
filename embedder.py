"""
Gemini embedding generation using Google Cloud Vertex AI.
"""

from google import genai
from typing import List
from config import settings


class GeminiEmbedder:
    """Wrapper for Gemini embedding generation."""
    
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
        self.model = settings.embedding_model
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                # Return zero vector on failure
                embeddings.append([0.0] * 768)
        
        return embeddings

