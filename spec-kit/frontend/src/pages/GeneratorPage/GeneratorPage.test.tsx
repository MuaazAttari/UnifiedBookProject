import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GeneratorPage from './GeneratorPage';

test('renders generator page with form elements', () => {
  render(<GeneratorPage />);

  const titleInput = screen.getByLabelText(/Textbook Title/i);
  expect(titleInput).toBeInTheDocument();

  const subjectInput = screen.getByLabelText(/Subject/i);
  expect(subjectInput).toBeInTheDocument();

  const generateButton = screen.getByRole('button', { name: /Generate Textbook/i });
  expect(generateButton).toBeInTheDocument();
});

test('allows user to fill in form fields', () => {
  render(<GeneratorPage />);

  const titleInput = screen.getByLabelText(/Textbook Title/i);
  fireEvent.change(titleInput, { target: { value: 'Test Textbook' } });
  expect(titleInput).toHaveValue('Test Textbook');

  const subjectInput = screen.getByLabelText(/Subject/i);
  fireEvent.change(subjectInput, { target: { value: 'Test Subject' } });
  expect(subjectInput).toHaveValue('Test Subject');
});