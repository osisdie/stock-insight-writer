"""Stock screening service to find investment candidates."""

from stock_insight_writer.clients.yahoo_finance import YahooFinanceClient
from stock_insight_writer.config import get_settings
from stock_insight_writer.models.stock import StockCandidate


class StockScreener:
    """Service to screen and identify stock candidates for analysis."""

    def __init__(self, yahoo_client: YahooFinanceClient | None = None) -> None:
        self.yahoo = yahoo_client or YahooFinanceClient()
        self.settings = get_settings()

    def screen_candidates(self) -> list[StockCandidate]:
        """Screen for stock candidates based on price movement and catalysts.

        Returns:
            List of StockCandidate objects (3-6 candidates)
        """
        candidates = []

        # Get market movers
        movers = self.yahoo.get_gainers_losers(limit=15)

        for ticker in movers:
            stock = self.yahoo.get_stock_data(ticker)
            if stock is None:
                continue

            # Filter by minimum price change
            if abs(stock.price_change_pct) < self.settings.min_price_change_pct:
                continue

            # Get news for catalyst identification
            news = self.yahoo.get_news(ticker, limit=3)
            if news:
                stock.news_headlines = [headline for headline, _ in news]
                # Use first headline as catalyst hint
                stock.catalyst = news[0][0] if news else None

            candidates.append(stock)

            if len(candidates) >= self.settings.max_candidates:
                break

        return candidates

    def screen_from_watchlist(self, tickers: list[str]) -> list[StockCandidate]:
        """Screen specific tickers from a user-provided watchlist.

        Args:
            tickers: List of ticker symbols to screen

        Returns:
            List of StockCandidate objects with significant movement
        """
        candidates = []

        for ticker in tickers:
            stock = self.yahoo.get_stock_data(ticker)
            if stock is None:
                continue

            # Get news
            news = self.yahoo.get_news(ticker, limit=3)
            if news:
                stock.news_headlines = [headline for headline, _ in news]
                stock.catalyst = news[0][0] if news else None

            candidates.append(stock)

        # Sort by absolute price change
        candidates.sort(key=lambda s: abs(s.price_change_pct), reverse=True)
        return candidates[: self.settings.max_candidates]
