import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import GeneratorPage from './pages/GeneratorPage/GeneratorPage';
import ReviewPage from './pages/ReviewPage/ReviewPage';
import Navbar from './components/Navbar/Navbar';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#e57373',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<GeneratorPage />} />
          <Route path="/generate" element={<GeneratorPage />} />
          <Route path="/review/:textbookId" element={<ReviewPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;