# Stock Insight Writer

AI-powered daily stock investment post writer using LLMs and market data.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Copy .env.example to .env and configure
cp .env.example .env
# Edit .env with your OpenRouter API key

# Generate a post
stock-writer generate --ticker AAPL --dry-run

# Screen candidates only
stock-writer screen --watchlist "AAPL,MSFT,NVDA"
```

## Project Structure

```
src/stock_insight_writer/
├── main.py           # CLI entry point (typer)
├── config.py         # Pydantic Settings (.env loading)
├── models/           # Data models (StockCandidate, InvestmentPost)
├── services/         # Business logic (screener, analyzer, writer, etc.)
├── clients/          # External API clients (LLM, Yahoo Finance)
└── utils/            # Utility functions (slug, retry)
```

## Required Environment Variables

- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)
- `SLACK_WEBHOOK_URL` - Slack webhook URL for notifications (optional)

## Output Format

Posts are exported to `output/stock-posts/` in this format:
- Filename: `YYYYMMDD_slug-title.md`
- Content: Title, Date, Tags, and Markdown body with References

## Known Issues

- Yahoo Finance API may return 401 errors due to session/cookie requirements
- If this happens, try again later or consider using browser cookies for yfinance
