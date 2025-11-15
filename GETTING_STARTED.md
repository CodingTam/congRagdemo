# Getting Started with Confluence RAG System

Welcome! This guide will help you get your Confluence RAG system up and running.

## 🎯 What You're Building

A smart chatbot that can answer questions about your Confluence documentation using AI. Ask questions in natural language, get detailed answers with source citations.

## 📋 Before You Start

Make sure you have:
- [ ] Python 3.9 or higher
- [ ] Node.js 16 or higher
- [ ] Access to your on-premises Confluence
- [ ] A Confluence Personal Access Token (PAT)
- [ ] Google Cloud project with Vertex AI enabled

## 🚀 Step-by-Step Setup

### Step 1: Verify Prerequisites

Run the verification script:

```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag
./verify_setup.sh
```

This will check if you have all required tools installed.

### Step 2: Get Your Confluence Personal Access Token

1. Log into your Confluence instance at https://confluence.agile.com
2. Click your profile picture → **Settings**
3. Select **Personal Access Tokens**
4. Click **Create token**
5. Give it a name (e.g., "RAG System")
6. Set expiration (recommend 90 days for POC)
7. **Copy the token** (you won't see it again!)

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or code .env, vim .env, etc.
```

**Update these values in .env:**

```bash
# Replace with your actual PAT token
CONFLUENCE_API_TOKEN=your_actual_token_here

# Verify this matches your Confluence URL
CONFLUENCE_BASE_URL=https://confluence.agile.com

# Google Cloud settings (update if different)
GOOGLE_CLOUD_PROJECT=divine-camera-478315-s6
GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 4: Set Up Google Cloud Authentication

Choose one option:

**Option A: Service Account (Recommended)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

**Option B: Application Default Credentials**
```bash
gcloud auth application-default login
```

### Step 5: Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

You should see packages installing. This takes about 1-2 minutes.

### Step 6: Install Frontend Dependencies

```bash
cd ../frontend

# Install Node packages
npm install
```

This takes about 2-3 minutes.

### Step 7: Test Your Setup

Run the verification script again:

```bash
cd ..
./verify_setup.sh
```

You should see all green checkmarks! ✅

### Step 8: Start the Backend

Open a new terminal window:

```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/backend
source venv/bin/activate
python api.py
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ Backend is running!

### Step 9: Start the Frontend

Open another terminal window:

```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/frontend
npm start
```

Your browser should automatically open to http://localhost:3000

✅ Frontend is running!

### Step 10: Ingest Your First Confluence Page

#### Find a Page ID

1. Open a Confluence page in your browser
2. Look at the URL
3. Find the number after `pageId=`

Example:
```
https://confluence.agile.com/display/TEAM/My+Page?pageId=123456
                                                           ^^^^^^
                                                        This is your page ID
```

#### Ingest the Page

**Option A: Using Swagger UI (Easiest)**

1. Open http://localhost:8000/docs in your browser
2. Find the `/api/ingest` endpoint
3. Click **"Try it out"**
4. Enter your page ID:

```json
{
  "page_ids": ["123456"]
}
```

5. Click **"Execute"**
6. Wait for success response

**Option B: Using curl**

```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"page_ids": ["123456"]}'
```

**Success looks like:**
```json
{
  "status": "success",
  "pages_processed": 1,
  "chunks_created": 15,
  "pages": [...]
}
```

### Step 11: Ask Your First Question! 🎉

1. Go to http://localhost:3000
2. You'll see the chat interface
3. Type a question about your Confluence page
4. Press Enter
5. Watch the magic happen!

**Try asking:**
- "What is this page about?"
- "Summarize the main points"
- "How do I [something from your page]?"

## 🎊 You're Done!

Your Confluence RAG system is now running! You should see:
- ✅ A detailed answer to your question
- ✅ Source references showing which Confluence page was used
- ✅ Clickable links back to Confluence

## 🔄 Daily Usage

### Starting the System

**Terminal 1 - Backend:**
```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/backend
source venv/bin/activate
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/tamilarasanrajendran/Documents/01.Projects/Confluence_Rag/frontend
npm start
```

### Adding More Pages

Use the same ingest process:
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"page_ids": ["123456", "789012", "345678"]}'
```

### Checking Status

```bash
curl http://localhost:8000/api/status
```

## 🐛 Troubleshooting

### "Connection refused" to Confluence

**Check:**
1. Is your VPN connected (if required)?
2. Is the CONFLUENCE_BASE_URL correct in .env?
3. Is your PAT token valid?

**Test connection:**
```bash
cd backend
source venv/bin/activate
python -c "from confluence_client import ConfluenceClient; print('OK' if ConfluenceClient().test_connection() else 'FAILED')"
```

### "Authentication error" with Google Cloud

**Fix:**
```bash
# Re-authenticate
gcloud auth application-default login

# Or set service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Port 8000 already in use

**Fix:**
```bash
# Find the process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Frontend can't connect to backend

**Check:**
1. Is backend running? (Terminal 1 should show "Uvicorn running...")
2. Check browser console for errors (F12 → Console)
3. Verify backend is on port 8000: http://localhost:8000

### No results when querying

**Check:**
1. Did you ingest pages? `curl http://localhost:8000/api/pages`
2. Are pages successfully indexed?
3. Try a simpler question first

## 📚 Next Steps

### Learn More
- **README.md** - Comprehensive documentation
- **TESTING_GUIDE.md** - Testing procedures
- **PROJECT_SUMMARY.md** - Technical overview

### Improve Your System
1. **Ingest more pages** - Better coverage = better answers
2. **Tune chunk size** - Adjust CHUNK_SIZE in .env if needed
3. **Adjust retrieval** - Change TOP_K_RESULTS for more/fewer sources

### Share with Team
1. Document your specific Confluence pages
2. Create example questions
3. Train team members on usage

## 💡 Tips for Best Results

### Good Questions
✅ "How do I deploy the application?"
✅ "What are the steps for setting up the environment?"
✅ "Where can I find the API documentation?"

### Less Effective Questions
❌ "Tell me everything"
❌ "What?"
❌ Questions about pages you haven't ingested

### Getting Better Answers
- Ingest related pages together
- Ask specific questions
- Use keywords from your documentation
- Try rephrasing if first answer isn't perfect

## 🎯 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] At least 1 page ingested
- [ ] Successfully asked a question
- [ ] Received an answer with sources
- [ ] Clicked a source link to Confluence

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review the full README.md
3. Check API docs at http://localhost:8000/docs
4. Review TESTING_GUIDE.md for detailed tests

## 🎉 Congratulations!

You've successfully set up your Confluence RAG system! You now have an AI-powered assistant that can answer questions about your internal documentation.

**Happy querying!** 🚀

---

**Quick Reference:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Status: http://localhost:8000/api/status

