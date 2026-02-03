#!/bin/bash
# Screen stocks for candidates
# Usage: ./scripts/screen.sh [--watchlist "AAPL,MSFT,NVDA"]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "📊 Screening stocks for candidates..."

if [ -n "$1" ]; then
    stock-writer screen --watchlist "$1"
else
    # Default watchlist of popular stocks
    stock-writer screen --watchlist "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,AMD"
fi
