import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { queryDocumentStream } from '../services/api';

const ChatInterface = ({ session, onNewSession }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Document **"${session.filename}"** loaded successfully.\n\n${session.page_count} pages · ${session.chunk_count} indexed segments\n\nAsk me anything about this document.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || isStreaming) return;
    const question = input.trim();
    setInput('');

    setMessages((prev) => [...prev, { role: 'user', content: question }]);

    // Add placeholder for streaming response
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);
    setIsStreaming(true);

    queryDocumentStream(
      session.session_id,
      question,
      (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: updated[updated.length - 1].content + chunk,
          };
          return updated;
        });
      },
      () => setIsStreaming(false),
      (err) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: `⚠️ Error: ${err}`,
          };
          return updated;
        });
        setIsStreaming(false);
      }
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const SAMPLE_QUERIES = [
    'What are the termination clauses?',
    'Summarize the key obligations of each party.',
    'What is the governing law?',
    'Are there any penalty clauses?',
  ];

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-doc-info">
          <span className="doc-icon">📄</span>
          <span className="doc-name">{session.filename}</span>
        </div>
        <button className="new-session-btn" onClick={onNewSession}>
          + New Document
        </button>
      </div>

      <div className="messages-list">
        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            message={msg}
            isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'assistant'}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="sample-queries">
          <p className="sample-label">Try asking:</p>
          <div className="sample-chips">
            {SAMPLE_QUERIES.map((q) => (
              <button key={q} className="chip" onClick={() => setInput(q)}>
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="input-area">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the document…"
          rows={2}
          disabled={isStreaming}
        />
        <button
          className="send-btn"
          onClick={sendMessage}
          disabled={!input.trim() || isStreaming}
        >
          {isStreaming ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
