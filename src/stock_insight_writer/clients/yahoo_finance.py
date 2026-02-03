"""Yahoo Finance client using yfinance."""

import io
import sys
import warnings

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from stock_insight_writer.models.stock import StockCandidate

# Suppress yfinance warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")


def _clear_yfinance_cache() -> None:
    """Clear yfinance's internal crumb/cookie cache to fix 401 errors."""
    try:
        # Clear the shared data cache (crumb, cookies)
        if hasattr(yf, "shared") and hasattr(yf.shared, "_SHARED_DATA"):
            yf.shared._SHARED_DATA.clear()
        # Also try clearing via cache module if available
        if hasattr(yf, "cache"):
            yf.cache.clear()
    except Exception:
        pass


class YahooFinanceClient:
    """Client for fetching stock data from Yahoo Finance."""

    def __init__(self) -> None:
        """Initialize the client, clearing any stale cache."""
        _clear_yfinance_cache()

    def _handle_auth_error(self, error: Exception) -> bool:
        """Check if error is auth-related and clear cache if so.

        Returns True if cache was cleared and retry should happen.
        """
        error_str = str(error).lower()
        if "401" in error_str or "unauthorized" in error_str or "crumb" in error_str:
            _clear_yfinance_cache()
            return True
        return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_stock_data(self, ticker: str) -> StockCandidate | None:
        """Fetch comprehensive stock data for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StockCandidate with populated data, or None if fetch fails
        """
        try:
            # Use download() for price data - more reliable than history()
            hist = yf.download(
                ticker,
                period="1mo",
                progress=False,
                auto_adjust=True,
                threads=False,
            )

            if hist.empty:
                return None

            # Handle both single-ticker and multi-ticker (multi-index) formats
            close_col = hist["Close"]
            if hasattr(close_col, "columns"):
                # Multi-index: extract the ticker column
                if ticker in close_col.columns:
                    close_col = close_col[ticker]
                else:
                    close_col = close_col.iloc[:, 0]

            # Get current price from latest close - ensure scalar
            close_values = close_col.dropna()
            if len(close_values) == 0:
                return None

            last_val = close_values.iloc[-1]
            current_price = float(last_val.item() if hasattr(last_val, "item") else last_val)
            if current_price <= 0:
                return None

            # Calculate price change
            if len(close_values) >= 2:
                start_val = close_values.iloc[0]
                start_price = float(start_val.item() if hasattr(start_val, "item") else start_val)
                price_change_pct = ((current_price - start_price) / start_price) * 100
            else:
                price_change_pct = 0.0

            # Try to get additional info (may fail, but we have price data)
            # Note: Yahoo Finance has restricted .info API - 401 errors are common
            info = {}
            try:
                # Suppress stderr (yfinance prints HTTP errors directly)
                old_stderr = sys.stderr
                sys.stderr = io.StringIO()
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info or {}
                finally:
                    sys.stderr = old_stderr
            except Exception as e:
                # If auth error, clear cache for next attempt
                self._handle_auth_error(e)

            return StockCandidate(
                ticker=ticker,
                company_name=info.get("longName", info.get("shortName", ticker)),
                current_price=current_price,
                price_change_pct=price_change_pct,
                high_52w=info.get("fiftyTwoWeekHigh"),
                low_52w=info.get("fiftyTwoWeekLow"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                analyst_target_price=info.get("targetMeanPrice"),
                analyst_rating=info.get("recommendationKey"),
                chart_url=f"https://ycharts.com/companies/{ticker}/chart/",
            )
        except Exception as e:
            # Clear cache on auth errors so retry has fresh session
            if self._handle_auth_error(e):
                raise  # Re-raise to trigger tenacity retry
            print(f"Warning: Failed to fetch {ticker}: {e}")
            return None

    def get_gainers_losers(self, limit: int = 10) -> list[str]:
        """Get top market movers (gainers and losers).

        Args:
            limit: Maximum number of tickers to return

        Returns:
            List of ticker symbols with significant movement
        """
        # Popular tickers to screen (tech, healthcare, finance, etc.)
        watchlist = [
            # Tech
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "NVDA",
            "TSLA",
            "AMD",
            "INTC",
            "CRM",
            "ORCL",
            "ADBE",
            "NOW",
            "SNOW",
            "PLTR",
            "NET",
            "DDOG",
            "ZM",
            # AI/Cloud
            "SMCI",
            "ARM",
            "AVGO",
            "MU",
            "QCOM",
            "MRVL",
            # Healthcare
            "UNH",
            "JNJ",
            "PFE",
            "ABBV",
            "MRK",
            "LLY",
            "TMO",
            "ABT",
            # Finance
            "JPM",
            "BAC",
            "WFC",
            "GS",
            "MS",
            "V",
            "MA",
            "PYPL",
            # Consumer
            "WMT",
            "COST",
            "TGT",
            "HD",
            "NKE",
            "SBUX",
            "MCD",
            # Other
            "XOM",
            "CVX",
            "BA",
            "CAT",
            "GE",
            "DIS",
            "NFLX",
        ]

        # Batch download for efficiency
        try:
            data = yf.download(
                watchlist,
                period="5d",
                progress=False,
                auto_adjust=True,
                threads=True,
                group_by="ticker",
            )

            movers = []
            for ticker in watchlist:
                try:
                    if ticker in data.columns.get_level_values(0):
                        ticker_data = data[ticker]["Close"].dropna()
                        if len(ticker_data) >= 2:
                            start = float(ticker_data.iloc[0])
                            end = float(ticker_data.iloc[-1])
                            change_pct = ((end - start) / start) * 100
                            if abs(change_pct) >= 5:  # 5%+ move
                                movers.append((ticker, change_pct))
                except Exception:
                    continue

            # Sort by absolute change and return tickers
            movers.sort(key=lambda x: abs(x[1]), reverse=True)
            return [t[0] for t in movers[:limit]]

        except Exception:
            # Fallback: return default high-volatility stocks
            return ["NVDA", "TSLA", "AMD", "META", "SMCI"][:limit]

    def get_news(self, ticker: str, limit: int = 5) -> list[tuple[str, str]]:
        """Get recent news for a ticker.

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news items

        Returns:
            List of (headline, url) tuples
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news or []
            return [
                (item.get("title", ""), item.get("link", ""))
                for item in news[:limit]
                if item.get("title") and item.get("link")
            ]
        except Exception:
            return []

    def get_price_summary(self, ticker: str) -> str:
        """Generate a price summary string for LLM consumption.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Formatted price summary
        """
        stock = self.get_stock_data(ticker)
        if not stock:
            return f"Unable to fetch data for {ticker}"

        lines = [
            f"Current Price: ${stock.current_price:.2f}",
            f"1-Month Change: {stock.price_change_pct:+.1f}%",
        ]

        if stock.high_52w:
            lines.append(f"52-Week High: ${stock.high_52w:.2f}")
        if stock.low_52w:
            lines.append(f"52-Week Low: ${stock.low_52w:.2f}")
        if stock.from_52w_high_pct is not None:
            lines.append(f"From 52W High: {stock.from_52w_high_pct:.1f}%")
        if stock.pe_ratio:
            lines.append(f"P/E Ratio: {stock.pe_ratio:.1f}")
        if stock.market_cap:
            cap_b = stock.market_cap / 1e9
            lines.append(f"Market Cap: ${cap_b:.1f}B")

        return "\n".join(lines)

    def get_analyst_summary(self, ticker: str) -> str:
        """Generate analyst data summary for LLM consumption.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Formatted analyst summary
        """
        stock = self.get_stock_data(ticker)
        if not stock:
            return f"Unable to fetch analyst data for {ticker}"

        lines = []
        if stock.analyst_target_price:
            lines.append(f"Consensus Target Price: ${stock.analyst_target_price:.2f}")
            if stock.upside_potential is not None:
                lines.append(f"Implied Upside: {stock.upside_potential:.1f}%")
        if stock.analyst_rating:
            lines.append(f"Consensus Rating: {stock.analyst_rating.upper()}")

        return "\n".join(lines) if lines else "No analyst data available"
