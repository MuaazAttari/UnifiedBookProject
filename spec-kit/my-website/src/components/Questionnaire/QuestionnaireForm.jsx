import React, { useState, useEffect } from 'react';
import './QuestionnaireForm.css';

const QuestionnaireForm = ({ onSubmit, initialData = null, userId = null }) => {
  const [formData, setFormData] = useState({
    education_level: '',
    technical_background: '',
    learning_goals: '',
    preferred_learning_style: '',
    experience_with_ai: '',
    experience_with_robotics: '',
    timezone: '',
    additional_notes: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  // Load initial data if provided
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({
        ...prev,
        ...initialData
      }));
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('authToken');

      if (!token) {
        throw new Error('Not authenticated. Please log in first.');
      }

      // Prepare the request
      const requestBody = {
        ...formData
      };

      // Submit the questionnaire
      const response = await fetch('/api/v1/auth/questionnaire', {
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

      const result = await response.json();

      setIsSubmitted(true);

      // Call the onSubmit callback if provided
      if (onSubmit) {
        onSubmit(result);
      }
    } catch (err) {
      console.error('Error submitting questionnaire:', err);
      setError(err.message || 'Failed to submit questionnaire. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="questionnaire-form-container">
        <div className="questionnaire-success">
          <h3>Thank You!</h3>
          <p>Your background information has been saved successfully.</p>
          <p>This will help us personalize your learning experience.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="questionnaire-form-container">
      <h2>Background Questionnaire</h2>
      <p className="questionnaire-intro">
        Please fill out this questionnaire to help us personalize your learning experience.
        All information is optional but helps us provide better recommendations.
      </p>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="questionnaire-form">
        <div className="form-group">
          <label htmlFor="education_level">
            Education Level:
          </label>
          <select
            id="education_level"
            name="education_level"
            value={formData.education_level}
            onChange={handleChange}
          >
            <option value="">Select your education level</option>
            <option value="high_school">High School</option>
            <option value="undergraduate">Undergraduate</option>
            <option value="graduate">Graduate</option>
            <option value="postgraduate">Postgraduate</option>
            <option value="professional">Professional/Industry</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="technical_background">
            Technical Background:
          </label>
          <textarea
            id="technical_background"
            name="technical_background"
            value={formData.technical_background}
            onChange={handleChange}
            placeholder="Describe your technical background, programming experience, etc."
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="learning_goals">
            Learning Goals:
          </label>
          <textarea
            id="learning_goals"
            name="learning_goals"
            value={formData.learning_goals}
            onChange={handleChange}
            placeholder="What do you hope to learn from this textbook?"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="preferred_learning_style">
            Preferred Learning Style:
          </label>
          <select
            id="preferred_learning_style"
            name="preferred_learning_style"
            value={formData.preferred_learning_style}
            onChange={handleChange}
          >
            <option value="">Select your preferred learning style</option>
            <option value="visual">Visual (diagrams, charts, videos)</option>
            <option value="hands_on">Hands-on (practical exercises)</option>
            <option value="theoretical">Theoretical (concepts, theory)</option>
            <option value="reading">Reading (text-based)</option>
            <option value="auditory">Auditory (lectures, discussions)</option>
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="experience_with_ai">
              Experience with AI:
            </label>
            <select
              id="experience_with_ai"
              name="experience_with_ai"
              value={formData.experience_with_ai}
              onChange={handleChange}
            >
              <option value="">Select level</option>
              <option value="none">No experience</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="experience_with_robotics">
              Experience with Robotics:
            </label>
            <select
              id="experience_with_robotics"
              name="experience_with_robotics"
              value={formData.experience_with_robotics}
              onChange={handleChange}
            >
              <option value="">Select level</option>
              <option value="none">No experience</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="timezone">
            Timezone:
          </label>
          <select
            id="timezone"
            name="timezone"
            value={formData.timezone}
            onChange={handleChange}
          >
            <option value="">Select your timezone</option>
            <option value="GMT-12">GMT-12: International Date Line West</option>
            <option value="GMT-11">GMT-11: Midway Island, Samoa</option>
            <option value="GMT-10">GMT-10: Hawaii</option>
            <option value="GMT-9">GMT-9: Alaska</option>
            <option value="GMT-8">GMT-8: Pacific Time (US & Canada)</option>
            <option value="GMT-7">GMT-7: Mountain Time (US & Canada)</option>
            <option value="GMT-6">GMT-6: Central Time (US & Canada)</option>
            <option value="GMT-5">GMT-5: Eastern Time (US & Canada)</option>
            <option value="GMT-4">GMT-4: Atlantic Time (Canada)</option>
            <option value="GMT-3">GMT-3: Brazil, Buenos Aires</option>
            <option value="GMT-2">GMT-2: Mid-Atlantic</option>
            <option value="GMT-1">GMT-1: Azores, Cape Verde Islands</option>
            <option value="GMT">GMT: Greenwich Mean Time</option>
            <option value="GMT+1">GMT+1: Central European Time</option>
            <option value="GMT+2">GMT+2: Eastern European Time</option>
            <option value="GMT+3">GMT+3: Moscow, St. Petersburg</option>
            <option value="GMT+4">GMT+4: Abu Dhabi, Muscat</option>
            <option value="GMT+5">GMT+5: Tashkent, Karachi</option>
            <option value="GMT+6">GMT+6: Almaty, Dhaka</option>
            <option value="GMT+7">GMT+7: Bangkok, Hanoi, Jakarta</option>
            <option value="GMT+8">GMT+8: Beijing, Singapore, Hong Kong</option>
            <option value="GMT+9">GMT+9: Tokyo, Seoul, Osaka</option>
            <option value="GMT+10">GMT+10: Sydney, Melbourne, Guam</option>
            <option value="GMT+11">GMT+11: Magadan, Solomon Islands</option>
            <option value="GMT+12">GMT+12: Auckland, Fiji, Marshall Islands</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="additional_notes">
            Additional Notes:
          </label>
          <textarea
            id="additional_notes"
            name="additional_notes"
            value={formData.additional_notes}
            onChange={handleChange}
            placeholder="Any additional information about your learning preferences or goals..."
            rows="3"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="submit-button"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Questionnaire'}
        </button>
      </form>
    </div>
  );
};

export default QuestionnaireForm;