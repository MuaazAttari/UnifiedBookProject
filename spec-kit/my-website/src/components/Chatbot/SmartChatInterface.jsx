import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './ChatInterface';

/**
 * A smart chat interface that can detect selected text on the page
 * and automatically switch between full book and selected text context.
 */
const SmartChatInterface = ({ contextType = 'full_book', chapterTitle = null }) => {
  const [selectedText, setSelectedText] = useState(null);
  const [autoContext, setAutoContext] = useState(contextType);
  const containerRef = useRef(null);

  // Function to get selected text from the page
  const getSelectedText = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim() !== '') {
      const selected = selection.toString().trim();
      if (selected.length > 0) {
        return selected;
      }
    }
    return null;
  };

  // Function to handle text selection on the page
  const handleSelectionChange = () => {
    const text = getSelectedText();
    if (text) {
      setSelectedText(text);
      setAutoContext('selected_text');
    } else {
      setSelectedText(null);
      setAutoContext(contextType); // Revert to original context type
    }
  };

  // Set up event listeners for text selection
  useEffect(() => {
    const handleMouseUp = () => {
      setTimeout(handleSelectionChange, 0); // Use timeout to ensure selection is complete
    };

    const handleKeyUp = (e) => {
      if (e.key === 'Escape') {
        // Clear selection when escape is pressed
        window.getSelection().removeAllRanges();
        setSelectedText(null);
        setAutoContext(contextType);
      }
    };

    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keyup', handleKeyUp);

    // Also check for selection when component mounts
    handleSelectionChange();

    // Clean up event listeners
    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [contextType]);

  // If we have selected text, use selected_text context, otherwise use the original context
  const effectiveContext = selectedText ? 'selected_text' : contextType;

  return (
    <div ref={containerRef} className="smart-chat-container">
      <ChatInterface
        contextType={effectiveContext}
        selectedText={selectedText}
        chapterTitle={chapterTitle}
      />

      {selectedText && (
        <div className="selection-indicator">
          <small>Using selected text: "{selectedText.substring(0, 50)}{selectedText.length > 50 ? '...' : ''}"</small>
        </div>
      )}
    </div>
  );
};

export default SmartChatInterface;