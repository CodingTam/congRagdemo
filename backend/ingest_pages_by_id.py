#!/usr/bin/env python3
"""
Confluence Pages Ingestion Script (by Page IDs)

This script ingests specific Confluence pages into ChromaDB by page IDs.
Usage: python ingest_pages_by_id.py <PAGE_ID_1> <PAGE_ID_2> ...

Example:
    python ingest_pages_by_id.py 123456 789012 345678
"""

import sys
import argparse
from datetime import datetime
from config import settings
from rag_engine import RAGEngine


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print("  Confluence Page Ingestion Tool (by Page IDs)")
    print("  Load specific Confluence pages into ChromaDB")
    print("=" * 70)
    print()


def ingest_pages(page_ids):
    """
    Ingest specific Confluence pages by their IDs.
    
    Args:
        page_ids: List of Confluence page IDs
    """
    print_banner()
    
    print(f"📋 Configuration:")
    print(f"   Page IDs: {', '.join(page_ids)}")
    print(f"   Total Pages: {len(page_ids)}")
    print(f"   Confluence URL: {settings.confluence_base_url}")
    print(f"   ChromaDB Path: {settings.chromadb_path}")
    print()
    
    # Initialize RAG engine
    print("🔧 Initializing RAG engine...")
    rag_engine = RAGEngine()
    print("✅ RAG engine initialized")
    print()
    
    # Test Confluence connection
    print("🔌 Testing Confluence connection...")
    if not rag_engine.confluence_client.test_connection():
        print("❌ Failed to connect to Confluence!")
        print("   Check your CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN in .env")
        sys.exit(1)
    print("✅ Connected to Confluence")
    print()
    
    # Process pages
    print("⚙️  Processing pages...")
    print()
    
    start_time = datetime.now()
    results = rag_engine.ingest_pages(page_ids)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Print results
    print("\n📄 Page Results:")
    print("-" * 70)
    
    for page_result in results.get('pages', []):
        if page_result.get('success'):
            print(f"✅ {page_result['page_title']}")
            print(f"   Page ID: {page_result['page_id']}")
            print(f"   Chunks: {page_result['chunks_created']}")
            print(f"   URL: {page_result['page_url']}")
        else:
            print(f"❌ Failed: {page_result.get('error', 'Unknown error')}")
        print()
    
    # Print summary
    print("=" * 70)
    print("  Ingestion Summary")
    print("=" * 70)
    print(f"✅ Successful: {results['pages_processed']} page(s)")
    print(f"❌ Failed: {len(page_ids) - results['pages_processed']} page(s)")
    print(f"📦 Total Chunks: {results['chunks_created']}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print()
    
    # Get final stats
    stats = rag_engine.vector_store.get_stats()
    print("📊 Vector Database Stats:")
    print(f"   Total Pages: {stats['total_pages']}")
    print(f"   Total Chunks: {stats['total_chunks']}")
    print()
    
    if results['pages_processed'] > 0:
        print("🎉 Ingestion completed successfully!")
        print()
        print("Next steps:")
        print("1. Start the backend: python api.py")
        print("2. Start the frontend: cd ../frontend && npm start")
        print("3. Open http://localhost:3000 and start asking questions!")
    else:
        print("⚠️  No pages were successfully ingested.")
        print("   Please check the errors above and try again.")
    
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ingest specific Confluence pages into ChromaDB by page IDs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_pages_by_id.py 123456
  python ingest_pages_by_id.py 123456 789012 345678

How to find page IDs:
  Open a Confluence page and look at the URL:
  https://confluence.agile.com/display/TEAM/Page+Title?pageId=123456
                                                               ^^^^^^
                                                            This is the page ID

Note: Make sure your .env file is configured with:
  - CONFLUENCE_BASE_URL
  - CONFLUENCE_API_TOKEN
  - GOOGLE_CLOUD_PROJECT and credentials
        """
    )
    
    parser.add_argument(
        'page_ids',
        nargs='+',
        type=str,
        help='One or more Confluence page IDs'
    )
    
    args = parser.parse_args()
    
    try:
        ingest_pages(args.page_ids)
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

