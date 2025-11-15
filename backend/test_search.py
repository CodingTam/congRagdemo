#!/usr/bin/env python3
"""
Test script to validate improved search capabilities.
This script tests various search scenarios including:
- Direct keyword matches
- Semantic similar queries
- Query variations
- Common phrasings
"""

import sys
import json
from rag_engine import RAGEngine
from config import settings


def test_search_queries():
    """Test various search queries to validate improvements."""

    print("=" * 60)
    print("Testing Improved Search Capabilities")
    print("=" * 60)

    # Initialize RAG engine
    print("\n✅ Initializing RAG engine...")
    rag = RAGEngine()

    # Check if any documents are indexed
    stats = rag.get_status()
    if stats["documents_indexed"] == 0:
        print("⚠️  No documents indexed. Please ingest some pages first.")
        print("Example: python -c \"from rag_engine import RAGEngine; rag = RAGEngine(); print(rag.ingest_page('YOUR_PAGE_ID'))\"")
        return

    print(f"📊 Found {stats['documents_indexed']} indexed pages with {stats['total_chunks']} chunks")

    # Test queries - these should work even with different phrasings
    test_queries = [
        # Original problematic query
        "how to install Python",

        # Variations that should also work
        "Python installation steps",
        "setup Python environment",
        "configure Python",
        "Python setup guide",

        # More general queries
        "installation guide",
        "setup instructions",
        "how to configure",

        # Keyword-focused queries
        "Python install",
        "install setup",

        # Question variations
        "what are the steps to install Python",
        "where can I find Python installation instructions",
        "Python installation documentation"
    ]

    print(f"\n🔍 Testing {len(test_queries)} query variations...")
    print("-" * 60)

    results_summary = []

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/{len(test_queries)}: \"{query}\"")
        print("-" * 40)

        try:
            # Execute query
            result = rag.query(query, top_k=3)

            # Check if results were found
            has_results = bool(result["chunks_used"])

            if has_results:
                print(f"✅ Found {len(result['chunks_used'])} relevant chunks")
                print(f"📄 Sources: {', '.join([s['page_title'] for s in result['sources']])}")

                # Show first 200 chars of answer
                answer_preview = result["answer"][:200] + "..." if len(result["answer"]) > 200 else result["answer"]
                print(f"💬 Answer preview: {answer_preview}")

                # Show relevance scores
                if result["sources"]:
                    scores = [s.get("relevance_score", 0) for s in result["sources"]]
                    print(f"📊 Relevance scores: {scores}")
            else:
                print("❌ No results found")

            results_summary.append({
                "query": query,
                "found": has_results,
                "num_chunks": len(result["chunks_used"]),
                "sources": [s['page_title'] for s in result['sources']] if has_results else []
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            results_summary.append({
                "query": query,
                "found": False,
                "error": str(e)
            })

    # Print summary
    print("\n" + "=" * 60)
    print("SEARCH TEST SUMMARY")
    print("=" * 60)

    successful = [r for r in results_summary if r["found"]]
    failed = [r for r in results_summary if not r["found"]]

    print(f"\n📊 Results:")
    print(f"  ✅ Successful: {len(successful)}/{len(test_queries)}")
    print(f"  ❌ Failed: {len(failed)}/{len(test_queries)}")

    if successful:
        print(f"\n✅ Queries that found results:")
        for r in successful:
            print(f"  - \"{r['query']}\" → {r['num_chunks']} chunks from {', '.join(r['sources'])}")

    if failed:
        print(f"\n❌ Queries that failed:")
        for r in failed:
            print(f"  - \"{r['query']}\"")
            if "error" in r:
                print(f"    Error: {r['error']}")

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if len(successful) < len(test_queries) / 2:
        print("\n⚠️  Less than 50% of queries succeeded. Consider:")
        print("  1. Check if Python-related content is actually indexed")
        print("  2. Review the chunk size (current: {})".format(settings.chunk_size))
        print("  3. Adjust similarity threshold (currently 0.2)")
        print("  4. Verify embeddings are being generated correctly")
    else:
        print("\n✅ Search is working well! Most query variations found results.")

    if failed:
        print("\n💡 For failed queries, try:")
        print("  1. Using more specific keywords")
        print("  2. Breaking complex queries into simpler ones")
        print("  3. Checking if the content exists in indexed pages")


def test_specific_query(query: str):
    """Test a specific query and show detailed results."""

    print("=" * 60)
    print(f"Testing Query: \"{query}\"")
    print("=" * 60)

    rag = RAGEngine()

    # Get detailed results
    result = rag.query(query, top_k=5)

    print("\n📋 RESULTS:")
    print("-" * 40)

    if result["chunks_used"]:
        print(f"\n✅ Found {len(result['chunks_used'])} relevant chunks\n")

        print("📄 SOURCES:")
        for i, source in enumerate(result["sources"], 1):
            print(f"  {i}. {source['page_title']}")
            print(f"     URL: {source['page_url']}")
            print(f"     Relevance: {source['relevance_score']*100:.1f}%")

        print(f"\n💬 ANSWER:")
        print("-" * 40)
        print(result["answer"])

        print(f"\n📑 CHUNKS USED:")
        print("-" * 40)
        for i, chunk in enumerate(result["chunks_used"], 1):
            print(f"\nChunk {i} from {chunk['page_title']}:")
            print(chunk["text"])
    else:
        print("\n❌ No results found for this query")
        print("\nTrying to understand why...")

        # Try to debug
        from hybrid_search import HybridSearch
        key_terms = HybridSearch._extract_key_terms(None, query)
        print(f"\n🔍 Key terms extracted: {key_terms}")
        print("\n💡 Suggestions:")
        print("  1. Check if content about this topic is indexed")
        print("  2. Try simpler keywords like: {}".format(", ".join(key_terms) if key_terms else "N/A"))
        print("  3. Verify pages are successfully ingested")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific query
        query = " ".join(sys.argv[1:])
        test_specific_query(query)
    else:
        # Run all tests
        test_search_queries()

        print("\n" + "=" * 60)
        print("💡 TIP: Test a specific query with:")
        print("   python test_search.py \"your search query here\"")
        print("=" * 60)