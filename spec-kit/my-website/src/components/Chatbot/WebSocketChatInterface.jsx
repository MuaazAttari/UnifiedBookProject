import React, { useState, useEffect, useRef } from 'react';
import './Chatbot.css';

/**
 * A WebSocket-based chat interface for real-time communication with the backend.
 */
const WebSocketChatInterface = ({ contextType = 'full_book', selectedText = null, chapterTitle = null }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentContext, setCurrentContext] = useState(contextType);
  const [displayedSelectedText, setDisplayedSelectedText] = useState(selectedText);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsConnecting, setWsConnecting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Initialize session ID and load chat history
  useEffect(() => {
    // Generate or retrieve session ID
    let currentSessionId = localStorage.getItem('chatSessionId');
    if (!currentSessionId) {
      currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('chatSessionId', currentSessionId);
    }
    setSessionId(currentSessionId);

    // Load chat history from localStorage for this session
    const savedMessages = localStorage.getItem(`chatHistory_${currentSessionId}`);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Error loading chat history:', e);
        setMessages([]);
      }
    }
  }, []);

  // WebSocket connection management
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      disconnectWebSocket();
    };
  }, []);

  const connectWebSocket = () => {
    if (wsConnecting || wsConnected) return;

    setWsConnecting(true);

    // Try to get user ID from auth context if available
    const userId = localStorage.getItem('userId') || 'anonymous';

    // Construct WebSocket URL based on current environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${userId}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        setWsConnecting(false);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'chat_response') {
            const botMessage = {
              id: Date.now() + 1,
              text: data.response.answer,
              sender: 'bot',
              sources: data.response.sources || [],
              timestamp: new Date(),
              tokensUsed: data.response.tokens_used,
              confidence: data.response.confidence,
              confidencePercentage: data.response.confidence_percentage || Math.round((data.response.confidence || 0) * 100)
            };
            setMessages(prev => {
              const newMessages = [...prev, botMessage];
              // Save to localStorage
              if (sessionId) {
                localStorage.setItem(`chatHistory_${sessionId}`, JSON.stringify(newMessages));
              }
              return newMessages;
            });
            setIsLoading(false);
          } else if (data.type === 'typing') {
            // Handle typing indicator
            setIsLoading(data.status);
          } else if (data.type === 'error') {
            const errorMessage = {
              id: Date.now() + 1,
              text: `Error: ${data.message}`,
              sender: 'bot',
              error: true,
              timestamp: new Date()
            };
            setMessages(prev => {
              const newMessages = [...prev, errorMessage];
              // Save to localStorage
              if (sessionId) {
                localStorage.setItem(`chatHistory_${sessionId}`, JSON.stringify(newMessages));
              }
              return newMessages;
            });
            setIsLoading(false);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setWsConnected(false);
        setWsConnecting(false);

        // Attempt to reconnect after a delay
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000); // Reconnect after 3 seconds
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
        setWsConnecting(false);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setWsConnecting(false);

      // Attempt to reconnect after a delay
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 3000);
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading || !wsConnected) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    const newMessages = [...prev, userMessage];
    setMessages(newMessages);
    // Save to localStorage
    if (sessionId) {
      localStorage.setItem(`chatHistory_${sessionId}`, JSON.stringify(newMessages));
    }
    setInputValue('');
    setIsLoading(true);

    // Send message via WebSocket
    const messageData = {
      type: 'chat_message',
      query: inputValue,
      context_type: currentContext,
      selected_text: currentContext === 'selected_text' ? displayedSelectedText : null,
      user_id: localStorage.getItem('userId') || null
    };

    try {
      wsRef.current.send(JSON.stringify(messageData));
    } catch (error) {
      console.error('Error sending message via WebSocket:', error);

      const errorMessage = {
        id: Date.now() + 1,
        text: 'Failed to send message. Please try again.',
        sender: 'bot',
        error: true,
        timestamp: new Date()
      };

      setMessages(prev => {
        const newMessages = [...prev, errorMessage];
        // Save to localStorage
        if (sessionId) {
          localStorage.setItem(`chatHistory_${sessionId}`, JSON.stringify(newMessages));
        }
        return newMessages;
      });
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChatHistory = () => {
    setMessages([]);
    if (sessionId) {
      localStorage.removeItem(`chatHistory_${sessionId}`);
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

  // Connection status indicator
  const connectionStatus = wsConnected ? (
    <span className="connection-status connected">● Connected</span>
  ) : wsConnecting ? (
    <span className="connection-status connecting">● Connecting...</span>
  ) : (
    <span className="connection-status disconnected">● Disconnected</span>
  );

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <div className="context-selector">
          <button
            className={`context-btn ${currentContext === 'full_book' ? 'active' : ''}`}
            onClick={() => switchContext('full_book')}
            disabled={isLoading}
            title="Ask questions about the full textbook content"
          >
            Full Book
          </button>
          <button
            className={`context-btn ${currentContext === 'selected_text' ? 'active' : ''}`}
            onClick={() => switchContext('selected_text')}
            disabled={isLoading || !selectedText}
            title={selectedText ? 'Ask questions about the selected text' : 'No text selected'}
          >
            Selected Text
          </button>
          <button
            className="context-btn clear-history-btn"
            onClick={clearChatHistory}
            disabled={isLoading || messages.length === 0}
            title="Clear chat history"
          >
            Clear Chat
          </button>
        </div>
        <div className="context-indicator">
          <span className="context-label">Context: {getContextDisplay()}</span>
          {connectionStatus}
        </div>
      </div>

      {currentContext === 'selected_text' && displayedSelectedText && (
        <div className="selected-text-preview">
          <details>
            <summary>
              <strong>Selected Text Preview:</strong>
            </summary>
            <div className="selected-text-content">
              "{displayedSelectedText.substring(0, 200)}{displayedSelectedText.length > 200 ? '...' : ''}"
            </div>
          </details>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h4>Textbook Assistant</h4>
            <p>Ask me questions about the {chapterTitle ? chapterTitle : 'textbook'} content.</p>
            <p>I can answer from the <strong>full book</strong> or from <strong>selected text</strong> when available.</p>
            {currentContext === 'selected_text' && displayedSelectedText && (
              <p>Currently using selected text context.</p>
            )}
            {!wsConnected && (
              <p><em>Connecting to real-time service...</em></p>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender}-message ${message.error ? 'error' : ''}`}
            >
              <div className="message-content">
                {message.sender === 'bot' && message.confidencePercentage !== undefined && (
                  <div className="confidence-indicator">
                    Confidence: {message.confidencePercentage}%
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
                            {source.relevance_score && (
                              <span className="relevance-score"> (Score: {source.relevance_score.toFixed(2)})</span>
                            )}
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
        {isLoading && !messages.find(m => m.id === 'typing-indicator') && (
          <div key="typing-indicator" className="message bot-message">
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
          placeholder={`Ask a question${wsConnected ? '' : ' (connecting...)'}...`}
          disabled={!wsConnected || isLoading}
          rows="1"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isLoading || !wsConnected}
          className="send-button"
        >
          {isLoading ? (
            <span className="loading-spinner">●●●</span>
          ) : (
            'Send'
          )}
        </button>
      </form>
    </div>
  );
};

export default WebSocketChatInterface;