# Stock Insight Writer

AI-powered daily stock investment post writer that automatically screens market movers, analyzes opportunities, and generates publication-ready investment analysis posts.

## Features

- **Automated Stock Screening** - Scans market for stocks with significant price movements
- **LLM-Powered Analysis** - Uses Claude/GPT to analyze candidates and select the most compelling opportunity
- **Professional Post Generation** - Creates well-structured investment analysis posts with:
  - Price action analysis
  - Technical indicators
  - Analyst consensus and price targets
  - Risk factors and investment thesis
- **Multiple LLM Support** - Works with any OpenRouter-compatible model (Claude, GPT-4, Llama, etc.)
- **Slack Notifications** - Optional alerts when new posts are generated
- **Dry Run Mode** - Preview posts before committing

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/osisdie/stock-insight-writer.git
cd stock-insight-writer

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

### Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API key
# Get your key from https://openrouter.ai/keys
```

### Usage

```bash
# Generate a post for a specific stock
stock-writer generate --ticker AAPL

# Preview without saving (dry run)
stock-writer generate --ticker NVDA --dry-run

# Screen stocks from a watchlist
stock-writer screen --watchlist "AAPL,MSFT,NVDA,META"

# Auto-screen market movers and generate post
stock-writer generate

# Show current configuration
stock-writer config
```

## Project Structure

```
stock-insight-writer/
├── src/stock_insight_writer/
│   ├── main.py           # CLI entry point (Typer)
│   ├── config.py         # Configuration (Pydantic Settings)
│   ├── clients/          # External API clients
│   │   ├── llm_client.py      # OpenRouter LLM client
│   │   └── yahoo_finance.py   # Yahoo Finance data client
│   ├── models/           # Data models
│   │   ├── stock.py      # StockCandidate model
│   │   └── post.py       # InvestmentPost model
│   ├── services/         # Business logic
│   │   ├── stock_screener.py  # Market screening
│   │   ├── stock_analyzer.py  # LLM analysis
│   │   ├── data_gatherer.py   # Material collection
│   │   ├── post_writer.py     # Post generation
│   │   ├── post_exporter.py   # File export
│   │   └── slack_notifier.py  # Notifications
│   └── utils/            # Utilities
├── scripts/              # Shell scripts
├── tests/                # Test suite
└── output/stock-posts/   # Generated posts
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | Your OpenRouter API key |
| `OPENROUTER_MODEL` | No | `anthropic/claude-sonnet-4` | LLM model to use |
| `SLACK_WEBHOOK_URL` | No | - | Slack webhook for notifications |
| `OUTPUT_DIR` | No | `output/stock-posts` | Output directory for posts |
| `MIN_PRICE_CHANGE_PCT` | No | `10.0` | Minimum price change % for screening |
| `MAX_CANDIDATES` | No | `6` | Maximum candidates to analyze |

## Output Format

Generated posts are saved as text files with the format:
```
YYYYMMDD_slug-title.md
```

Each post includes:
- Title with stock ticker
- Publication date
- Hashtags/tags
- Full markdown body with analysis
- References section

## Development

```bash
# Run tests
pytest

# Run linting
ruff check .

# Format code
ruff format .
```

## CI/CD

The project includes CI configurations for both GitHub Actions and GitLab CI:

- **Lint** - Code quality checks with Ruff
- **Test** - Run test suite with pytest
- **Security** - Dependency vulnerability scanning

CI runs on:
- Push to `main` branch
- Pull/Merge requests
- Manual trigger

## Tech Stack

- **Python 3.12+**
- **Typer** - CLI framework
- **Pydantic** - Data validation and settings
- **yfinance** - Yahoo Finance market data
- **OpenAI SDK** - LLM integration (OpenRouter-compatible)
- **httpx** - HTTP client
- **tenacity** - Retry logic

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
