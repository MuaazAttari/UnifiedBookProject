import React, { useState, useEffect } from 'react';
import { Container, Typography, TextField, Button, Box, Tabs, Tab, Paper, Alert, Grid } from '@mui/material';
import apiClient from '../../services/api-client';
import { Textbook } from '../../services/api-client';
import ContentEditor from '../../components/ContentEditor/ContentEditor';
import ChapterReview from '../../components/ChapterReview/ChapterReview';

const ReviewPage = () => {
  const [textbook, setTextbook] = useState<Textbook | null>(null);
  const [textbookId, setTextbookId] = useState<string>(''); // In a real app, this would come from URL params
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // For now, using a default textbook ID for testing
    // In a real app, this would come from URL parameters
    const defaultTextbookId = 'textbook-123'; // Replace with actual ID when available
    setTextbookId(defaultTextbookId);
    loadTextbook(defaultTextbookId);
  }, []);

  const loadTextbook = async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const textbookData = await apiClient.getTextbook(id);
      setTextbook(textbookData);
    } catch (err: any) {
      setError(err.message || 'Error loading textbook');
      console.error('Error loading textbook:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleChapterUpdate = (updatedChapter: any) => {
    if (textbook) {
      const updatedChapters = [...textbook.chapters];
      const chapterIndex = updatedChapters.findIndex(ch => ch.id === updatedChapter.id);
      if (chapterIndex !== -1) {
        updatedChapters[chapterIndex] = updatedChapter;
        setTextbook({
          ...textbook,
          chapters: updatedChapters
        });
      }
    }
  };

  const handleApproveChapter = (chapterId: string) => {
    // This would update the chapter status to 'REVIEWED' via API
    console.log('Approving chapter:', chapterId);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" className="container">
        <Typography variant="h4" className="page-title">
          Review Textbook
        </Typography>
        <Typography>Loading textbook...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" className="container">
        <Typography variant="h4" className="page-title">
          Review Textbook
        </Typography>
        <Alert severity="error">{error}</Alert>
        <Button variant="contained" onClick={() => loadTextbook(textbookId)}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" className="container">
      <Typography variant="h4" className="page-title">
        Review Textbook
      </Typography>

      {textbook && (
        <>
          <Typography variant="h5" sx={{ mb: 2 }}>
            {textbook.title}
          </Typography>

          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              {textbook.chapters.map((chapter, index) => (
                <Tab key={chapter.id} label={`Chapter ${index + 1}: ${chapter.title}`} />
              ))}
            </Tabs>
          </Paper>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Chapter Review
                </Typography>
                {textbook.chapters[activeTab] && (
                  <ChapterReview
                    title={textbook.chapters[activeTab].title}
                    content={textbook.chapters[activeTab].sections.length > 0
                      ? textbook.chapters[activeTab].sections[0].content
                      : 'No content available'}
                    status={textbook.chapters[activeTab].status}
                    position={textbook.chapters[activeTab].position}
                    onEdit={() => {}} // Will be handled by the editor tab
                    onApprove={() => handleApproveChapter(textbook.chapters[activeTab].id)}
                  />
                )}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Edit Content
                </Typography>
                {textbook.chapters[activeTab] && (
                  <ContentEditor
                    chapterId={textbook.chapters[activeTab].id}
                    initialChapter={textbook.chapters[activeTab]}
                    onChapterUpdate={handleChapterUpdate}
                  />
                )}
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </Container>
  );
};

export default ReviewPage;