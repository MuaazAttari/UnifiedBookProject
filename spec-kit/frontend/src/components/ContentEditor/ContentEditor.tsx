import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Alert,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import apiClient from '../../services/api-client';
import { Chapter } from '../../services/api-client';
import SectionManager from '../SectionManager/SectionManager';

interface ContentEditorProps {
  chapterId: string;
  initialChapter?: Chapter;
  onChapterUpdate?: (updatedChapter: Chapter) => void;
}

const ContentEditor: React.FC<ContentEditorProps> = ({ chapterId, initialChapter, onChapterUpdate }) => {
  const [chapter, setChapter] = useState<Chapter | null>(initialChapter || null);
  const [title, setTitle] = useState<string>('');
  const [status, setStatus] = useState<string>('DRAFT');
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialChapter) {
      setChapter(initialChapter);
      setTitle(initialChapter.title);
      setStatus(initialChapter.status);
    }
  }, [initialChapter]);

  const handleSave = async () => {
    if (!chapter) return;

    try {
      setLoading(true);
      setError(null);

      // For now, we'll only update title and status since content is managed via sections
      const updateData: any = {
        title,
        content: chapter.sections.length > 0 ? chapter.sections[0].content : '',
        status
      };

      const updatedChapter = await apiClient.updateChapter(chapterId, updateData);
      setChapter(updatedChapter);

      if (onChapterUpdate) {
        onChapterUpdate(updatedChapter);
      }

      alert('Chapter updated successfully!');
    } catch (err: any) {
      setError(err.message || 'Error updating chapter');
      console.error('Error updating chapter:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSectionsUpdate = (updatedSections: any[]) => {
    if (chapter) {
      const updatedChapter = {
        ...chapter,
        sections: updatedSections
      };
      setChapter(updatedChapter);

      if (onChapterUpdate) {
        onChapterUpdate(updatedChapter);
      }
    }
  };

  if (!chapter) {
    return <Typography>Loading chapter...</Typography>;
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Edit Chapter: {title}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Chapter Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        margin="normal"
        disabled={loading}
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Status</InputLabel>
        <Select
          value={status}
          label="Status"
          onChange={(e: SelectChangeEvent<string>) => setStatus(e.target.value)}
          disabled={loading}
        >
          <MenuItem value="DRAFT">Draft</MenuItem>
          <MenuItem value="GENERATING">Generating</MenuItem>
          <MenuItem value="COMPLETED">Completed</MenuItem>
          <MenuItem value="REVIEWED">Reviewed</MenuItem>
        </Select>
      </FormControl>

      <Paper sx={{ mt: 2 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab label="Sections" />
          <Tab label="Chapter Details" />
        </Tabs>
      </Paper>

      {activeTab === 0 ? (
        <Box sx={{ mt: 2 }}>
          <SectionManager
            chapterId={chapterId}
            sections={chapter.sections}
            onSectionsUpdate={handleSectionsUpdate}
          />
        </Box>
      ) : (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Use the Sections tab to edit the content of this chapter. Each chapter is composed of multiple sections.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Chapter'}
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ContentEditor;