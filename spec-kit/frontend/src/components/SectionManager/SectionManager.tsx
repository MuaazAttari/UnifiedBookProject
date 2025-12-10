import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  TextField,
  Paper
} from '@mui/material';
import apiClient from '../../services/api-client';
import SectionEditing from '../SectionEditing/SectionEditing';

interface Section {
  id: string;
  title: string;
  content: string;
  type: string;
  position: number;
  chapter_id: string;
}

interface SectionManagerProps {
  chapterId: string;
  sections: Section[];
  onSectionsUpdate: (updatedSections: Section[]) => void;
}

const SectionManager: React.FC<SectionManagerProps> = ({
  chapterId,
  sections,
  onSectionsUpdate
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSectionTitle, setNewSectionTitle] = useState('');
  const [newSectionContent, setNewSectionContent] = useState('');
  const [newSectionType, setNewSectionType] = useState('CONTENT');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddSection = async () => {
    try {
      setLoading(true);
      setError(null);

      const newSection = await apiClient.addSection(chapterId, {
        title: newSectionTitle,
        content: newSectionContent,
        type: newSectionType
      });

      // Update the sections list
      onSectionsUpdate([...sections, newSection]);

      // Reset form
      setNewSectionTitle('');
      setNewSectionContent('');
      setNewSectionType('CONTENT');
      setShowAddForm(false);

      alert('Section added successfully!');
    } catch (err: any) {
      setError(err.message || 'Error adding section');
      console.error('Error adding section:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSectionUpdate = (updatedSection: Section) => {
    const updatedSections = sections.map(section =>
      section.id === updatedSection.id ? updatedSection : section
    );
    onSectionsUpdate(updatedSections);
  };

  const handleSectionDelete = (sectionId: string) => {
    const updatedSections = sections.filter(section => section.id !== sectionId);
    onSectionsUpdate(updatedSections);
  };

  const handleTypeChange = (e: SelectChangeEvent<string>) => {
    setNewSectionType(e.target.value);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Manage Sections</Typography>
        <Button
          variant="outlined"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : 'Add Section'}
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {showAddForm && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Add New Section</Typography>

          <TextField
            fullWidth
            label="Section Title"
            value={newSectionTitle}
            onChange={(e) => setNewSectionTitle(e.target.value)}
            margin="normal"
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Type</InputLabel>
            <Select
              value={newSectionType}
              label="Type"
              onChange={handleTypeChange}
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
            value={newSectionContent}
            onChange={(e) => setNewSectionContent(e.target.value)}
            margin="normal"
          />

          <Button
            variant="contained"
            color="primary"
            onClick={handleAddSection}
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? 'Adding...' : 'Add Section'}
          </Button>
        </Paper>
      )}

      {sections.length === 0 ? (
        <Typography>No sections in this chapter yet.</Typography>
      ) : (
        <Box>
          {sections.map((section) => (
            <SectionEditing
              key={section.id}
              section={section}
              onSectionUpdate={handleSectionUpdate}
              onSectionDelete={handleSectionDelete}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

export default SectionManager;