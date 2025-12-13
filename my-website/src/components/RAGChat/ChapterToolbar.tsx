import React from 'react';
import './ChapterToolbar.css';

const ChapterToolbar = () => {
  return (
    <div className="chapter-toolbar">
      <button className="toolbar-btn" title="Personalize (Coming Soon)">
        🎯
      </button>
      <button className="toolbar-btn" title="Translate (Coming Soon)">
        🌍
      </button>
      <button
        className="toolbar-btn active"
        title="Ask AI about this chapter"
        onClick={() => {
          // Open the chat widget and potentially send a general question about the chapter
          // This would trigger the chat widget to open
          const event = new CustomEvent('openRAGChat', { detail: { type: 'chapter-overview' } });
          document.dispatchEvent(event);
        }}
      >
        💬
      </button>
    </div>
  );
};

export default ChapterToolbar;