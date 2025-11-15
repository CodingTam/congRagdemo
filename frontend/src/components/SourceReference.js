import React, { useState } from 'react';
import './SourceReference.css';

function SourceReference({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="source-reference">
      <button 
        className="source-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        📄 {sources.length} Source{sources.length > 1 ? 's' : ''} Referenced
        <span className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </button>
      
      {isExpanded && (
        <div className="source-list">
          {sources.map((source, index) => (
            <div key={index} className="source-card">
              <div className="source-header">
                <h4 className="source-title">{source.page_title}</h4>
                <span className="relevance-badge">
                  {Math.round(source.relevance_score * 100)}% relevant
                </span>
              </div>
              <a 
                href={source.page_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="source-link"
              >
                🔗 View in Confluence
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SourceReference;

