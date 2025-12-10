import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Button,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup
} from '@mui/material';
import apiClient from '../../services/api-client';
import { UserPreferences } from '../../services/api-client';

interface FormatCustomizerProps {
  onPreferencesChange?: (preferences: UserPreferences) => void;
}

const FormatCustomizer: React.FC<FormatCustomizerProps> = ({ onPreferencesChange }) => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    default_educational_level: 'UNDERGRADUATE',
    default_format: 'PDF',
    default_style: 'academic',
    include_exercises_by_default: true,
    include_summaries_by_default: true,
    updated_at: new Date().toISOString()
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getUserPreferences();
      setPreferences(response);
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: SelectChangeEvent<string | boolean>) => {
    const { name, value } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleToggleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const response = await apiClient.updateUserPreferences({
        default_educational_level: preferences.default_educational_level,
        default_format: preferences.default_format,
        default_style: preferences.default_style,
        include_exercises_by_default: preferences.include_exercises_by_default
      });

      setPreferences(response);
      if (onPreferencesChange) {
        onPreferencesChange(response);
      }
      alert('Preferences saved successfully!');
    } catch (error: any) {
      console.error('Error saving preferences:', error);
      alert(`Error saving preferences: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Format Customization
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel>Educational Level</InputLabel>
        <Select
          name="default_educational_level"
          value={preferences.default_educational_level}
          label="Educational Level"
          onChange={handleInputChange}
          disabled={loading}
        >
          <MenuItem value="K12">K-12</MenuItem>
          <MenuItem value="UNDERGRADUATE">Undergraduate</MenuItem>
          <MenuItem value="GRADUATE">Graduate</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth margin="normal">
        <InputLabel>Default Format</InputLabel>
        <Select
          name="default_format"
          value={preferences.default_format}
          label="Default Format"
          onChange={handleInputChange}
          disabled={loading}
        >
          <MenuItem value="PDF">PDF</MenuItem>
          <MenuItem value="DOCX">DOCX</MenuItem>
          <MenuItem value="HTML">HTML</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth margin="normal">
        <InputLabel>Default Style</InputLabel>
        <Select
          name="default_style"
          value={preferences.default_style}
          label="Default Style"
          onChange={handleInputChange}
          disabled={loading}
        >
          <MenuItem value="academic">Academic</MenuItem>
          <MenuItem value="casual">Casual</MenuItem>
          <MenuItem value="technical">Technical</MenuItem>
        </Select>
      </FormControl>

      <FormGroup sx={{ mt: 2 }}>
        <FormControlLabel
          control={
            <Switch
              name="include_exercises_by_default"
              checked={preferences.include_exercises_by_default}
              onChange={handleToggleChange}
              disabled={loading}
            />
          }
          label="Include Exercises by Default"
        />
        <FormControlLabel
          control={
            <Switch
              name="include_summaries_by_default"
              checked={preferences.include_summaries_by_default}
              onChange={handleToggleChange}
              disabled={loading}
            />
          }
          label="Include Summaries by Default"
        />
      </FormGroup>

      <Button
        variant="contained"
        color="primary"
        sx={{ mt: 3 }}
        onClick={handleSave}
        disabled={loading}
      >
        {loading ? 'Saving...' : 'Save Preferences'}
      </Button>
    </Box>
  );
};

export default FormatCustomizer;