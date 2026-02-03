"""CLI entry point for the Stock Insight Writer."""

from pathlib import Path

import typer

from stock_insight_writer.clients.llm_client import LLMClient
from stock_insight_writer.clients.yahoo_finance import YahooFinanceClient
from stock_insight_writer.config import get_settings
from stock_insight_writer.services.data_gatherer import DataGatherer
from stock_insight_writer.services.post_exporter import PostExporter
from stock_insight_writer.services.post_writer import PostWriter
from stock_insight_writer.services.slack_notifier import SlackNotifier
from stock_insight_writer.services.stock_analyzer import StockAnalyzer
from stock_insight_writer.services.stock_screener import StockScreener

app = typer.Typer(
    name="stock-writer",
    help="AI-powered daily stock investment post writer",
)


@app.command()
def generate(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Preview the post without saving or notifying",
    ),
    ticker: str | None = typer.Option(
        None,
        "--ticker",
        "-t",
        help="Specific ticker to write about (skips screening)",
    ),
    watchlist: str | None = typer.Option(
        None,
        "--watchlist",
        "-w",
        help="Comma-separated list of tickers to screen from",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (default: output/posts)",
    ),
) -> None:
    """Generate a daily investment post.

    This command orchestrates the full workflow:
    1. Screen candidates (or use provided ticker/watchlist)
    2. Analyze and select top candidate
    3. Gather materials (price data, news, analyst targets)
    4. Generate post using LLM
    5. Export to file
    6. Send Slack notification
    """
    settings = get_settings()

    # Initialize clients
    yahoo = YahooFinanceClient()
    llm = LLMClient()

    # Initialize services
    screener = StockScreener(yahoo)
    analyzer = StockAnalyzer(llm)
    gatherer = DataGatherer(yahoo)
    writer = PostWriter(llm)
    exporter = PostExporter(output_dir or settings.output_dir)
    notifier = SlackNotifier()

    typer.echo("🔍 Starting stock post generation...")

    # Step 1: Get candidates
    if ticker:
        typer.echo(f"📊 Using specified ticker: {ticker}")
        candidates = screener.screen_from_watchlist([ticker])
    elif watchlist:
        tickers = [t.strip().upper() for t in watchlist.split(",")]
        typer.echo(f"📊 Screening from watchlist: {', '.join(tickers)}")
        candidates = screener.screen_from_watchlist(tickers)
    else:
        typer.echo("📊 Screening market for candidates...")
        candidates = screener.screen_candidates()

    if not candidates:
        typer.echo("❌ No suitable candidates found. Try specifying a ticker with --ticker.")
        raise typer.Exit(1)

    typer.echo(f"✅ Found {len(candidates)} candidate(s):")
    for c in candidates:
        typer.echo(f"   • {c.ticker}: ${c.current_price:.2f} ({c.price_change_pct:+.1f}%)")

    # Step 2: Select top candidate
    typer.echo("\n🤖 Analyzing candidates with LLM...")
    selected, analysis = analyzer.select_top_candidate(candidates)
    typer.echo(f"✅ Selected: {selected.ticker} ({selected.company_name})")
    typer.echo(f"   Reasoning: {analysis[:200]}...")

    # Step 3: Gather materials
    typer.echo("\n📚 Gathering materials...")
    materials = gatherer.gather_materials(selected)
    typer.echo(f"✅ Collected price data, {len(materials.get('news_items', []))} news items")

    # Step 4: Generate post
    typer.echo("\n✍️ Generating post with LLM...")
    post = writer.write_post(materials)
    typer.echo(f"✅ Generated: {post.title}")

    # Step 5: Preview or export
    if dry_run:
        typer.echo("\n" + "=" * 60)
        typer.echo("DRY RUN - Post preview:")
        typer.echo("=" * 60)
        typer.echo(exporter.preview(post))
        typer.echo("=" * 60)
        typer.echo(f"Would save to: {exporter.get_output_path(post)}")
    else:
        typer.echo("\n💾 Exporting post...")
        output_path = exporter.export(post)
        typer.echo(f"✅ Saved to: {output_path}")

        # Step 6: Notify
        typer.echo("\n📢 Sending Slack notification...")
        if notifier.notify(post, output_path):
            typer.echo("✅ Slack notification sent!")
        else:
            typer.echo("⚠️ Slack webhook not configured, skipping notification")

    typer.echo("\n🎉 Done!")


@app.command()
def screen(
    watchlist: str | None = typer.Option(
        None,
        "--watchlist",
        "-w",
        help="Comma-separated list of tickers to screen",
    ),
) -> None:
    """Screen stocks for potential candidates without generating a post.

    Useful for reviewing candidates before committing to post generation.
    """
    yahoo = YahooFinanceClient()
    screener = StockScreener(yahoo)

    if watchlist:
        tickers = [t.strip().upper() for t in watchlist.split(",")]
        typer.echo(f"📊 Screening watchlist: {', '.join(tickers)}")
        candidates = screener.screen_from_watchlist(tickers)
    else:
        typer.echo("📊 Screening market for candidates...")
        candidates = screener.screen_candidates()

    if not candidates:
        typer.echo("❌ No candidates found with significant price movement.")
        raise typer.Exit(1)

    typer.echo(f"\n✅ Found {len(candidates)} candidate(s):\n")
    for c in candidates:
        typer.echo(f"📈 {c.ticker} - {c.company_name}")
        typer.echo(f"   Price: ${c.current_price:.2f} ({c.price_change_pct:+.1f}%)")
        if c.analyst_target_price:
            typer.echo(f"   Target: ${c.analyst_target_price:.2f}")
            if c.upside_potential:
                typer.echo(f"   Upside: {c.upside_potential:.1f}%")
        if c.news_headlines:
            typer.echo(f"   News: {c.news_headlines[0][:80]}...")
        typer.echo()


@app.command()
def config() -> None:
    """Display current configuration (with secrets masked)."""
    settings = get_settings()

    typer.echo("📋 Current Configuration:\n")
    typer.echo(f"   OpenRouter Model: {settings.openrouter_model}")
    typer.echo(f"   OpenRouter API Key: {'*' * 10}...{settings.openrouter_api_key.get_secret_value()[-4:]}")
    typer.echo(f"   Output Directory: {settings.output_dir}")
    typer.echo(f"   Min Price Change: {settings.min_price_change_pct}%")
    typer.echo(f"   Max Candidates: {settings.max_candidates}")
    if settings.slack_webhook_url:
        typer.echo(f"   Slack Webhook: {'*' * 20}...configured")
    else:
        typer.echo("   Slack Webhook: Not configured")


if __name__ == "__main__":
    app()
