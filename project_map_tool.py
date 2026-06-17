#!/usr/bin/env python3
"""
Project Map Tool - Search and load only relevant files from project_map.json.
This avoids loading the entire massive map when only a few files are needed.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional

# Path to the project map file
PROJECT_MAP_PATH = Path(__file__).parent / "brain_modes" / "project_map.json"


def load_project_map() -> Dict:
    """Load the full project map JSON."""
    with open(PROJECT_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_relevant_files(query: str, max_results: int = 5) -> List[str]:
    """
    Search project_map.json for files relevant to a query.
    
    This implementation matches the query against:
      - File paths (case-insensitive)
      - File notes (if any)
      - File roles (if any)
      - File extensions
    
    Args:
        query: Search term from user prompt
        max_results: Maximum number of file paths to return
    
    Returns:
        List of matching file paths (relative to project root)
    """
    query_lower = query.lower()
    
    try:
        project_map = load_project_map()
    except Exception as e:
        print(f"[project_map_tool] Failed to load project map: {e}")
        return []
    
    root = project_map.get('root', '')
    matched_paths = []
    
    for file_entry in project_map.get('files', []):
        path = file_entry.get('path', '').lower()
        notes = file_entry.get('notes', '').lower()
        role = file_entry.get('role', '').lower()
        
        # Check path match
        if query_lower in path:
            matched_paths.append(file_entry['path'])
            continue
            
        # Check notes match
        if query_lower in notes:
            matched_paths.append(file_entry['path'])
            continue
            
        # Check role match
        if query_lower in role:
            matched_paths.append(file_entry['path'])
            continue
    
    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for p in matched_paths:
        if p not in seen:
            seen.add(p)
            unique_paths.append(p)
    
    return unique_paths[:max_results]


def load_file_content(file_path: str, max_bytes: int = 5_000_000) -> Optional[str]:
    """
    Load content from a specific file, reading only up to max_bytes.
    
    Args:
        file_path: Path to the file (as stored in project map)
        max_bytes: Maximum content size to read (prevents OOM)
    
    Returns:
        File content as string, or None if failed
    """
    try:
        full_path = Path(file_path)
        if not full_path.is_file():
            return None
            
        # Check file size to prevent OOM
        size = full_path.stat().st_size
        if size > max_bytes:
            print(f"[project_map_tool] Skipping large file {file_path} ({size} bytes > {max_bytes} limit)")
            return None
            
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"[project_map_tool] Failed to read {file_path}: {e}")
        return None


def get_file_metadata(file_path: str) -> Dict:
    """
    Get basic metadata about a file from the project map.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dict with size, language, role, etc.
    """
    try:
        project_map = load_project_map()
        for entry in project_map.get('files', []):
            if entry.get('path') == file_path:
                return {
                    'size_bytes': entry.get('size_bytes', 0),
                    'language': entry.get('language', 'unknown'),
                    'role': entry.get('role', 'unknown'),
                    'notes': entry.get('notes', '')
                }
        return {'size_bytes': 0, 'language': 'unknown', 'role': 'unknown', 'notes': ''}
    except Exception as e:
        print(f"[project_map_tool] Failed to get metadata: {e}")
        return {'size_bytes': 0, 'language': 'unknown', 'role': 'unknown', 'notes': ''}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Project Map Tool")
    parser.add_argument('query', help='Search query for relevant files')
    parser.add_argument('--top', type=int, default=5, help='Maximum results')
    
    args = parser.parse_args()
    
    relevant_paths = search_relevant_files(args.query, max_results=args.top)
    
    print(f"Found {len(relevant_paths)} relevant files:")
    for path in relevant_paths:
        print(f"- {path}")
        
        metadata = get_file_metadata(path)
        print(f"  Size: {metadata['size_bytes']} bytes, Language: {metadata['language']}")
        
        content = load_file_content(path, max_bytes=1_000_000)
        if content:
            snippet = content[:200] + "..." if len(content) > 200 else content
            print(f"  Snippet: {snippet[:100]}{'...' if len(snippet) > 100 else ''}")
        print()