# Quick Start Guide

Get the Confluence RAG system up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python3 --version

# Check Node.js version (need 16+)
node --version

# Check npm
npm --version
```

## Step 1: Setup Backend (2 minutes)

```bash
# Navigate to project
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag

# Create and activate virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (1 minute)

```bash
# Go back to project root
cd ..

# Copy environment template
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required changes in .env:**
- `CONFLUENCE_API_TOKEN` - Your Personal Access Token
- Verify `CONFLUENCE_BASE_URL` matches your instance

## Step 3: Setup Frontend (1 minute)

```bash
# Install frontend dependencies
cd frontend
npm install
```

## Step 4: Start the Application (1 minute)

### Terminal 1 - Backend:
```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/backend
source venv/bin/activate
python api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Frontend:
```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/frontend
npm start
```

Browser opens at: http://localhost:3000

## Step 5: Ingest Your First Page

### Option A: Using Swagger UI (Easiest)

1. Open http://localhost:8000/docs
2. Click on `/api/ingest` → "Try it out"
3. Enter your page IDs:
```json
{
  "page_ids": ["YOUR_PAGE_ID_HERE"]
}
```
4. Click "Execute"

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "page_ids": ["YOUR_PAGE_ID_HERE"]
  }'
```

## Step 6: Ask Your First Question!

1. Go to http://localhost:3000
2. Type: "What is this page about?"
3. Press Enter
4. See the magic happen! ✨

## Troubleshooting

### Can't connect to Confluence?
```bash
# Test connection
cd backend
source venv/bin/activate
python -c "from confluence_client import ConfluenceClient; print('OK' if ConfluenceClient().test_connection() else 'FAILED')"
```

### Google Cloud authentication error?
```bash
# Set up authentication
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
# OR
gcloud auth application-default login
```

### Port already in use?
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing
- Ingest more pages to improve coverage
- Explore the API at http://localhost:8000/docs

## Getting Confluence Page IDs

1. Open a Confluence page in your browser
2. Look at the URL
3. Find the number after `pageId=`

Example:
```
https://confluence.agile.com/display/TEAM/Page+Title?pageId=123456
                                                            ^^^^^^
                                                         This is your page ID
```

## Quick Commands Reference

```bash
# Start backend
cd backend && source venv/bin/activate && python api.py

# Start frontend
cd frontend && npm start

# Check status
curl http://localhost:8000/api/status

# List indexed pages
curl http://localhost:8000/api/pages

# Clear database (careful!)
curl -X DELETE http://localhost:8000/api/clear
```

---

**You're all set! 🚀 Happy querying!**

