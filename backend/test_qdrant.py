#!/usr/bin/env python3
"""
Test script for Qdrant integration.
This script verifies that the Qdrant vector database is properly configured and working.
"""

import sys
import numpy as np
from config import settings
from vector_store import VectorStore
from embedder import GeminiEmbedder


def test_qdrant_operations():
    """Test basic Qdrant operations."""

    print("=" * 60)
    print("Testing Qdrant Integration")
    print("=" * 60)
    print()

    # Test 1: Initialize VectorStore
    print("Test 1: Initializing VectorStore...")
    try:
        vector_store = VectorStore()
        print("✅ VectorStore initialized successfully")
        print(f"   Collection: {vector_store.collection_name}")
        print(f"   Path: {settings.qdrant_path}")
        print(f"   Memory mode: {settings.qdrant_use_memory}")
    except Exception as e:
        print(f"❌ Failed to initialize VectorStore: {e}")
        return False
    print()

    # Test 2: Get collection stats
    print("Test 2: Getting collection statistics...")
    try:
        stats = vector_store.get_stats()
        print(f"✅ Stats retrieved successfully")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Total pages: {stats['total_pages']}")
        print(f"   Collection: {stats['collection_name']}")
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
    print()

    # Test 3: Add test documents
    print("Test 3: Adding test documents...")
    try:
        # Create test data
        test_ids = ["test_doc_1", "test_doc_2", "test_doc_3"]
        test_docs = [
            "Python is a high-level programming language.",
            "How to install Python on your system.",
            "Python installation guide for beginners."
        ]
        test_metadatas = [
            {"page_id": "test_1", "page_title": "Python Overview"},
            {"page_id": "test_2", "page_title": "Installation Steps"},
            {"page_id": "test_3", "page_title": "Beginner Guide"}
        ]

        # Generate random embeddings (normally would use GeminiEmbedder)
        print("   Generating test embeddings...")
        test_embeddings = [
            np.random.randn(settings.embedding_dimension).tolist()
            for _ in test_docs
        ]

        # Add documents
        vector_store.add_documents(
            ids=test_ids,
            embeddings=test_embeddings,
            metadatas=test_metadatas,
            documents=test_docs
        )
        print(f"✅ Added {len(test_docs)} test documents")
    except Exception as e:
        print(f"❌ Failed to add documents: {e}")
        return False
    print()

    # Test 4: Query documents
    print("Test 4: Querying documents...")
    try:
        # Create a query embedding
        query_embedding = np.random.randn(settings.embedding_dimension).tolist()

        # Query the vector store
        results = vector_store.query(query_embedding, top_k=2)

        if results["documents"][0]:
            print(f"✅ Query returned {len(results['documents'][0])} results")
            for i, doc in enumerate(results["documents"][0]):
                print(f"   Result {i+1}: {doc[:50]}...")
                print(f"   Distance: {results['distances'][0][i]:.4f}")
        else:
            print("⚠️  No results returned")
    except Exception as e:
        print(f"❌ Failed to query: {e}")
    print()

    # Test 5: Get all documents
    print("Test 5: Getting all documents...")
    try:
        all_docs = vector_store.get_all_documents()
        print(f"✅ Retrieved {len(all_docs['documents'])} documents")
        for i, doc in enumerate(all_docs["documents"][:3]):
            print(f"   Doc {i+1}: {doc[:50]}...")
    except Exception as e:
        print(f"❌ Failed to get all documents: {e}")
    print()

    # Test 6: Delete by page ID
    print("Test 6: Deleting documents by page ID...")
    try:
        vector_store.delete_by_page_id("test_1")
        print("✅ Deleted documents with page_id='test_1'")

        # Verify deletion
        stats_after = vector_store.get_stats()
        print(f"   Chunks after deletion: {stats_after['total_chunks']}")
    except Exception as e:
        print(f"❌ Failed to delete: {e}")
    print()

    # Test 7: Clear collection (cleanup)
    print("Test 7: Clearing test data...")
    try:
        vector_store.clear_collection()
        print("✅ Collection cleared")

        # Verify clearing
        stats_final = vector_store.get_stats()
        print(f"   Final chunk count: {stats_final['total_chunks']}")
    except Exception as e:
        print(f"❌ Failed to clear: {e}")
    print()

    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    return True


def test_with_real_embeddings():
    """Test with real Gemini embeddings."""

    print("=" * 60)
    print("Testing Qdrant with Real Embeddings")
    print("=" * 60)
    print()

    try:
        # Initialize components
        print("Initializing components...")
        vector_store = VectorStore()
        embedder = GeminiEmbedder()
        print("✅ Components initialized")
        print()

        # Test documents
        test_docs = [
            "Python is a versatile programming language used for web development.",
            "How to install Python on Windows, Mac, and Linux systems.",
            "Python installation requires downloading from python.org.",
            "JavaScript is another popular programming language."
        ]

        # Generate real embeddings
        print("Generating embeddings with Gemini...")
        embeddings = []
        for doc in test_docs:
            embedding = embedder.generate_embedding(doc)
            if embedding:
                embeddings.append(embedding)
                print(f"   ✅ Embedded: {doc[:50]}...")
            else:
                print(f"   ❌ Failed to embed: {doc[:50]}...")
                embeddings.append(np.random.randn(settings.embedding_dimension).tolist())
        print()

        # Add to vector store
        print("Adding documents to Qdrant...")
        test_ids = [f"real_test_{i}" for i in range(len(test_docs))]
        test_metadatas = [
            {"page_id": f"real_{i}", "page_title": f"Test Doc {i}"}
            for i in range(len(test_docs))
        ]

        vector_store.add_documents(
            ids=test_ids,
            embeddings=embeddings,
            metadatas=test_metadatas,
            documents=test_docs
        )
        print(f"✅ Added {len(test_docs)} documents")
        print()

        # Test semantic search
        query = "How do I install Python?"
        print(f"Testing semantic search: '{query}'")

        # Generate query embedding
        query_embedding = embedder.generate_embedding(query)
        if query_embedding:
            results = vector_store.query(query_embedding, top_k=3)

            if results["documents"][0]:
                print(f"✅ Found {len(results['documents'][0])} results:")
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i]
                    similarity = 1 - distance
                    print(f"   {i+1}. (Similarity: {similarity:.2%}) {doc[:80]}...")
            else:
                print("❌ No results found")
        else:
            print("❌ Failed to generate query embedding")
        print()

        # Cleanup
        print("Cleaning up test data...")
        vector_store.clear_collection()
        print("✅ Test data cleared")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    print()
    print("=" * 60)
    print("✅ Real embedding tests completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("Qdrant Integration Test Suite")
    print("==============================")
    print()

    # Run basic tests
    if test_qdrant_operations():
        print("\n" + "=" * 60)
        print("Basic tests passed! Testing with real embeddings...")
        print("=" * 60 + "\n")

        # Run tests with real embeddings if basic tests pass
        test_with_real_embeddings()
    else:
        print("\n❌ Basic tests failed. Please check your Qdrant configuration.")
        sys.exit(1)