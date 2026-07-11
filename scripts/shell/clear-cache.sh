#!/bin/bash
# Clear Python caches and build artifacts

echo "🧹 Cleaning Python cache directories..."

# Python bytecode caches
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Testing caches
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find . -type d -name .hypothesis -exec rm -rf {} + 2>/dev/null

# Linting/type checking caches
find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null
find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null

# Coverage data
find . -type f -name ".coverage" -delete 2>/dev/null
find . -type f -name ".coverage.*" -delete 2>/dev/null
rm -rf htmlcov/ 2>/dev/null

# Build artifacts
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
find . -type d -name dist -exec rm -rf {} + 2>/dev/null
find . -type d -name build -exec rm -rf {} + 2>/dev/null
find . -type d -name .eggs -exec rm -rf {} + 2>/dev/null

# macOS artifacts
find . -type f -name ".DS_Store" -delete 2>/dev/null

echo "✅ Cache cleanup complete!"
echo "   Cleared: __pycache__, .pyc/.pyo, .pytest_cache, .hypothesis,"
echo "            .ruff_cache, .mypy_cache, coverage data, build artifacts, .DS_Store"
