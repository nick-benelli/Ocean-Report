#!/bin/bash
# Clear Python caches
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null
echo "Python caches cleared (__pycache__, .pyc, .pytest_cache, .ruff_cache)"