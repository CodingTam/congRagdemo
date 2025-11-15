import React, { useState } from 'react';
import './SearchBox.css';

function SearchBox({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="search-box-container">
      <form onSubmit={handleSubmit} className="search-box">
        <textarea
          className="search-input"
          placeholder="Ask me anything about our processes..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows="1"
        />
        <button 
          type="submit" 
          className="send-button" 
          disabled={disabled || !input.trim()}
        >
          <span className="send-icon">➤</span>
        </button>
      </form>
      <div className="search-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}

export default SearchBox;

