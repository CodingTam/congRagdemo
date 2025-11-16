"""
Configuration management for Confluence RAG system.
Loads environment variables and provides centralized settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # On-Premises Confluence
    confluence_base_url: str
    confluence_api_token: str
    
    # Google Cloud / Vertex AI
    google_cloud_project: str = "divine-camera-478315-s6"
    google_cloud_location: str = "us-central1"
    
    # Vector Database Settings (Qdrant)
    qdrant_path: str = "./data/qdrant"
    qdrant_collection_name: str = "confluence_docs"
    qdrant_use_memory: bool = False  # Set to True for in-memory storage
    embedding_dimension: int = 768  # Gemini text-embedding-004 dimension
    
    # Application Settings
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k_results: int = 8  # Increased from 4 for better context coverage
    
    # API Settings
    backend_port: int = 8000
    frontend_port: int = 3000
    
    # Model Settings
    generation_model: str = "gemini-2.0-flash-exp"
    embedding_model: str = "text-embedding-004"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

