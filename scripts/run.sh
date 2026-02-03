#!/bin/bash
# Generate a daily stock investment post
# Usage: ./scripts/run.sh [--debug] [--ticker TICKER] [--watchlist "AAPL,MSFT"]
#
# Options:
#   --debug     Enable debugpy and wait for VS Code to attach (port 5678)
#   --ticker    Specific ticker to write about
#   --watchlist Comma-separated list of tickers to screen

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

# Check for debug flag
DEBUG_MODE=false
ARGS=()

for arg in "$@"; do
    if [ "$arg" == "--debug" ]; then
        DEBUG_MODE=true
    else
        ARGS+=("$arg")
    fi
done

if [ "$DEBUG_MODE" = true ]; then
    echo "🐛 Starting in DEBUG mode (waiting for debugger on port 5678)..."
    echo "   Attach VS Code debugger to continue."
    python -m debugpy --listen 5678 --wait-for-client -m stock_insight_writer.main generate "${ARGS[@]}"
else
    echo "🚀 Starting stock post generation..."
    stock-writer generate "${ARGS[@]}"
fi
