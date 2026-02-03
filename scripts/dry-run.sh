#!/bin/bash
# Dry run - preview post without saving
# Usage: ./scripts/dry-run.sh [--ticker TICKER]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Default to a specific ticker if none provided
TICKER="${1:-AAPL}"

echo "🔍 Running dry-run for $TICKER..."
stock-writer generate --dry-run --ticker "$TICKER"
