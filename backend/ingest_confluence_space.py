#!/usr/bin/env python3
"""
Confluence Space Ingestion Script

This script ingests all pages from a Confluence space into ChromaDB.
Usage: python ingest_confluence_space.py <SPACE_KEY> [--limit LIMIT]

Example:
    python ingest_confluence_space.py TEAM
    python ingest_confluence_space.py DOCS --limit 10
"""

import sys
import argparse
from datetime import datetime
from config import settings
from rag_engine import RAGEngine


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print("  Confluence Space Ingestion Tool")
    print("  Load Confluence pages into ChromaDB for RAG")
    print("=" * 70)
    print()


def print_progress(current, total, message=""):
    """Print progress bar."""
    percent = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {percent:.1f}% ({current}/{total}) {message}", end="", flush=True)


def ingest_space(space_key, limit=None):
    """
    Ingest all pages from a Confluence space.
    
    Args:
        space_key: Confluence space key (e.g., 'TEAM', 'DOCS')
        limit: Maximum number of pages to ingest (None = all pages)
    """
    print_banner()
    
    print(f"📋 Configuration:")
    print(f"   Space Key: {space_key}")
    print(f"   Limit: {limit if limit else 'No limit (all pages)'}")
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
    
    # Fetch pages from space
    print(f"📥 Fetching pages from space '{space_key}'...")
    pages = rag_engine.confluence_client.get_pages_from_space(
        space_key=space_key,
        limit=limit if limit else 100  # Default to 100 if no limit
    )
    
    if not pages:
        print(f"❌ No pages found in space '{space_key}'")
        print("   Please check:")
        print("   - Space key is correct")
        print("   - Your PAT has access to this space")
        print("   - Space contains pages")
        sys.exit(1)
    
    print(f"✅ Found {len(pages)} page(s)")
    print()
    
    # Process each page
    print("⚙️  Processing pages...")
    print()
    
    successful = 0
    failed = 0
    total_chunks = 0
    start_time = datetime.now()
    
    for idx, page in enumerate(pages, 1):
        page_id = page.get('id')
        page_title = page.get('title', 'Unknown')
        
        print_progress(idx - 1, len(pages), f"Processing: {page_title[:40]}...")
        
        try:
            # Don't rebuild index after each page (massive performance improvement)
            result = rag_engine.ingest_page(page_id, rebuild_index=False)
            
            if result.get('success'):
                successful += 1
                chunks = result.get('chunks_created', 0)
                total_chunks += chunks
                print_progress(idx, len(pages), f"✓ {page_title[:40]}")
            else:
                failed += 1
                error = result.get('error', 'Unknown error')
                print_progress(idx, len(pages), f"✗ {page_title[:40]}: {error}")
        
        except Exception as e:
            failed += 1
            print_progress(idx, len(pages), f"✗ {page_title[:40]}: {str(e)}")
    
    print()  # New line after progress bar
    print()
    
    # Rebuild keyword index once at the end (much more efficient!)
    if successful > 0:
        print("🔨 Building keyword search index...")
        rag_engine.hybrid_search.build_keyword_index()
        print("✅ Keyword index built")
        print()
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Print summary
    print("=" * 70)
    print("  Ingestion Summary")
    print("=" * 70)
    print(f"✅ Successful: {successful} page(s)")
    print(f"❌ Failed: {failed} page(s)")
    print(f"📦 Total Chunks: {total_chunks}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"⚡ Speed: {duration/len(pages):.2f} sec/page" if len(pages) > 0 else "")
    print()
    
    # Get final stats
    stats = rag_engine.vector_store.get_stats()
    print("📊 Vector Database Stats:")
    print(f"   Total Pages: {stats['total_pages']}")
    print(f"   Total Chunks: {stats['total_chunks']}")
    print()
    
    if successful > 0:
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
        description='Ingest Confluence space pages into ChromaDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest_confluence_space.py TEAM
  python ingest_confluence_space.py DOCS --limit 10
  python ingest_confluence_space.py PROJECT --limit 50

Note: Make sure your .env file is configured with:
  - CONFLUENCE_BASE_URL
  - CONFLUENCE_API_TOKEN
  - GOOGLE_CLOUD_PROJECT and credentials
        """
    )
    
    parser.add_argument(
        'space_key',
        type=str,
        help='Confluence space key (e.g., TEAM, DOCS, PROJECT)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of pages to ingest (default: all pages, max 100)'
    )
    
    args = parser.parse_args()
    
    try:
        ingest_space(args.space_key, args.limit)
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

