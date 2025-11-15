"""
FastAPI REST API for Confluence RAG system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rag_engine import RAGEngine
from config import settings

app = FastAPI(
    title="Confluence RAG API",
    description="API for Confluence Knowledge Assistant",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()


# Request/Response models
class IngestRequest(BaseModel):
    page_ids: Optional[List[str]] = None
    space_key: Optional[str] = None
    limit: int = 3


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    chunks_used: List[dict]


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Confluence RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/ingest")
async def ingest_documents(request: IngestRequest):
    """
    Ingest Confluence pages into the vector store.
    
    Provide either page_ids or space_key.
    """
    try:
        if request.page_ids:
            result = rag_engine.ingest_pages(request.page_ids)
        elif request.space_key:
            result = rag_engine.ingest_space(request.space_key, request.limit)
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either page_ids or space_key"
            )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a question.
    """
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        result = rag_engine.query(request.question, request.top_k)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """
    Get system status and health information.
    """
    try:
        status = rag_engine.get_status()
        return status
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pages")
async def get_indexed_pages():
    """
    Get list of indexed pages.
    """
    try:
        stats = rag_engine.vector_store.get_stats()
        
        # Get all documents to extract unique pages
        all_data = rag_engine.vector_store.collection.get()
        
        pages = {}
        if all_data["metadatas"]:
            for metadata in all_data["metadatas"]:
                page_id = metadata.get("page_id")
                if page_id and page_id not in pages:
                    pages[page_id] = {
                        "id": page_id,
                        "title": metadata.get("page_title"),
                        "url": metadata.get("page_url"),
                        "last_modified": metadata.get("last_modified")
                    }
        
        return {
            "pages": list(pages.values()),
            "total_pages": len(pages),
            "total_chunks": stats["total_chunks"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear")
async def clear_vector_store():
    """
    Clear all documents from the vector store.
    Use with caution!
    """
    try:
        rag_engine.vector_store.clear_collection()
        return {"message": "Vector store cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True
    )

