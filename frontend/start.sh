#!/bin/bash

# Start script for Confluence RAG Frontend

echo "🚀 Starting Confluence RAG Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found!"
    echo "Please run: npm install"
    exit 1
fi

# Start the development server
echo "✅ Starting React development server on port 3000..."
npm start

