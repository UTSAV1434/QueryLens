import { useState, useRef, useEffect } from "react";

const SAMPLE_QUERIES = [
  "Show total revenue by region",
  "Monthly sales trend over time",
  "Top 10 products by revenue",
  "Compare profit across categories",
  "Revenue by region for Q3 2024",
  "Units sold distribution",
];

export default function ChatPanel({ messages, onSendQuery, isLoading, onUndo }) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendQuery(input.trim());
    setInput("");
  };

  const handleSuggestionClick = (query) => {
    if (isLoading) return;
    onSendQuery(query);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const canUndo = messages.length >= 2 && messages[messages.length - 1].type === "assistant" && messages[messages.length - 2].type === "user";

  return (
    <aside className="chat-panel">
      <div className="chat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Ask your data
          </h3>
          <p>Type a question in plain English</p>
        </div>
        <button 
          onClick={onUndo} 
          disabled={!canUndo || isLoading}
          style={{ 
            background: 'transparent', 
            border: '1px solid var(--border-glass)', 
            padding: '6px 12px', 
            borderRadius: '6px', 
            color: (canUndo && !isLoading) ? 'var(--text-primary)' : 'var(--text-muted)',
            cursor: (canUndo && !isLoading) ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px'
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 7v6h6" />
            <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
          </svg>
          Undo
        </button>
      </div>

      <div className="suggested-queries">
        <div className="suggested-queries-title">Try asking</div>
        <div className="suggested-queries-list">
          {SAMPLE_QUERIES.map((q, i) => (
            <button
              key={i}
              className="suggested-query-btn"
              onClick={() => handleSuggestionClick(q)}
              disabled={isLoading}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="message assistant">
            <div className="msg-label">QueryLens</div>
            Hi! 👋 I can help you explore your data. Upload a CSV or ask a question about the loaded dataset.
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.type}`}>
            {msg.type === "user" && <div className="msg-label">You</div>}
            {msg.type === "assistant" && <div className="msg-label">QueryLens</div>}
            {msg.type === "error" && <div className="msg-label">Error</div>}
            {msg.text}
          </div>
        ))}

        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="loading-text">Analyzing your data...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSubmit}>
        <div className="chat-input-wrapper">
          <textarea
            className="chat-input"
            placeholder="Ask about your data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            id="query-input"
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || isLoading}
            id="send-query-btn"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "2px" }}>
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </form>
    </aside>
  );
}
