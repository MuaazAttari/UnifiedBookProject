import React, { useState, useEffect } from 'react';
import './TranslateToUrduButton.css';

const TranslateToUrduButton = ({ content, chapterId = null, onTranslate }) => {
  const [translatedContent, setTranslatedContent] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [error, setError] = useState('');
  const [showOriginal, setShowOriginal] = useState(false);

  const handleTranslate = async () => {
    if (!content) {
      setError('No content to translate');
      return;
    }

    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('Please log in to use translation feature');
      return;
    }

    setIsTranslating(true);
    setError('');

    try {
      // Call the translation API
      const requestBody = {
        text: content,
        target_language: 'ur',
        source_language: 'en'
      };

      const response = await fetch('/api/v1/translation/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTranslatedContent(data.translated_text);
      setIsTranslated(true);

      // Call the callback if provided
      if (onTranslate) {
        onTranslate(data);
      }
    } catch (err) {
      console.error('Translation error:', err);
      setError(err.message || 'Translation failed. Please try again.');
    } finally {
      setIsTranslating(false);
    }
  };

  const toggleContent = () => {
    setShowOriginal(!showOriginal);
  };

  const getDisplayContent = () => {
    if (isTranslated && !showOriginal) {
      return translatedContent;
    }
    return content;
  };

  const getButtonText = () => {
    if (isTranslating) return 'Translating...';
    if (isTranslated) return showOriginal ? 'Show Urdu' : 'Show Original';
    return '.Translate to Urdu';
  };

  const getButtonIcon = () => {
    if (isTranslating) return '🔄';
    if (isTranslated) return showOriginal ? '🇺🇸' : '🇵🇰';
    return '🇵🇰';
  };

  return (
    <div className="translate-to-urdu-container">
      <button
        className={`translate-button ${isTranslating ? 'translating' : ''} ${isTranslated ? 'translated' : ''}`}
        onClick={isTranslated ? toggleContent : handleTranslate}
        disabled={isTranslating}
        title={isTranslated ? 'Toggle between original and Urdu' : 'Translate content to Urdu'}
      >
        <span className="button-icon">{getButtonIcon()}</span>
        <span className="button-text">{getButtonText()}</span>
      </button>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="translated-content">
        {getDisplayContent()}
      </div>

      {isTranslated && (
        <div className="translation-info">
          <small>Content translated from English to Urdu</small>
        </div>
      )}
    </div>
  );
};

export default TranslateToUrduButton;