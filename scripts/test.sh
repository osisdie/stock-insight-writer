#!/bin/bash
# Run tests
# Usage: ./scripts/test.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🧪 Running tests..."

# Install test dependencies if needed
pip install -q pytest pytest-asyncio

# Run pytest
pytest tests/ -v "$@"
