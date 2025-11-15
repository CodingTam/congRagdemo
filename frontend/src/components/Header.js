import React from 'react';
import './Header.css';

function Header({ status, onClear }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">Global Team Chatbot</h1>
          <p className="header-subtitle">Ask questions about our internal documentation</p>
        </div>
        
        <div className="header-right">
          {status && (
            <div className="status-indicator">
              <div className={`status-dot ${status.confluence_connected ? 'connected' : 'disconnected'}`}></div>
              <span className="status-text">
                {status.documents_indexed} pages indexed · {status.total_chunks} chunks
              </span>
            </div>
          )}
          
          <button className="clear-button" onClick={onClear} title="Clear conversation">
            🗑️ Clear
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;

