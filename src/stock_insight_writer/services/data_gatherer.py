"""Data gathering service to collect materials for post writing."""

from stock_insight_writer.clients.yahoo_finance import YahooFinanceClient
from stock_insight_writer.models.stock import StockCandidate


class DataGatherer:
    """Service to gather comprehensive data for a selected stock."""

    def __init__(self, yahoo_client: YahooFinanceClient | None = None) -> None:
        self.yahoo = yahoo_client or YahooFinanceClient()

    def gather_materials(self, candidate: StockCandidate) -> dict:
        """Gather all materials needed for post writing.

        Args:
            candidate: The selected stock candidate

        Returns:
            Dictionary with gathered materials
        """
        ticker = candidate.ticker

        # Refresh stock data to ensure it's current
        fresh_data = self.yahoo.get_stock_data(ticker)
        if fresh_data:
            # Update candidate with fresh data
            candidate.current_price = fresh_data.current_price
            candidate.high_52w = fresh_data.high_52w
            candidate.low_52w = fresh_data.low_52w
            candidate.analyst_target_price = fresh_data.analyst_target_price
            candidate.analyst_rating = fresh_data.analyst_rating

        # Get news with URLs for references
        news_items = self.yahoo.get_news(ticker, limit=5)

        # Build materials dictionary
        materials = {
            "ticker": ticker,
            "company_name": candidate.company_name,
            "stock_data": self.yahoo.get_price_summary(ticker),
            "analyst_data": self.yahoo.get_analyst_summary(ticker),
            "news_items": news_items,
            "news_summary": self._format_news_summary(news_items),
            "chart_url": f"https://ycharts.com/companies/{ticker}/chart/",
            "candidate": candidate,
        }

        return materials

    def _format_news_summary(self, news_items: list[tuple[str, str]]) -> str:
        """Format news items for LLM consumption.

        Args:
            news_items: List of (headline, url) tuples

        Returns:
            Formatted news summary
        """
        if not news_items:
            return "No recent news available."

        lines = ["Recent news and catalysts:"]
        for headline, _ in news_items:
            lines.append(f"- {headline}")

        return "\n".join(lines)
