// import React, { useState, useEffect, useRef } from 'react';
// import './ChatWidget.css';

// const ChatWidget = () => {
//   const [isOpen, setIsOpen] = useState(false);
//   const [messages, setMessages] = useState([]);
//   const [inputValue, setInputValue] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [selectedText, setSelectedText] = useState(null);
//   const [isFullView, setIsFullView] = useState(false);
//   const messagesEndRef = useRef(null);
//   const inputRef = useRef(null);

//   // Function to scroll to bottom of messages
//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   // Function to handle sending a message
//   const handleSendMessage = async () => {
//     if (!inputValue.trim() || isLoading) return;

//     const userMessage = {
//       id: Date.now(),
//       text: inputValue,
//       sender: 'user',
//       timestamp: new Date().toISOString()
//     };

//     // Add user message to chat
//     setMessages(prev => [...prev, userMessage]);
//     setInputValue('');
//     setIsLoading(true);

//     try {
//       // Prepare the request payload
//       const requestBody = {
//         text: inputValue,
//         selected_text: selectedText
//       };

//       // Call the backend API
//       const response = await fetch('/api/v1/query', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(requestBody)
//       });

//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//       }

//       const data = await response.json();

//       // Create assistant message with sources
//       const assistantMessage = {
//         id: Date.now() + 1,
//         text: data.response || 'I found some relevant information for your query.',
//         sender: 'assistant',
//         sources: data.provenance || [],
//         timestamp: new Date().toISOString()
//       };

//       setMessages(prev => [...prev, assistantMessage]);
//     } catch (error) {
//       console.error('Error sending message:', error);
//       const errorMessage = {
//         id: Date.now() + 1,
//         text: 'Sorry, I encountered an error processing your request. Please try again.',
//         sender: 'assistant',
//         timestamp: new Date().toISOString()
//       };
//       setMessages(prev => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // Handle Enter key press
//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSendMessage();
//     }
//   };

//   // Toggle chat window
//   const toggleChat = () => {
//     setIsOpen(!isOpen);
//     if (!isOpen) {
//       setTimeout(() => inputRef.current?.focus(), 100);
//     }
//   };

//   // Toggle full view
//   const toggleFullView = () => {
//     setIsFullView(!isFullView);
//   };

//   // Function to handle text selection
//   useEffect(() => {
//     const handleSelection = () => {
//       const selectedText = window.getSelection().toString().trim();
//       if (selectedText) {
//         setSelectedText(selectedText);
//       } else {
//         setSelectedText(null);
//       }
//     };

//     document.addEventListener('mouseup', handleSelection);
//     return () => {
//       document.removeEventListener('mouseup', handleSelection);
//     };
//   }, []);

//   // Handle custom event to open chat from chapter toolbar
//   useEffect(() => {
//     const handleOpenChat = () => {
//       setIsOpen(true);
//       setTimeout(() => inputRef.current?.focus(), 100);
//     };

//     document.addEventListener('openRAGChat', handleOpenChat);
//     return () => {
//       document.removeEventListener('openRAGChat', handleOpenChat);
//     };
//   }, []);

//   // Render source links
//   const renderSources = (sources) => {
//     if (!sources || sources.length === 0) return null;

//     return (
//       <div className="sources-container">
//         <div className="sources-header">Sources:</div>
//         <ul className="sources-list">
//           {sources.map((source, index) => (
//             <li key={index} className="source-item">
//               <a href="#" onClick={(e) => e.preventDefault()}>
//                 {source.doc_id || `Source ${index + 1}`}
//               </a>
//             </li>
//           ))}
//         </ul>
//       </div>
//     );
//   };

//   // Show a small CTA when text is selected
//   if (selectedText && !isOpen) {
//     return (
//       <div className="text-selection-cta" onClick={() => {
//         setIsOpen(true);
//         setTimeout(() => inputRef.current?.focus(), 100);
//       }}>
//         Ask about this selection
//       </div>
//     );
//   }

//   return (
//     <div className={`chat-widget ${isFullView ? 'full-view' : ''}`}>
//       {isOpen ? (
//         <div className={`chat-container ${isFullView ? 'full-view' : ''}`}>
//           <div className="chat-header">
//             <div className="chat-title">AI Assistant</div>
//             <div className="chat-actions">
//               <button
//                 className="chat-action-btn"
//                 onClick={toggleFullView}
//                 title={isFullView ? "Minimize" : "Expand"}
//               >
//                 {isFullView ? "−" : "□"}
//               </button>
//               <button
//                 className="chat-action-btn close-btn"
//                 onClick={toggleChat}
//               >
//                 ×
//               </button>
//             </div>
//           </div>

//           <div className="chat-messages">
//             {messages.length === 0 ? (
//               <div className="welcome-message">
//                 <h3>Ask me anything about the textbook!</h3>
//                 <p>I can help answer questions based on the content.</p>
//               </div>
//             ) : (
//               messages.map((message) => (
//                 <div
//                   key={message.id}
//                   className={`message ${message.sender}`}
//                 >
//                   <div className="message-content">
//                     {message.text}
//                   </div>
//                   {message.sender === 'assistant' && renderSources(message.sources)}
//                 </div>
//               ))
//             )}
//             {isLoading && (
//               <div className="message assistant">
//                 <div className="message-content">
//                   <div className="typing-indicator">
//                     <span></span>
//                     <span></span>
//                     <span></span>
//                   </div>
//                 </div>
//               </div>
//             )}
//             <div ref={messagesEndRef} />
//           </div>

//           <div className="chat-input-area">
//             <textarea
//               ref={inputRef}
//               value={inputValue}
//               onChange={(e) => setInputValue(e.target.value)}
//               onKeyPress={handleKeyPress}
//               placeholder="Ask a question about the content..."
//               rows="1"
//               disabled={isLoading}
//               className="chat-input"
//             />
//             <button
//               onClick={handleSendMessage}
//               disabled={!inputValue.trim() || isLoading}
//               className="send-button"
//             >
//               {isLoading ? 'Sending...' : 'Send'}
//             </button>
//           </div>
//         </div>
//       ) : (
//         <button className="chat-toggle-button" onClick={toggleChat}>
//           💬
//         </button>
//       )}
//     </div>
//   );
// };

// export default ChatWidget;

import React, { useState, useEffect, useRef } from 'react';
import './ChatWidget.css';

const SESSION_ID = 'frontend-session';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFullView, setIsFullView] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue;

    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        text: userText,
        sender: 'user'
      }
    ]);

    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/routes/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           query_text: inputValue, // <-- previously text: inputValue
           session_id: SESSION_ID
          
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          text: data.answer || 'No answer available.',
          sender: 'assistant',
          sources: data.citations || []
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          text: 'Sorry, I encountered an error processing your request.',
          sender: 'assistant'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`chat-widget ${isFullView ? 'full-view' : ''}`}>
      {isOpen ? (
        <div className="chat-container">
          <div className="chat-header">
            <div className="chat-title">AI Assistant</div>
            <div className="chat-actions">
              <button onClick={() => setIsFullView(!isFullView)}>
                {isFullView ? '−' : '□'}
              </button>
              <button onClick={() => setIsOpen(false)}>×</button>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                Ask me anything about the book.
              </div>
            )}

            {messages.map(msg => (
              <div key={msg.id} className={`message ${msg.sender}`}>
                <div className="message-content">{msg.text}</div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="message-content">Typing...</div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask something..."
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              Send
            </button>
          </div>
        </div>
      ) : (
        <button className="chat-toggle-button" onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}
    </div>
  );
};

export default ChatWidget;
