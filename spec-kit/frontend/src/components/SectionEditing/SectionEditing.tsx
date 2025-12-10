import React, { useState } from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Button,
  Typography,
  IconButton,
  Alert
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import apiClient from '../../services/api-client';

interface Section {
  id: string;
  title: string;
  content: string;
  type: string;
  position: number;
  chapter_id: string;
}

interface SectionEditingProps {
  section: Section;
  onSectionUpdate?: (updatedSection: Section) => void;
  onSectionDelete?: (sectionId: string) => void;
}

const SectionEditing: React.FC<SectionEditingProps> = ({
  section,
  onSectionUpdate,
  onSectionDelete
}) => {
  const [title, setTitle] = useState(section.title);
  const [content, setContent] = useState(section.content);
  const [type, setType] = useState(section.type);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTypeChange = (e: SelectChangeEvent<string>) => {
    setType(e.target.value);
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);

      const updatedSection = await apiClient.updateSection(section.id, {
        title,
        content,
        type
      });

      if (onSectionUpdate) {
        onSectionUpdate({
          ...section,
          title,
          content,
          type
        });
      }

      alert('Section updated successfully!');
    } catch (err: any) {
      setError(err.message || 'Error updating section');
      console.error('Error updating section:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this section?')) {
      try {
        setLoading(true);
        await apiClient.deleteSection(section.id);

        if (onSectionDelete) {
          onSectionDelete(section.id);
        }
      } catch (err: any) {
        setError(err.message || 'Error deleting section');
        console.error('Error deleting section:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 2, mb: 2, position: 'relative' }}>
      <IconButton
        onClick={handleDelete}
        size="small"
        sx={{ position: 'absolute', top: 8, right: 8 }}
        disabled={loading}
      >
        <DeleteIcon fontSize="small" />
      </IconButton>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Section Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        margin="normal"
        disabled={loading}
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Type</InputLabel>
        <Select
          value={type}
          label="Type"
          onChange={handleTypeChange}
          disabled={loading}
        >
          <MenuItem value="CONTENT">Content</MenuItem>
          <MenuItem value="SUMMARY">Summary</MenuItem>
          <MenuItem value="EXERCISE">Exercise</MenuItem>
          <MenuItem value="KEY_POINT">Key Point</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        label="Section Content"
        multiline
        rows={4}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        margin="normal"
        disabled={loading}
      />

      <Button
        variant="contained"
        color="primary"
        size="small"
        onClick={handleSave}
        sx={{ mt: 1 }}
        disabled={loading}
      >
        {loading ? 'Saving...' : 'Update Section'}
      </Button>
    </Box>
  );
};

export default SectionEditing;