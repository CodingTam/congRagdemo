# Testing Guide for Confluence RAG System

This guide provides comprehensive testing procedures for the Confluence RAG system.

## 🧪 Testing Checklist

### Phase 1: Backend Component Testing

#### 1.1 Test Confluence Connection

```bash
cd backend
source venv/bin/activate

# Create a test script
cat > test_confluence.py << 'EOF'
from confluence_client import ConfluenceClient

client = ConfluenceClient()
print("Testing Confluence connection...")

if client.test_connection():
    print("✅ Confluence connection successful!")
else:
    print("❌ Confluence connection failed!")
    print("Check your CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN")
EOF

python test_confluence.py
```

**Expected Output:**
```
Testing Confluence connection...
✅ Confluence connection successful!
```

#### 1.2 Test Gemini Embeddings

```bash
cat > test_embeddings.py << 'EOF'
from embedder import GeminiEmbedder

embedder = GeminiEmbedder()
print("Testing Gemini embeddings...")

test_text = "This is a test sentence for embedding generation."
embedding = embedder.generate_embedding(test_text)

if embedding and len(embedding) > 0:
    print(f"✅ Embedding generated successfully!")
    print(f"   Dimension: {len(embedding)}")
else:
    print("❌ Embedding generation failed!")
    print("Check your Google Cloud authentication")
EOF

python test_embeddings.py
```

**Expected Output:**
```
Testing Gemini embeddings...
✅ Embedding generated successfully!
   Dimension: 768
```

#### 1.3 Test ChromaDB

```bash
cat > test_chromadb.py << 'EOF'
from vector_store import VectorStore

print("Testing ChromaDB...")
store = VectorStore()

# Test adding a document
test_embedding = [0.1] * 768
store.add_documents(
    ids=["test_1"],
    embeddings=[test_embedding],
    metadatas=[{"test": "data"}],
    documents=["Test document"]
)

# Test retrieval
results = store.query(test_embedding, top_k=1)

if results["ids"][0]:
    print("✅ ChromaDB working correctly!")
    print(f"   Stored and retrieved: {results['ids'][0][0]}")
else:
    print("❌ ChromaDB test failed!")

# Clean up
store.clear_collection()
EOF

python test_chromadb.py
```

**Expected Output:**
```
Testing ChromaDB...
Added 1 documents to vector store
✅ ChromaDB working correctly!
   Stored and retrieved: test_1
Collection cleared
```

#### 1.4 Test Text Chunking

```bash
cat > test_chunking.py << 'EOF'
from utils import chunk_text

print("Testing text chunking...")

test_text = """
This is a test document with multiple paragraphs.

Paragraph 1 contains some information about the system.
It has multiple sentences to test the chunking logic.

Paragraph 2 has different content.
This helps verify that chunking works across paragraphs.

Paragraph 3 is the final section.
It ensures we handle the end of documents correctly.
""" * 5  # Repeat to ensure we get multiple chunks

chunks = chunk_text(test_text, chunk_size=200, overlap=50)

print(f"✅ Chunking successful!")
print(f"   Original length: {len(test_text)} chars")
print(f"   Number of chunks: {len(chunks)}")
print(f"   Average chunk size: {sum(len(c) for c in chunks) / len(chunks):.0f} chars")
EOF

python test_chunking.py
```

### Phase 2: API Testing

#### 2.1 Start the Backend

```bash
# In terminal 1
cd backend
source venv/bin/activate
python api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

#### 2.2 Test API Endpoints

Open a new terminal:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test status endpoint
curl http://localhost:8000/api/status

# Test pages endpoint
curl http://localhost:8000/api/pages
```

**Expected Responses:**

Root:
```json
{
  "message": "Confluence RAG API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

Status:
```json
{
  "status": "healthy",
  "confluence_connected": true,
  "vector_db_loaded": true,
  "documents_indexed": 0,
  "total_chunks": 0
}
```

#### 2.3 Test Document Ingestion

**Important:** Replace `123456` with an actual page ID from your Confluence instance.

```bash
# Ingest a single page
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "page_ids": ["123456"]
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "pages_processed": 1,
  "chunks_created": 15,
  "pages": [
    {
      "success": true,
      "page_id": "123456",
      "page_title": "Example Page",
      "page_url": "https://confluence.agile.com/...",
      "chunks_created": 15
    }
  ]
}
```

#### 2.4 Test Query Endpoint

```bash
# Query the system
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this page about?"
  }'
