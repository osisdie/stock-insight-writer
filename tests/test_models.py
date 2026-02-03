"""Tests for data models."""

from datetime import date

from stock_insight_writer.models.post import InvestmentPost
from stock_insight_writer.models.stock import StockCandidate


class TestStockCandidate:
    def test_upside_potential(self):
        stock = StockCandidate(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=100.0,
            price_change_pct=5.0,
            analyst_target_price=120.0,
        )
        assert stock.upside_potential == 20.0

    def test_from_52w_high(self):
        stock = StockCandidate(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=90.0,
            price_change_pct=-10.0,
            high_52w=100.0,
        )
        assert stock.from_52w_high_pct == -10.0

    def test_summary(self):
        stock = StockCandidate(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=150.0,
            price_change_pct=5.5,
        )
        summary = stock.summary()
        assert "AAPL" in summary
        assert "$150.00" in summary
        assert "+5.5%" in summary


class TestInvestmentPost:
    def test_filename_generation(self):
        post = InvestmentPost(
            title="Apple (#AAPL) Reaches New Heights",
            ticker="AAPL",
            post_date=date(2026, 2, 3),
            tags=["Apple", "AAPL", "Tech"],
            content="Test content",
        )
        filename = post.filename
        assert filename.startswith("20260203_")
        assert "apple" in filename.lower()

    def test_format_for_export(self):
        post = InvestmentPost(
            title="Apple (#AAPL) Test Post",
            ticker="AAPL",
            post_date=date(2026, 2, 3),
            tags=["Apple", "AAPL"],
            content="This is the content body.",
            references=[("News Article", "https://example.com/news")],
        )
        output = post.format_for_export()

        # Check structure
        assert "# Title" in output
        assert "`Apple (#AAPL) Test Post`" in output
        assert "# Date" in output
        assert "`2026-02-03`" in output
        assert "# Tags" in output
        assert "- #Apple" in output
        assert "# Content" in output
        assert "**References**" in output
        assert "[News Article](https://example.com/news)" in output
        assert "This is the content body." in output
