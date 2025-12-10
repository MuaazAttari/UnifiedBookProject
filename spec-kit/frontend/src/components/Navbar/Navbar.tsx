import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Container maxWidth="xl">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              Textbook Generator
            </Link>
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Generate
          </Button>
          <Button color="inherit" component={Link} to="/review">
            Review
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;