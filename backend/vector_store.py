"""
Qdrant vector store operations.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
from config import settings
import os
import uuid
import hashlib


class VectorStore:
    """Wrapper for Qdrant operations."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize Qdrant client and collection.
        
        Args:
            collection_name: Name of the collection (defaults to settings)
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        
        # Initialize Qdrant client
        if settings.qdrant_use_memory:
            # In-memory storage (for testing/development)
            self.client = QdrantClient(":memory:")
        else:
            # Persistent storage
            os.makedirs(settings.qdrant_path, exist_ok=True)
            self.client = QdrantClient(path=settings.qdrant_path)
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # Create new collection with cosine distance
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Using existing collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise
    
    def _string_to_uuid(self, text: str) -> str:
        """
        Convert a string ID to a UUID using deterministic hashing.
        
        Args:
            text: String to convert
            
        Returns:
            UUID string
        """
        # Create a deterministic UUID from the string using MD5 hash
        hash_digest = hashlib.md5(text.encode()).hexdigest()
        return str(uuid.UUID(hash_digest))
    
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
            ids: List of unique IDs (will be converted to UUIDs)
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            documents: List of document texts
        """
        try:
            # Create points for Qdrant
            points = []
            for idx, (doc_id, embedding, metadata, document) in enumerate(
                zip(ids, embeddings, metadatas, documents)
            ):
                # Convert string ID to UUID
                uuid_id = self._string_to_uuid(doc_id)
                
                # Add document text and original ID to metadata
                payload = {
                    **metadata, 
                    "document": document,
                    "original_id": doc_id  # Store original string ID
                }
                
                # Create point
                point = PointStruct(
                    id=uuid_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Added {len(ids)} documents to vector store")
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise
    
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
            Dictionary with results in ChromaDB-compatible format
        """
        try:
            # Search for similar vectors
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Convert to ChromaDB-compatible format
            ids = []
            documents = []
            metadatas = []
            distances = []
            
            for result in search_results:
                # Use original_id if available, otherwise use UUID
                original_id = result.payload.get("original_id", str(result.id))
                ids.append(original_id)
                
                # Extract document and metadata
                payload = dict(result.payload)
                document = payload.pop("document", "")
                payload.pop("original_id", None)  # Remove original_id from metadata
                documents.append(document)
                metadatas.append(payload)
                
                # Qdrant returns similarity score, convert to distance
                # For cosine similarity: distance = 1 - similarity
                distances.append(1.0 - result.score)
            
            return {
                "ids": [ids],
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances]
            }
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
            # Delete points with matching page_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="page_id",
                            match=MatchValue(value=page_id)
                        )
                    ]
                )
            )
            print(f"Deleted all chunks from page {page_id}")
        except Exception as e:
            print(f"Error deleting page {page_id}: {e}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            total_chunks = collection_info.points_count
            
            # To get unique pages, we need to scroll through all points
            # For large collections, this might be slow - consider caching
            unique_pages = set()
            offset = None
            batch_size = 100
            
            while True:
                # Scroll through points
                records, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                if not records:
                    break
                
                # Extract unique page IDs
                for record in records:
                    if "page_id" in record.payload:
                        unique_pages.add(record.payload["page_id"])
                
                # Check if we've reached the end
                if next_offset is None:
                    break
                offset = next_offset
            
            return {
                "total_chunks": total_chunks,
                "total_pages": len(unique_pages),
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_chunks": 0, "total_pages": 0, "collection_name": "unknown"}
    
    def get_all_documents(self) -> Dict:
        """
        Get all documents from the collection.

        Returns:
            Dictionary with ids, documents, metadatas in ChromaDB-compatible format
        """
        try:
            ids = []
            documents = []
            metadatas = []

            offset = None
            batch_size = 100

            while True:
                # Scroll through all points
                records, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                if not records:
                    break

                # Extract data from each record
                for record in records:
                    payload = dict(record.payload)
                    original_id = payload.get("original_id", str(record.id))
                    ids.append(original_id)

                    document = payload.pop("document", "")
                    documents.append(document)

                    # Remove internal fields from metadata
                    payload.pop("original_id", None)
                    metadatas.append(payload)

                # Check if we've reached the end
                if next_offset is None:
                    break
                offset = next_offset

            return {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas
            }
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return {"ids": [], "documents": [], "metadatas": []}

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete the collection
            self.client.delete_collection(collection_name=self.collection_name)

            # Recreate it
            self._ensure_collection()
            print("Collection cleared")
        except Exception as e:
            print(f"Error clearing collection: {e}")
