"""
Hybrid Search Module for Confluence RAG System

This module implements multiple search strategies:
1. Semantic search using embeddings
2. Keyword search using TF-IDF
3. Query expansion and reformulation
4. Fuzzy matching for typo tolerance
5. Automatic fallback strategies
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import chromadb


class HybridSearch:
    """
    Implements hybrid search combining semantic and keyword-based retrieval.
    """

    def __init__(self, vector_store, embedder):
        """
        Initialize hybrid search with vector store and embedder.

        Args:
            vector_store: ChromaDB vector store instance
            embedder: Gemini embedder instance
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.documents = []
        self.metadata_list = []

    def build_keyword_index(self):
        """
        Build TF-IDF index for keyword search from all documents in vector store.
        """
        try:
            # Get all documents from vector store
            all_data = self.vector_store.collection.get()

            if not all_data["documents"]:
                print("No documents found in vector store for keyword indexing")
                return

            self.documents = all_data["documents"]
            self.metadata_list = all_data["metadatas"]

            # Build TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),  # Include unigrams, bigrams, and trigrams
                min_df=1,
                max_df=0.95
            )

            # Fit and transform documents
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.documents)
            print(f"Built TF-IDF index for {len(self.documents)} documents")

        except Exception as e:
            print(f"Error building keyword index: {e}")

    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with variations and related terms.

        Args:
            query: Original user query

        Returns:
            List of expanded queries
        """
        expanded_queries = [query]

        # Add question variations
        question_words = ["how to", "what is", "where is", "when to", "why"]
        base_query = query.lower()

        # Remove question words if present
        for qw in question_words:
            if base_query.startswith(qw):
                base_query = base_query[len(qw):].strip()
                break

        # Generate variations
        if not any(query.lower().startswith(qw) for qw in question_words):
            # Add question forms
            expanded_queries.append(f"how to {base_query}")
            expanded_queries.append(f"what is {base_query}")
        else:
            # Try without question words
            expanded_queries.append(base_query)

        # Add keyword-focused versions
        # Extract key terms (nouns and verbs)
        key_terms = self._extract_key_terms(query)
        if key_terms:
            expanded_queries.append(" ".join(key_terms))

        # Add synonym replacements for common terms
        synonyms = {
            "install": ["setup", "configure", "deploy", "installation"],
            "python": ["Python", "python3", "py"],
            "run": ["execute", "start", "launch", "invoke"],
            "create": ["make", "build", "generate", "initialize"],
            "delete": ["remove", "destroy", "clear", "uninstall"],
            "update": ["upgrade", "modify", "change", "patch"],
            "fix": ["resolve", "repair", "debug", "troubleshoot"],
            "error": ["issue", "problem", "exception", "bug", "failure"],
            "guide": ["tutorial", "documentation", "instructions", "steps"],
            "access": ["login", "authenticate", "connect", "permission"],
            "configure": ["settings", "options", "parameters", "config"],
            "deploy": ["release", "publish", "rollout"],
            "setup": ["configuration", "initialize", "prepare"],
            "connection": ["connectivity", "link", "integration"],
            "page": ["document", "article", "wiki"],
            "team": ["group", "department", "organization"],
            "project": ["repository", "workspace", "codebase"],
            "version": ["release", "build", "edition"],
            "environment": ["env", "server", "platform", "system"]
        }

        # Generate queries with synonyms
        for word, syns in synonyms.items():
            if word in query.lower():
                for syn in syns[:2]:  # Limit to 2 synonyms
                    expanded_queries.append(query.lower().replace(word, syn))

        return list(set(expanded_queries))[:5]  # Return up to 5 unique variations

    def _extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key terms from query (simple implementation).

        Args:
            query: User query

        Returns:
            List of key terms
        """
        # Remove common words
        stop_words = {
            "the", "is", "at", "which", "on", "a", "an", "as", "are", "was",
            "were", "been", "be", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can",
            "shall", "to", "of", "in", "for", "with", "by", "from", "about"
        }

        words = query.lower().split()
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        return key_terms

    def keyword_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Perform keyword-based search using TF-IDF.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (index, score) tuples
        """
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            print("TF-IDF index not built. Building now...")
            self.build_keyword_index()

        if self.tfidf_vectorizer is None:
            return []

        try:
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])

            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]

            # Return indices with scores
            results = [(idx, similarities[idx]) for idx in top_indices if similarities[idx] > 0]
            return results

        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []

    def semantic_search(self, query_embedding: List[float], top_k: int = 10) -> Dict:
        """
        Perform semantic search using embeddings.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            ChromaDB query results
        """
        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    def hybrid_query(self, question: str, top_k: int = 5,
                    semantic_weight: float = 0.7,
                    keyword_weight: float = 0.3,
                    similarity_threshold: float = 0.3) -> Dict:
        """
        Perform hybrid search combining semantic and keyword search.

        Args:
            question: User question
            top_k: Number of results to return
            semantic_weight: Weight for semantic search scores
            keyword_weight: Weight for keyword search scores
            similarity_threshold: Minimum similarity score to include result

        Returns:
            Combined search results
        """
        # Expand query
        expanded_queries = self.expand_query(question)
        print(f"Expanded queries: {expanded_queries}")

        all_results = {}

        for query in expanded_queries:
            # Generate embedding for semantic search
            query_embedding = self.embedder.generate_embedding(query)

            # Perform semantic search
            semantic_results = self.semantic_search(query_embedding, top_k * 2)

            # Perform keyword search
            keyword_results = self.keyword_search(query, top_k * 2)

            # Combine results
            combined = self._combine_results(
                semantic_results,
                keyword_results,
                semantic_weight,
                keyword_weight
            )

            # Merge with all results
            for doc_id, score_data in combined.items():
                if doc_id not in all_results or score_data["score"] > all_results[doc_id]["score"]:
                    all_results[doc_id] = score_data

        # Filter by threshold and sort by score
        filtered_results = {
            doc_id: data for doc_id, data in all_results.items()
            if data["score"] >= similarity_threshold
        }

        # If no results meet threshold, use fallback strategy
        if not filtered_results and all_results:
            print(f"No results above threshold {similarity_threshold}, using top results anyway")
            # Take top results regardless of threshold
            sorted_items = sorted(all_results.items(), key=lambda x: x[1]["score"], reverse=True)
            filtered_results = dict(sorted_items[:top_k])

        # Sort by score and format output
        sorted_results = sorted(filtered_results.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]

        # Format as ChromaDB-style results
        ids = [[]]
        documents = [[]]
        metadatas = [[]]
        distances = [[]]

        for doc_id, data in sorted_results:
            ids[0].append(doc_id)
            documents[0].append(data["document"])
            metadatas[0].append(data["metadata"])
            distances[0].append(1 - data["score"])  # Convert similarity to distance

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances
        }

    def _combine_results(self, semantic_results: Dict, keyword_results: List[Tuple[int, float]],
                        semantic_weight: float, keyword_weight: float) -> Dict:
        """
        Combine semantic and keyword search results.

        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            semantic_weight: Weight for semantic scores
            keyword_weight: Weight for keyword scores

        Returns:
            Combined results dictionary
        """
        combined = {}

        # Process semantic results
        if semantic_results["ids"][0]:
            for i, doc_id in enumerate(semantic_results["ids"][0]):
                score = 1 - semantic_results["distances"][0][i]  # Convert distance to similarity
                combined[doc_id] = {
                    "document": semantic_results["documents"][0][i],
                    "metadata": semantic_results["metadatas"][0][i],
                    "score": score * semantic_weight,
                    "semantic_score": score,
                    "keyword_score": 0
                }

        # Process keyword results
        for idx, keyword_score in keyword_results:
            if idx < len(self.documents):
                # Get document ID from vector store
                all_data = self.vector_store.collection.get()
                if idx < len(all_data["ids"]):
                    doc_id = all_data["ids"][idx]

                    if doc_id in combined:
                        # Update existing entry
                        combined[doc_id]["keyword_score"] = keyword_score
                        combined[doc_id]["score"] += keyword_score * keyword_weight
                    else:
                        # Add new entry
                        combined[doc_id] = {
                            "document": self.documents[idx],
                            "metadata": self.metadata_list[idx],
                            "score": keyword_score * keyword_weight,
                            "semantic_score": 0,
                            "keyword_score": keyword_score
                        }

        return combined

    def fallback_search(self, question: str, top_k: int = 5) -> Dict:
        """
        Fallback search strategy when primary search fails.
        Uses more aggressive query expansion and lower thresholds.

        Args:
            question: User question
            top_k: Number of results to return

        Returns:
            Search results
        """
        print("Using fallback search strategy...")

        # Extract individual keywords
        key_terms = self._extract_key_terms(question)

        all_results = {}

        # Search for each key term individually
        for term in key_terms:
            results = self.keyword_search(term, top_k)
            for idx, score in results:
                if idx < len(self.documents):
                    all_data = self.vector_store.collection.get()
                    if idx < len(all_data["ids"]):
                        doc_id = all_data["ids"][idx]
                        if doc_id not in all_results or score > all_results[doc_id]["score"]:
                            all_results[doc_id] = {
                                "document": self.documents[idx],
                                "metadata": self.metadata_list[idx],
                                "score": score
                            }

        # Sort and format results
        sorted_results = sorted(all_results.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]

        ids = [[]]
        documents = [[]]
        metadatas = [[]]
        distances = [[]]

        for doc_id, data in sorted_results:
            ids[0].append(doc_id)
            documents[0].append(data["document"])
            metadatas[0].append(data["metadata"])
            distances[0].append(1 - data["score"])

        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances
        }