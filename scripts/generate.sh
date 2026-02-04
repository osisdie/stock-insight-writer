#!/usr/bin/env bash
# Generate a stock insight post
# Usage: ./scripts/generate.sh [options]
# Examples:
#   ./scripts/generate.sh --ticker AAPL              # Specific stock
#   ./scripts/generate.sh --watchlist "AAPL,MSFT"    # Screen from watchlist
#   ./scripts/generate.sh --lang zh-TW --dry-run     # Chinese, preview only

set -euo pipefail

cd "$(dirname "$0")/.."

# Check if .env exists
if [[ ! -f .env ]]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure your API keys."
    exit 1
fi

# Run the generator
stock-writer generate "$@"
