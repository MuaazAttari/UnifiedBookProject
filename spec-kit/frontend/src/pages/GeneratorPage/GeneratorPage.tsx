import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Box, FormControl, InputLabel, Select, MenuItem, SelectChangeEvent, Alert, Grid } from '@mui/material';
import apiClient from '../../services/api-client';
import { TextbookGenerationRequest, TextbookGenerationResponse } from '../../services/api-client';
import FormatCustomizer from '../../components/FormatCustomizer/FormatCustomizer';

const GeneratorPage = () => {
  const [formData, setFormData] = useState<Omit<TextbookGenerationRequest, 'settings'>>({
    subject: '',
    title: '',
    educational_level: 'UNDERGRADUATE'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    setFormData(prev => ({
      ...prev,
      educational_level: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response: TextbookGenerationResponse = await apiClient.generateTextbook({
        ...formData,
        settings: {}
      });

      alert(`Textbook generation initiated successfully. ID: ${response.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to generate textbook. Please try again.');
      console.error('Error generating textbook:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" className="container">
      <Typography variant="h4" className="page-title">
        Generate Textbook
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Textbook Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              margin="normal"
              required
            />

            <TextField
              fullWidth
              label="Subject"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              margin="normal"
              required
            />

            <FormControl fullWidth margin="normal" required>
              <InputLabel>Educational Level</InputLabel>
              <Select
                name="educational_level"
                value={formData.educational_level}
                label="Educational Level"
                onChange={handleSelectChange}
              >
                <MenuItem value="K12">K-12</MenuItem>
                <MenuItem value="UNDERGRADUATE">Undergraduate</MenuItem>
                <MenuItem value="GRADUATE">Graduate</MenuItem>
              </Select>
            </FormControl>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ mt: 3 }}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Textbook'}
            </Button>
          </Box>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormatCustomizer />
        </Grid>
      </Grid>
    </Container>
  );
};

export default GeneratorPage;