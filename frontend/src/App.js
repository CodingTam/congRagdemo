import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import SearchBox from './components/SearchBox';
import LoadingIndicator from './components/LoadingIndicator';
import SourceReference from './components/SourceReference';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [status, setStatus] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch status on mount
  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const handleSendMessage = async (question) => {
    if (!question.trim()) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Show loading
    setIsLoading(true);
    setLoadingMessage('🔍 Searching knowledge base...');

    try {
      // Query the API
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        question: question
      });

      setLoadingMessage('✨ Generating response...');

      // Add bot response
      const botMessage = {
        type: 'bot',
        content: response.data.answer,
        sources: response.data.sources,
        chunks_used: response.data.chunks_used,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error querying:', error);
      
      // Add error message
      const errorMessage = {
        type: 'bot',
        content: '⚠️ Sorry, I encountered an error processing your question. Please try again.',
        sources: [],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleClearConversation = () => {
    setMessages([]);
  };

  return (
    <div className="App">
      <Header status={status} onClear={handleClearConversation} />
      
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>👋 Welcome to the Global Team Chatbot</h2>
              <p>Ask me anything about our internal documentation and processes.</p>
              <div className="example-questions">
                <p><strong>Try asking:</strong></p>
                <ul>
                  <li>"How do I deploy the framework?"</li>
                  <li>"What are the steps for setting up the environment?"</li>
                  <li>"Where can I find the API documentation?"</li>
                </ul>
              </div>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div key={index}>
              <ChatMessage message={message} />
              {message.type === 'bot' && message.sources && message.sources.length > 0 && (
                <SourceReference sources={message.sources} />
              )}
            </div>
          ))}
          
          {isLoading && <LoadingIndicator message={loadingMessage} />}
          
          <div ref={messagesEndRef} />
        </div>
        
        <SearchBox onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

export default App;