```

**Expected Response:**
```json
{
  "answer": "Based on the Confluence documentation...",
  "sources": [
    {
      "page_title": "Example Page",
      "page_url": "https://confluence.agile.com/...",
      "relevance_score": 0.89
    }
  ],
  "chunks_used": [...]
}
```

### Phase 3: Frontend Testing

#### 3.1 Start the Frontend

```bash
# In terminal 2
cd frontend
npm start
```

Wait for: `Compiled successfully!`

Browser should open at: http://localhost:3000

#### 3.2 UI Component Testing

**Test Checklist:**

- [ ] Header displays correctly with title and subtitle
- [ ] Status indicator shows connection status
- [ ] Welcome message appears when no messages
- [ ] Example questions are visible
- [ ] Search box is present and functional
- [ ] Clear button is visible

#### 3.3 Interaction Testing

1. **Type a question** in the search box
2. **Press Enter** or click send button
3. **Verify:**
   - [ ] User message appears on the right
   - [ ] Loading indicator shows "🔍 Searching knowledge base..."
   - [ ] Loading indicator changes to "✨ Generating response..."
   - [ ] Bot response appears on the left
   - [ ] Source references appear below the answer
   - [ ] Sources are expandable
   - [ ] Confluence links are clickable

4. **Click a source card**
   - [ ] Expands to show details
   - [ ] Shows relevance score
   - [ ] Link opens in new tab

5. **Test Clear button**
   - [ ] Clears all messages
   - [ ] Welcome message reappears

### Phase 4: End-to-End Testing

#### Test Scenario 1: Simple Question

1. Ingest a page about deployment
2. Ask: "How do I deploy?"
3. **Verify:**
   - Response time < 10 seconds
   - Answer contains numbered steps
   - Source citation present
   - Confluence link works

#### Test Scenario 2: Multi-Source Question

1. Ingest 2-3 related pages
2. Ask a question that spans multiple pages
3. **Verify:**
   - Multiple sources referenced
   - Answer synthesizes information
   - All sources are relevant

#### Test Scenario 3: Unknown Topic

1. Ask about something not in indexed pages
2. **Verify:**
   - System responds gracefully
   - Message indicates information not found
   - Suggests rephrasing

#### Test Scenario 4: Follow-up Questions

1. Ask initial question
2. Ask follow-up question
3. **Verify:**
   - Both questions answered
   - Conversation history maintained
   - Context preserved

### Phase 5: Performance Testing

#### 5.1 Ingestion Performance

```bash
# Time the ingestion of 3 pages
time curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "page_ids": ["123456", "789012", "345678"]
  }'
```

**Target:** < 30 seconds for 3 pages

#### 5.2 Query Performance

```bash
# Time a query
time curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy the framework?"
  }'
```

**Target:** < 10 seconds

### Phase 6: Error Handling Testing

#### 6.1 Invalid Page ID

```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "page_ids": ["999999999"]
  }'
```

**Verify:** Graceful error message

#### 6.2 Empty Question

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": ""
  }'
```

**Verify:** 400 error with helpful message

#### 6.3 Backend Offline

1. Stop the backend
2. Try to send a message in UI
3. **Verify:** Error message displayed

## 📊 Test Results Template

```
Date: ___________
Tester: ___________

Backend Component Tests:
[ ] Confluence Connection
[ ] Gemini Embeddings
[ ] ChromaDB
[ ] Text Chunking

API Tests:
[ ] Root Endpoint
[ ] Status Endpoint
[ ] Ingest Endpoint
[ ] Query Endpoint
[ ] Pages Endpoint

Frontend Tests:
[ ] UI Components
[ ] User Interactions
[ ] Source References
[ ] Clear Functionality

End-to-End Tests:
[ ] Simple Question
[ ] Multi-Source Question
[ ] Unknown Topic
[ ] Follow-up Questions

Performance:
[ ] Ingestion < 30s for 3 pages
[ ] Query < 10s

Error Handling:
[ ] Invalid Page ID
[ ] Empty Question
[ ] Backend Offline

Notes:
_________________________________
_________________________________
_________________________________
```

## 🐛 Common Issues and Solutions

### Issue: "Connection refused" errors

**Solution:** Ensure backend is running on port 8000

### Issue: CORS errors in browser

**Solution:** Check CORS middleware in `api.py`

### Issue: Empty responses

**Solution:** Verify pages are ingested: `curl http://localhost:8000/api/pages`

### Issue: Slow queries

**Solution:** Check `TOP_K_RESULTS` setting, reduce if needed

## ✅ Success Criteria

The POC is successful when:

- ✅ Backend connects to Confluence
- ✅ 2-3 pages ingested successfully
- ✅ User can ask questions via UI
- ✅ Detailed answers with numbered steps
- ✅ Source references with clickable links
- ✅ Full flow completes in < 10 seconds
- ✅ UI is clean and professional
- ✅ Error handling works gracefully

---

**Happy Testing! 🚀**

