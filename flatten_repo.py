#!/usr/bin/env python3
"""
Flatten a git repository into a single text file optimized for LLM consumption.
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path
from typing import Set, List
import subprocess


BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
    '.pdf', '.zip', '.tar', '.gz', '.rar',
    '.exe', '.dll', '.so', '.dylib',
    '.pyc', '.pyo', '.pyd', '.class', '.jar',
    '.whl', '.egg', '.o', '.a', '.lib',
    '.bin', '.dat', '.db', '.sqlite',
}

SKIP_DIRS = {
    '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
    'node_modules', '.npm', '.yarn', 'dist', 'build', '.egg-info',
    '.tox', '.coverage', '.vscode', '.idea', '.DS_Store',
    '.next', '.nuxt', 'out', '.cache', '.turbo', 'tests', '.claude',
}

SKIP_FILES = {
    '.gitignore', 'CLAUDE.md',
}


def is_binary_file(file_path: str) -> bool:
    """Check if file is binary."""
    ext = Path(file_path).suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(512)
        return False
    except (UnicodeDecodeError, IOError):
        return True


def get_gitignore_patterns(repo_path: str) -> Set[str]:
    """Extract patterns from .gitignore."""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    patterns = set()

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except Exception:
            pass

    return patterns


def should_exclude(file_path: str, repo_path: str, exclude_list: List[str]) -> bool:
    """Check if file should be excluded."""
    rel_path = os.path.relpath(file_path, repo_path)
    file_name = os.path.basename(file_path)

    # Check against skip files list
    if file_name in SKIP_FILES:
        return True

    # Check against exclude list
    for exclude_pattern in exclude_list:
        if exclude_pattern in rel_path or rel_path.startswith(exclude_pattern):
            return True

    # Check directory names
    for part in Path(rel_path).parts:
        if part in SKIP_DIRS:
            return True

    return False


def get_file_language(file_path: str) -> str:
    """Determine programming language from file extension."""
    ext = Path(file_path).suffix.lower()

    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sh': 'bash',
        '.bash': 'bash',
        '.sql': 'sql',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.md': 'markdown',
        '.rst': 'rst',
        '.tex': 'latex',
    }

    return language_map.get(ext, 'text')


def flatten_repo(repo_path: str, output_file: str, exclude_list: List[str] = None):
    """Flatten repository into a single text file."""
    if exclude_list is None:
        exclude_list = []

    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory")
        sys.exit(1)

    files_to_include = []

    # Walk through repo
    for root, dirs, files in os.walk(repo_path):
        # Skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not should_exclude(
            os.path.join(root, d), repo_path, exclude_list
        )]

        for file in files:
            file_path = os.path.join(root, file)

            # Skip excluded files
            if should_exclude(file_path, repo_path, exclude_list):
                continue

            # Skip binary files
            if is_binary_file(file_path):
                continue

            # Skip hidden files (except .gitignore, .github, etc.)
            if file.startswith('.') and file not in {'.gitignore', '.env.example'}:
                continue

            try:
                rel_path = os.path.relpath(file_path, repo_path)
                files_to_include.append((file_path, rel_path))
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")

    # Sort files for consistent output
    files_to_include.sort(key=lambda x: x[1])

    print(f"Found {len(files_to_include)} files to include")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write("REPOSITORY SNAPSHOT\n")
        out.write("=" * 80 + "\n\n")
        out.write(f"Repository: {repo_path}\n")
        out.write(f"Total files: {len(files_to_include)}\n\n")

        # File index
        out.write("FILE INDEX:\n")
        out.write("-" * 80 + "\n")
        for file_path, rel_path in files_to_include:
            out.write(f"{rel_path}\n")
        out.write("\n" + "=" * 80 + "\n\n")

        # File contents
        for file_path, rel_path in files_to_include:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                language = get_file_language(file_path)
                file_size = os.path.getsize(file_path)

                out.write(f"\n{'='*80}\n")
                out.write(f"FILE: {rel_path}\n")
                out.write(f"Language: {language}\n")
                out.write(f"Size: {file_size} bytes\n")
                out.write(f"{'='*80}\n\n")
                out.write(f"```{language}\n")
                out.write(content)
                if not content.endswith('\n'):
                    out.write('\n')
                out.write("```\n")

            except Exception as e:
                out.write(f"\n[ERROR reading {rel_path}: {e}]\n")

    print(f"Successfully flattened repo to: {output_file}")
    print(f"Output file size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description='Flatten a git repository into a single text file for LLM consumption'
    )
    parser.add_argument(
        'repo_path',
        help='Path to the repository to flatten'
    )
    parser.add_argument(
        '-o', '--output',
        default='flattened_repo.txt',
        help='Output file path (default: flattened_repo.txt)'
    )
    parser.add_argument(
        '-e', '--exclude',
        nargs='*',
        default=[],
        help='File or folder patterns to exclude (space-separated)'
    )

    args = parser.parse_args()

    flatten_repo(args.repo_path, args.output, args.exclude)


if __name__ == '__main__':
    main()
