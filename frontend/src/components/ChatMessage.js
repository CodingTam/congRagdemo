import React from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {
  const formatContent = (content) => {
    // Simple formatting for numbered lists and code blocks
    const lines = content.split('\n');
    const formatted = [];
    let inCodeBlock = false;
    let codeLines = [];
    
    lines.forEach((line, index) => {
      // Check for code block markers
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          // End of code block
          formatted.push(
            <pre key={`code-${index}`} className="code-block">
              <code>{codeLines.join('\n')}</code>
            </pre>
          );
          codeLines = [];
          inCodeBlock = false;
        } else {
          // Start of code block
          inCodeBlock = true;
        }
        return;
      }
      
      if (inCodeBlock) {
        codeLines.push(line);
        return;
      }
      
      // Format bold text
      const boldFormatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Check for numbered list items
      if (/^\d+\./.test(line.trim())) {
        formatted.push(
          <div key={index} className="numbered-item" dangerouslySetInnerHTML={{ __html: boldFormatted }} />
        );
      } else if (line.trim()) {
        formatted.push(
          <p key={index} dangerouslySetInnerHTML={{ __html: boldFormatted }} />
        );
      }
    });
    
    return formatted;
  };

  return (
    <div className={`chat-message ${message.type}`}>
      <div className="message-avatar">
        {message.type === 'user' ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-text">
          {formatContent(message.content)}
        </div>
        <div className="message-timestamp">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;

