import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, isStreaming }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">{isUser ? '👤' : '⚖️'}</div>
      <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
        {isStreaming && <span className="cursor-blink">▊</span>}
      </div>
    </div>
  );
};

export default ChatMessage;
