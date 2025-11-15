"""
RAG engine for orchestrating retrieval and generation.
"""

from typing import List, Dict, Optional
from google import genai
from config import settings
from confluence_client import ConfluenceClient
from embedder import GeminiEmbedder
from vector_store import VectorStore
from utils import chunk_text, create_chunk_metadata, clean_text


class RAGEngine:
    """Main RAG orchestration engine."""
    
    def __init__(self):
        self.confluence_client = ConfluenceClient()
        self.embedder = GeminiEmbedder()
        self.vector_store = VectorStore()
        self.generation_client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location
        )
    
    def ingest_page(self, page_id: str) -> Dict:
        """
        Ingest a single Confluence page.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Dictionary with ingestion results
        """
        # Fetch page content
        page_data = self.confluence_client.get_page_content(page_id)
        if not page_data:
            return {
                "success": False,
                "error": f"Failed to fetch page {page_id}"
            }
        
        content = page_data["content"]
        metadata = page_data["metadata"]
        
        # Clean text
        content = clean_text(content)
        
        # Chunk the content
        chunks = chunk_text(
            content,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
        
        if not chunks:
            return {
                "success": False,
                "error": f"No content to chunk for page {page_id}"
            }
        
        # Generate embeddings
        embeddings = self.embedder.generate_embeddings_batch(chunks)
        
        # Prepare data for vector store
        ids = [f"page_{page_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            create_chunk_metadata(chunk, i, metadata)
            for i, chunk in enumerate(chunks)
        ]
        
        # Store in vector database
        self.vector_store.add_documents(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )
        
        return {
            "success": True,
            "page_id": page_id,
            "page_title": metadata["page_title"],
            "page_url": metadata["page_url"],
            "chunks_created": len(chunks)
        }
    
    def ingest_pages(self, page_ids: List[str]) -> Dict:
        """
        Ingest multiple Confluence pages.
        
        Args:
            page_ids: List of Confluence page IDs
            
        Returns:
            Dictionary with ingestion results
        """
        results = []
        total_chunks = 0
        
        for page_id in page_ids:
            result = self.ingest_page(page_id)
            results.append(result)
            if result["success"]:
                total_chunks += result["chunks_created"]
        
        successful = [r for r in results if r["success"]]
        
        return {
            "status": "success" if successful else "failed",
            "pages_processed": len(successful),
            "chunks_created": total_chunks,
            "pages": results
        }
    
    def ingest_space(self, space_key: str, limit: int = 10) -> Dict:
        """
        Ingest pages from a Confluence space.
        
        Args:
            space_key: Confluence space key
            limit: Maximum number of pages to ingest
            
        Returns:
            Dictionary with ingestion results
        """
        pages = self.confluence_client.get_pages_from_space(space_key, limit)
        if not pages:
            return {
                "status": "failed",
                "error": f"No pages found in space {space_key}"
            }
        
        page_ids = [page["id"] for page in pages]
        return self.ingest_pages(page_ids)
    
    def query(self, question: str, top_k: Optional[int] = None) -> Dict:
        """
        Query the RAG system.
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve (defaults to settings)
            
        Returns:
            Dictionary with answer and sources
        """
        if top_k is None:
            top_k = settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(question)
        if not query_embedding:
            return {
                "answer": "Sorry, I encountered an error processing your question.",
                "sources": [],
                "chunks_used": []
            }
        
        # Retrieve similar chunks
        results = self.vector_store.query(query_embedding, top_k=top_k)
        
        if not results["documents"][0]:
            return {
                "answer": "I couldn't find relevant information in our Confluence documentation to answer your question. Could you rephrase or ask about a related topic?",
                "sources": [],
                "chunks_used": []
            }
        
        # Extract chunks and metadata
        chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        # Build context from chunks
        context_parts = []
        for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
            context_parts.append(
                f"[Source {i+1}: {metadata['page_title']}]\n{chunk}\n"
            )
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = self._build_prompt(question, context)
        
        # Generate answer
        try:
            response = self.generation_client.models.generate_content(
                model=settings.generation_model,
                contents=prompt
            )
            answer = response.text
        except Exception as e:
            print(f"Error generating answer: {e}")
            answer = "Sorry, I encountered an error generating the answer."
        
        # Prepare sources (deduplicate by page)
        sources = {}
        for metadata, distance in zip(metadatas, distances):
            page_id = metadata["page_id"]
            if page_id not in sources:
                sources[page_id] = {
                    "page_title": metadata["page_title"],
                    "page_url": metadata["page_url"],
                    "relevance_score": round(1 - distance, 2)  # Convert distance to similarity
                }
        
        # Prepare chunks used
        chunks_used = [
            {
                "text": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "page_title": metadata["page_title"]
            }
            for chunk, metadata in zip(chunks, metadatas)
        ]
        
        return {
            "answer": answer,
            "sources": list(sources.values()),
            "chunks_used": chunks_used
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build the prompt for generation.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a Global Team Knowledge Assistant powered by our internal Confluence.
Use ONLY the following context to answer the question.
Always provide detailed, step-by-step answers when applicable.
Format steps as numbered lists for clarity.

Context from Confluence:
{context}

User Question:
{question}

Instructions:
- Base your answer ONLY on the provided context
- If the context doesn't contain enough information, say so clearly
- Include specific details like commands, URLs, or configuration values when present
- Use numbered steps for procedural information
- Cite which Confluence page(s) you're referencing

Answer:"""
        
        return prompt
    
    def get_status(self) -> Dict:
        """
        Get system status.
        
        Returns:
            Dictionary with status information
        """
        confluence_connected = self.confluence_client.test_connection()
        vector_stats = self.vector_store.get_stats()
        
        return {
            "status": "healthy" if confluence_connected else "degraded",
            "confluence_connected": confluence_connected,
            "vector_db_loaded": True,
            "documents_indexed": vector_stats["total_pages"],
            "total_chunks": vector_stats["total_chunks"]
        }

