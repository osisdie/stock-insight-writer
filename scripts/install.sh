#!/bin/bash
# Install the stock-writer package and dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "📦 Installing stock-writer..."
pip install -e .

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and add your OPENROUTER_API_KEY"
echo "  2. Run: stock-writer generate --dry-run --ticker AAPL"
