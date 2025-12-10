import React, { useState, useEffect } from 'react';
import './PersonalizeChapterButton.css';

const PersonalizeChapterButton = ({ chapterId, chapterTitle = "this chapter", onPersonalize }) => {
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [personalizationSettings, setPersonalizationSettings] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if personalization exists for this chapter
  useEffect(() => {
    checkPersonalizationStatus();
  }, [chapterId]);

  const checkPersonalizationStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) return;

      const response = await fetch(`/api/v1/personalization/chapters/${chapterId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setIsPersonalized(data.personalization_enabled);
        setPersonalizationSettings(data);
      }
    } catch (err) {
      console.error('Error checking personalization status:', err);
    }
  };

  const togglePersonalization = async () => {
    if (!chapterId) {
      setError('Chapter ID is required');
      return;
    }

    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('Please log in to personalize content');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      if (isPersonalized) {
        // Disable personalization
        const response = await fetch(`/api/v1/personalization/chapters/${chapterId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            personalization_enabled: false
          })
        });

        if (!response.ok) {
          throw new Error('Failed to disable personalization');
        }

        const data = await response.json();
        setIsPersonalized(false);
        setPersonalizationSettings(data);

        // Call the callback if provided
        if (onPersonalize) {
          onPersonalize({ enabled: false, settings: data });
        }
      } else {
        // Enable personalization with default settings
        const response = await fetch(`/api/v1/personalization/chapters/${chapterId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            personalization_enabled: true,
            difficulty_level: 'intermediate', // Default to user's level
            learning_style: 'theoretical' // Default to user's preference
          })
        });

        if (!response.ok) {
          throw new Error('Failed to enable personalization');
        }

        const data = await response.json();
        setIsPersonalized(true);
        setPersonalizationSettings(data);

        // Call the callback if provided
        if (onPersonalize) {
          onPersonalize({ enabled: true, settings: data });
        }
      }
    } catch (err) {
      console.error('Error toggling personalization:', err);
      setError(err.message || 'Failed to update personalization settings');
    } finally {
      setIsLoading(false);
    }
  };

  const adjustContent = async (content) => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('Please log in to personalize content');
      return content;
    }

    try {
      const response = await fetch('/api/v1/personalization/adjust-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: content,
          chapter_id: chapterId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to adjust content');
      }

      const data = await response.json();
      return data.adjusted_content;
    } catch (err) {
      console.error('Error adjusting content:', err);
      setError(err.message || 'Failed to adjust content');
      return content; // Return original content if adjustment fails
    }
  };

  const getButtonText = () => {
    if (isLoading) return 'Processing...';
    return isPersonalized ? `Personalized for ${chapterTitle}` : `Personalize ${chapterTitle}`;
  };

  const getButtonIcon = () => {
    if (isLoading) return '🔄';
    return isPersonalized ? '✅' : '✨';
  };

  return (
    <div className="personalize-chapter-container">
      <button
        className={`personalize-button ${isPersonalized ? 'enabled' : 'disabled'} ${isLoading ? 'loading' : ''}`}
        onClick={togglePersonalization}
        disabled={isLoading}
        title={isPersonalized ? `Content is personalized for you` : `Personalize this content for your learning style`}
      >
        <span className="button-icon">{getButtonIcon()}</span>
        <span className="button-text">{getButtonText()}</span>
      </button>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {showSettings && personalizationSettings && (
        <div className="personalization-settings">
          <h4>Personalization Settings</h4>
          <p><strong>Difficulty:</strong> {personalizationSettings.difficulty_level || 'Not set'}</p>
          <p><strong>Learning Style:</strong> {personalizationSettings.learning_style || 'Not set'}</p>
          <button onClick={() => setShowSettings(false)}>Close</button>
        </div>
      )}

      <div className="personalization-info">
        {isPersonalized ? (
          <small>Content adjusted based on your preferences and experience level</small>
        ) : (
          <small>Enable to customize content to your learning style and experience</small>
        )}
      </div>
    </div>
  );
};

export default PersonalizeChapterButton;