#!/bin/bash

# Setup script for the Unified Textbook Generation and RAG System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows: venv\Scripts\activate
# On Unix/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Setup complete! Activate the virtual environment and run the application with:"
echo "uvicorn src.main:app --reload"