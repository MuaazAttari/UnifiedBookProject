#!/usr/bin/env python3
"""
Utility functions for RAG system tasks
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scripts.reindex_docs import reindex_all_documents


async def run_reindex():
    """
    Function to run reindex from other contexts
    """
    await reindex_all_documents()