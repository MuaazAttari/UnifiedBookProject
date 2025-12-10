import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';

const Chatbot = ({ contextType = 'full_book', selectedText = null }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentContext, setCurrentContext] = useState(contextType);
  const [displayedSelectedText, setDisplayedSelectedText] = useState(selectedText);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle context switching
  const switchContext = (newContext) => {
    setCurrentContext(newContext);
    if (newContext === 'full_book') {
      setDisplayedSelectedText(null);
    } else if (newContext === 'selected_text' && selectedText) {
      setDisplayedSelectedText(selectedText);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare the request body based on context
      const requestBody = {
        query: inputValue,
        context_type: currentContext,
        ...(currentContext === 'selected_text' && displayedSelectedText && { selected_text: displayedSelectedText })
      };

      // Call the backend API
      const response = await fetch('/api/v1/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'bot',
        sources: data.sources || [],
        timestamp: new Date(),
        tokensUsed: data.tokens_used,
        confidence: data.confidence
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        error: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Function to get context display text
  const getContextDisplay = () => {
    if (currentContext === 'full_book') {
      return 'Full Book Context';
    } else if (currentContext === 'selected_text' && displayedSelectedText) {
      return 'Selected Text Context';
    }
    return 'Context';
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <div className="context-selector">
          <button
            className={`context-btn ${currentContext === 'full_book' ? 'active' : ''}`}
            onClick={() => switchContext('full_book')}
            disabled={isLoading}
          >
            Full Book
          </button>
          <button
            className={`context-btn ${currentContext === 'selected_text' ? 'active' : ''}`}
            onClick={() => switchContext('selected_text')}
            disabled={isLoading || !selectedText}
            title={!selectedText ? 'No text selected' : ''}
          >
            Selected Text
          </button>
        </div>
        <div className="context-indicator">
          <span className="context-label">Context: {getContextDisplay()}</span>
        </div>
      </div>

      {currentContext === 'selected_text' && displayedSelectedText && (
        <div className="selected-text-preview">
          <div className="selected-text-content">
            <strong>Selected Text:</strong> {displayedSelectedText.substring(0, 100)}{displayedSelectedText.length > 100 ? '...' : ''}
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your textbook assistant. Ask me questions about the content.</p>
            <p>I can answer from the <strong>full book</strong> or from <strong>selected text</strong> when available.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender}-message ${message.error ? 'error' : ''}`}
            >
              <div className="message-content">
                {message.sender === 'bot' && message.confidence !== undefined && (
                  <div className="confidence-indicator">
                    Confidence: {Math.round(message.confidence * 100)}%
                  </div>
                )}
                <div className="message-text">{message.text}</div>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <details>
                      <summary>Sources ({message.sources.length})</summary>
                      <ul>
                        {message.sources.map((source, index) => (
                          <li key={index}>
                            {source.title || source.source || `Source ${index + 1}`}
                          </li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the textbook content..."
          disabled={isLoading}
          rows="1"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default Chatbot;