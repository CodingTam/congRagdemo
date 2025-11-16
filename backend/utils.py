"""
Utility functions for text processing and chunking.
"""

from typing import List, Dict
import re


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Split text into overlapping chunks.
    Strategy: Split by paragraphs first, then by sentences if needed.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters (approximates tokens)
        overlap: Overlap size in characters
        
    Returns:
        List of text chunks
    """
    if not text or len(text) == 0:
        return []
    
    # First, split by paragraphs (double newline or single newline)
    paragraphs = re.split(r'\n\s*\n|\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph keeps us under chunk_size, add it
        if len(current_chunk) + len(para) + 1 <= chunk_size:
            if current_chunk:
                current_chunk += "\n" + para
            else:
                current_chunk = para
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk)
            
            # If paragraph itself is larger than chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = split_into_sentences(para)
                temp_chunk = ""
                
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) + 1 <= chunk_size:
                        if temp_chunk:
                            temp_chunk += " " + sentence
                        else:
                            temp_chunk = sentence
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = sentence
                
                current_chunk = temp_chunk
            else:
                current_chunk = para
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    # Apply overlap between chunks
    if overlap > 0 and len(chunks) > 1:
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            # Get overlap from previous chunk
            prev_chunk = chunks[i - 1]
            overlap_text = prev_chunk[-overlap:] if len(prev_chunk) > overlap else prev_chunk
            
            # Prepend to current chunk
            overlapped_chunk = overlap_text + "\n" + chunks[i]
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    return chunks


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (can be improved with nltk if needed)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def create_chunk_metadata(
    chunk_text: str,
    chunk_index: int,
    page_metadata: Dict
) -> Dict:
    """
    Create metadata for a chunk.
    
    Args:
        chunk_text: The chunk text
        chunk_index: Index of the chunk
        page_metadata: Metadata from the source page
        
    Returns:
        Dictionary with chunk metadata
    """
    return {
        "page_id": page_metadata.get("page_id"),
        "page_title": page_metadata.get("page_title"),
        "page_url": page_metadata.get("page_url"),
        "chunk_text": chunk_text,
        "chunk_index": chunk_index,
        "last_modified": page_metadata.get("last_modified"),
        "space_key": page_metadata.get("space_key"),
        "space_name": page_metadata.get("space_name")
    }


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')
    
    return text.strip()

