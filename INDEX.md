# Confluence RAG System - Documentation Index

Welcome to the Confluence RAG System! This index will help you find the right documentation for your needs.

## 🚀 Quick Navigation

### For First-Time Users
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** ⭐ START HERE
   - Step-by-step setup guide
   - Prerequisites check
   - Configuration instructions
   - First question walkthrough

2. **[QUICKSTART.md](QUICKSTART.md)** 
   - 5-minute quick setup
   - Minimal instructions
   - For experienced developers

### For Understanding the System
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
   - High-level overview
   - Architecture diagram
   - Technology stack
   - Key features

4. **[README.md](README.md)**
   - Comprehensive documentation
   - Detailed setup instructions
   - API reference
   - Troubleshooting guide

### For Testing & Validation
5. **[TESTING_GUIDE.md](TESTING_GUIDE.md)**
   - Component testing
   - API testing
   - End-to-end scenarios
   - Performance benchmarks

### For Development & Extension
6. **[memory-bank/](memory-bank/)**
   - Project context
   - System patterns
   - Technical decisions
   - Architecture details

## 📚 Documentation by Purpose

### "I want to get started quickly"
→ **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete beginner-friendly guide

### "I'm experienced, just give me the commands"
→ **[QUICKSTART.md](QUICKSTART.md)** - Minimal setup instructions

### "I need to understand what this system does"
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level overview

### "I need detailed technical documentation"
→ **[README.md](README.md)** - Comprehensive guide

### "I need to test the system"
→ **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures

### "I need to understand the architecture"
→ **[memory-bank/systemPatterns.md](memory-bank/systemPatterns.md)** - Architecture details

### "I need to extend or modify the system"
→ **[memory-bank/](memory-bank/)** - All technical context

## 🎯 Common Tasks

### Setting Up for the First Time
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Follow step-by-step instructions
3. Run `./verify_setup.sh` to check setup
4. Start asking questions!

### Daily Usage
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python api.py

# Terminal 2 - Frontend
cd frontend && npm start
```

### Adding New Pages
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"page_ids": ["123456", "789012"]}'
```

### Checking System Status
```bash
curl http://localhost:8000/api/status
```

### Troubleshooting
1. Check [README.md](README.md) troubleshooting section
2. Review [GETTING_STARTED.md](GETTING_STARTED.md) troubleshooting
3. Run `./verify_setup.sh` to diagnose issues

## 📁 File Structure Reference

```
confluence-rag/
├── INDEX.md                    ← You are here
├── GETTING_STARTED.md          ← Best starting point
├── QUICKSTART.md               ← Quick setup (5 min)
├── README.md                   ← Comprehensive docs
├── PROJECT_SUMMARY.md          ← High-level overview
├── TESTING_GUIDE.md            ← Testing procedures
├── verify_setup.sh             ← Setup verification script
├── .env.example                ← Environment template
├── .gitignore                  ← Git exclusions
│
├── backend/                    ← Python FastAPI backend
│   ├── api.py                  ← REST API endpoints
│   ├── config.py               ← Configuration
│   ├── confluence_client.py    ← Confluence integration
│   ├── embedder.py             ← Gemini embeddings
│   ├── vector_store.py         ← ChromaDB operations
│   ├── rag_engine.py           ← RAG orchestration
│   ├── utils.py                ← Text processing
│   ├── requirements.txt        ← Python dependencies
│   └── start.sh                ← Backend start script
│
├── frontend/                   ← React frontend
│   ├── src/
│   │   ├── App.js              ← Main application
│   │   ├── App.css             ← Main styles
│   │   └── components/         ← React components
│   ├── package.json            ← Node dependencies
│   └── start.sh                ← Frontend start script
│
└── memory-bank/                ← Project documentation
    ├── projectbrief.md         ← Project overview
    ├── productContext.md       ← Product goals
    ├── systemPatterns.md       ← Architecture
    ├── techContext.md          ← Technology details
    ├── activeContext.md        ← Current state
    └── progress.md             ← Implementation status
```

## 🎓 Learning Path

### Beginner Path
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Understand the system
3. **Practice** - Ingest pages and ask questions
4. **[README.md](README.md)** - Deep dive when needed

### Advanced Path
1. **[QUICKSTART.md](QUICKSTART.md)** - Quick setup
2. **[memory-bank/systemPatterns.md](memory-bank/systemPatterns.md)** - Architecture
3. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Validation
4. **Code exploration** - Read the source

### Administrator Path
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Initial setup
2. **[README.md](README.md)** - Full documentation
3. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Validation procedures
4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - System overview for team

## 🔗 Quick Links

### Web Interfaces
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Status**: http://localhost:8000/api/status

### Key Commands
```bash
# Verify setup
./verify_setup.sh

# Start backend
cd backend && ./start.sh

# Start frontend
cd frontend && ./start.sh

# Check status
curl http://localhost:8000/api/status

# List pages
curl http://localhost:8000/api/pages
```

## 📞 Getting Help

### Documentation
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup help
2. **[README.md](README.md)** - Comprehensive troubleshooting
3. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Validation help

### Tools
- **Verification Script**: `./verify_setup.sh`
- **API Documentation**: http://localhost:8000/docs
- **Status Endpoint**: http://localhost:8000/api/status

### Common Issues
- **Can't connect to Confluence**: Check `.env` configuration
- **Google Cloud auth errors**: Set up service account or ADC
- **Port conflicts**: Kill processes on 8000 or 3000
- **No results**: Ensure pages are ingested

## 🎯 Success Checklist

- [ ] Read [GETTING_STARTED.md](GETTING_STARTED.md)
- [ ] Configured `.env` file
- [ ] Installed backend dependencies
- [ ] Installed frontend dependencies
- [ ] Started backend successfully
- [ ] Started frontend successfully
- [ ] Ingested at least one Confluence page
- [ ] Asked a question and got an answer
- [ ] Verified source references work

## 🚀 Next Steps

1. **If you haven't started**: Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. **If you're set up**: Start ingesting more pages
3. **If you're running**: Explore the [README.md](README.md) for advanced features
4. **If you're extending**: Check [memory-bank/](memory-bank/) for architecture

---

**Welcome to your Confluence RAG System!** 🎉

Start with [GETTING_STARTED.md](GETTING_STARTED.md) and you'll be asking questions in minutes!

