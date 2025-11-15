# Data Ingestion Scripts

Two standalone scripts to load Confluence data into ChromaDB.

## 📋 Prerequisites

1. **Configure `.env` file**:
```bash
CONFLUENCE_BASE_URL=https://confluence.agile.com
CONFLUENCE_API_TOKEN=your_pat_token_here
GOOGLE_CLOUD_PROJECT=divine-camera-478315-s6
GOOGLE_CLOUD_LOCATION=us-central1
```

2. **Activate virtual environment**:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Ensure dependencies are installed**:
```bash
pip install -r requirements.txt
```

## 🚀 Script 1: Ingest by Space Key

Load all pages from a Confluence space.

### Usage

```bash
python ingest_confluence_space.py <SPACE_KEY> [--limit LIMIT]
```

### Examples

```bash
# Ingest all pages from TEAM space (up to 100)
python ingest_confluence_space.py TEAM

# Ingest first 10 pages from DOCS space
python ingest_confluence_space.py DOCS --limit 10

# Ingest 50 pages from PROJECT space
python ingest_confluence_space.py PROJECT --limit 50
```

### Options

- `SPACE_KEY` (required): The Confluence space key (e.g., TEAM, DOCS, PROJECT)
- `--limit` (optional): Maximum number of pages to ingest (default: 100)

### Output

```
======================================================================
  Confluence Space Ingestion Tool
  Load Confluence pages into ChromaDB for RAG
======================================================================

📋 Configuration:
   Space Key: TEAM
   Limit: No limit (all pages)
   Confluence URL: https://confluence.agile.com
   ChromaDB Path: ./data/chromadb

🔧 Initializing RAG engine...
✅ RAG engine initialized

🔌 Testing Confluence connection...
✅ Connected to Confluence

📥 Fetching pages from space 'TEAM'...
✅ Found 25 page(s)

⚙️  Processing pages...

[████████████████████████████████████████] 100.0% (25/25) ✓ Deployment Guide

======================================================================
  Ingestion Summary
======================================================================
✅ Successful: 25 page(s)
❌ Failed: 0 page(s)
📦 Total Chunks: 387
⏱️  Duration: 45.32 seconds
⚡ Speed: 1.81 sec/page

📊 Vector Database Stats:
   Total Pages: 25
   Total Chunks: 387

🎉 Ingestion completed successfully!

Next steps:
1. Start the backend: python api.py
2. Start the frontend: cd ../frontend && npm start
3. Open http://localhost:3000 and start asking questions!
```

---

## 📄 Script 2: Ingest by Page IDs

Load specific Confluence pages by their IDs.

### Usage

```bash
python ingest_pages_by_id.py <PAGE_ID_1> <PAGE_ID_2> ...
```

### Examples

```bash
# Ingest a single page
python ingest_pages_by_id.py 123456

# Ingest multiple pages
python ingest_pages_by_id.py 123456 789012 345678
```

### How to Find Page IDs

Open a Confluence page and look at the URL:
```
https://confluence.agile.com/display/TEAM/Page+Title?pageId=123456
                                                           ^^^^^^
                                                    This is the page ID
```

### Output

```
======================================================================
  Confluence Page Ingestion Tool (by Page IDs)
  Load specific Confluence pages into ChromaDB
======================================================================

📋 Configuration:
   Page IDs: 123456, 789012, 345678
   Total Pages: 3
   Confluence URL: https://confluence.agile.com
   ChromaDB Path: ./data/chromadb

🔧 Initializing RAG engine...
✅ RAG engine initialized

🔌 Testing Confluence connection...
✅ Connected to Confluence

⚙️  Processing pages...

📄 Page Results:
----------------------------------------------------------------------
✅ Deployment Guide
   Page ID: 123456
   Chunks: 15
   URL: https://confluence.agile.com/display/TEAM/Deployment+Guide

✅ API Documentation
   Page ID: 789012
   Chunks: 22
   URL: https://confluence.agile.com/display/TEAM/API+Documentation

✅ Setup Instructions
   Page ID: 345678
   Chunks: 18
   URL: https://confluence.agile.com/display/TEAM/Setup+Instructions

======================================================================
  Ingestion Summary
======================================================================
✅ Successful: 3 page(s)
❌ Failed: 0 page(s)
📦 Total Chunks: 55
⏱️  Duration: 8.45 seconds

📊 Vector Database Stats:
   Total Pages: 3
   Total Chunks: 55

🎉 Ingestion completed successfully!
```

