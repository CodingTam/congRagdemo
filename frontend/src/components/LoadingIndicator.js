import React from 'react';
import './LoadingIndicator.css';

function LoadingIndicator({ message }) {
  return (
    <div className="loading-indicator">
      <div className="loading-content">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        {message && <div className="loading-message">{message}</div>}
      </div>
    </div>
  );
}

export default LoadingIndicator;

