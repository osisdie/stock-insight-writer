#!/usr/bin/env bash
# Setup script for stock_insight_writer
# Usage: ./scripts/setup.sh

set -euo pipefail

cd "$(dirname "$0")/.."

echo "📈 Setting up Stock Insight Writer..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📦 Python version: $python_version"

# Create virtual environment if it doesn't exist
if [[ ! -d .venv ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install package
echo "📥 Installing dependencies..."
pip install -e ".[dev]"

# Copy .env.example if .env doesn't exist
if [[ ! -f .env ]]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - OPENROUTER_API_KEY (required)"
    echo "   - SLACK_WEBHOOK_URL (optional)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Configure your .env file with API keys"
echo "  3. Run: stock-writer config"
echo "  4. Generate a post: stock-writer generate --ticker AAPL --dry-run"