---

## 🔧 Troubleshooting

### Connection Failed

**Error**: `❌ Failed to connect to Confluence!`

**Solution**:
1. Check `CONFLUENCE_BASE_URL` in `.env`
2. Verify `CONFLUENCE_API_TOKEN` is valid
3. Ensure VPN is connected (if required)
4. Test manually: `curl -H "Authorization: Bearer YOUR_TOKEN" https://confluence.agile.com/rest/api/content?limit=1`

### No Pages Found

**Error**: `❌ No pages found in space 'TEAM'`

**Solution**:
1. Verify space key is correct (case-sensitive)
2. Check your PAT has read access to the space
3. Ensure space contains pages
4. Try listing spaces: Go to `https://confluence.agile.com/rest/api/space`

### Google Cloud Authentication Error

**Error**: Authentication errors when generating embeddings

**Solution**:
```bash
# Option 1: Set service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Use Application Default Credentials
gcloud auth application-default login
```

### ChromaDB Errors

**Error**: Database or permission errors

**Solution**:
```bash
# Clear the database and start fresh
rm -rf data/chromadb
mkdir -p data/chromadb
```

---

## 📊 What Happens During Ingestion

1. **Connection Test**: Verifies Confluence API access
2. **Fetch Pages**: Retrieves pages from space or by IDs
3. **Content Extraction**: Downloads full page HTML content
4. **Text Cleaning**: Removes HTML tags, scripts, styles
5. **Chunking**: Splits text into 800-char chunks with 150-char overlap
6. **Embedding Generation**: Creates vectors using Gemini API
7. **Storage**: Saves to ChromaDB with metadata
8. **Progress Tracking**: Shows real-time progress bar

---

## 💡 Best Practices

### For Large Spaces

```bash
# Start with a small limit to test
python ingest_confluence_space.py TEAM --limit 5

# Then increase gradually
python ingest_confluence_space.py TEAM --limit 25

# Finally, do full ingestion
python ingest_confluence_space.py TEAM
```

### For Production

1. **Identify critical pages first** - use page ID script
2. **Test with small subset** - verify quality
3. **Ingest full space** - when confident
4. **Monitor progress** - watch for errors
5. **Verify results** - check vector DB stats

### Incremental Updates

To update existing pages:
```bash
# Pages are re-indexed if you run again
# Old chunks are replaced with new ones
python ingest_pages_by_id.py 123456
```

---

## 🎯 Quick Reference

```bash
# By Space (most common)
python ingest_confluence_space.py TEAM

# By Space with limit
python ingest_confluence_space.py TEAM --limit 10

# By Page IDs
python ingest_pages_by_id.py 123456 789012

# Help
python ingest_confluence_space.py --help
python ingest_pages_by_id.py --help
```

---

## 🔄 After Ingestion

Once ingestion is complete:

1. **Start the backend**:
```bash
python api.py
```

2. **Start the frontend** (in another terminal):
```bash
cd ../frontend
npm start
```

3. **Open browser**: http://localhost:3000

4. **Ask questions** and see your Confluence data in action!

---

## 📝 Notes

- **Rate Limits**: Scripts respect Confluence API limits
- **Duplicate Pages**: Re-ingesting updates existing data
- **Storage**: All data stored locally in `./data/chromadb`
- **Costs**: Gemini API calls may incur costs (check Google Cloud billing)
- **Time**: ~2-5 seconds per page depending on size

---

**Happy Ingesting! 🚀**

