"""
ChromaDB vector store operations.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from config import settings
import os


class VectorStore:
    """Wrapper for ChromaDB operations."""
    
    def __init__(self, collection_name: str = "confluence_docs"):
        # Create data directory if it doesn't exist
        os.makedirs(settings.chromadb_path, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=settings.chromadb_path,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        documents: List[str]
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            ids: List of unique IDs
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            documents: List of document texts
        """
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            print(f"Added {len(ids)} documents to vector store")
        except Exception as e:
            print(f"Error adding documents: {e}")
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 4
    ) -> Dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            Dictionary with results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def delete_by_page_id(self, page_id: str) -> None:
        """
        Delete all chunks from a specific page.
        
        Args:
            page_id: Confluence page ID
        """
        try:
            # Query for all documents with this page_id
            results = self.collection.get(
                where={"page_id": page_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Deleted {len(results['ids'])} chunks from page {page_id}")
        except Exception as e:
            print(f"Error deleting page {page_id}: {e}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            count = self.collection.count()
            
            # Get unique page IDs
            all_data = self.collection.get()
            unique_pages = set()
            if all_data["metadatas"]:
                for metadata in all_data["metadatas"]:
                    if "page_id" in metadata:
                        unique_pages.add(metadata["page_id"])
            
            return {
                "total_chunks": count,
                "total_pages": len(unique_pages),
                "collection_name": self.collection.name
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_chunks": 0, "total_pages": 0, "collection_name": "unknown"}
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Collection cleared")
        except Exception as e:
            print(f"Error clearing collection: {e}")

