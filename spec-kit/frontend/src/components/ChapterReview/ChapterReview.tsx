import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Chip
} from '@mui/material';

interface ChapterReviewProps {
  title: string;
  content: string;
  status: string;
  position: number;
  onEdit: () => void;
  onApprove: () => void;
}

const ChapterReview: React.FC<ChapterReviewProps> = ({
  title,
  content,
  status,
  position,
  onEdit,
  onApprove
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DRAFT':
        return 'default';
      case 'GENERATING':
        return 'info';
      case 'COMPLETED':
        return 'secondary';
      case 'REVIEWED':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Chapter {position}: {title}
        </Typography>
        <Chip
          label={status}
          color={getStatusColor(status) as any}
          size="small"
        />
      </Box>

      <Typography variant="body1" paragraph>
        {content.substring(0, 300)}{content.length > 300 ? '...' : ''}
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
        <Button variant="outlined" onClick={onEdit}>
          Edit Content
        </Button>
        <Button variant="contained" color="success" onClick={onApprove}>
          Approve
        </Button>
      </Box>
    </Paper>
  );
};

export default ChapterReview;