#!/usr/bin/env python3
"""
Management script for RAG system tasks
"""
import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scripts.reindex_docs import reindex_all_documents


def main():
    parser = argparse.ArgumentParser(description="Management script for RAG system")
    parser.add_argument(
        "command",
        choices=["reindex"],
        help="Command to execute"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )

    args = parser.parse_args()

    if args.command == "reindex":
        print("Starting reindex process...")
        if args.dry_run:
            print("This is a dry run - no changes will be made")
        else:
            asyncio.run(reindex_all_documents())
        print("Reindex process completed!")


if __name__ == "__main__":
    main()