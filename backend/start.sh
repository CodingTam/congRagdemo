#!/bin/bash

# Start script for Confluence RAG Backend

echo "🚀 Starting Confluence RAG Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the API
echo "✅ Starting FastAPI server on port 8000..."
python api.py

