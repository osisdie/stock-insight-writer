"""Stock candidate data model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StockCandidate:
    """A stock candidate for analysis and potential post writing."""

    ticker: str
    company_name: str
    current_price: float
    price_change_pct: float  # Recent price change percentage

    # Optional fields populated during data gathering
    high_52w: float | None = None
    low_52w: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None

    # News and catalysts
    news_headlines: list[str] = field(default_factory=list)
    catalyst: str | None = None

    # Analyst data
    analyst_target_price: float | None = None
    analyst_rating: str | None = None

    # Chart URL
    chart_url: str | None = None

    # Timestamp
    fetched_at: datetime = field(default_factory=datetime.now)

    @property
    def upside_potential(self) -> float | None:
        """Calculate potential upside to analyst target."""
        if self.analyst_target_price and self.current_price > 0:
            return ((self.analyst_target_price - self.current_price) / self.current_price) * 100
        return None

    @property
    def from_52w_high_pct(self) -> float | None:
        """Calculate percentage from 52-week high."""
        if self.high_52w and self.current_price > 0:
            return ((self.current_price - self.high_52w) / self.high_52w) * 100
        return None

    def summary(self) -> str:
        """Generate a brief summary for LLM analysis."""
        parts = [
            f"{self.ticker} ({self.company_name})",
            f"Price: ${self.current_price:.2f}",
            f"Change: {self.price_change_pct:+.1f}%",
        ]
        if self.upside_potential is not None:
            parts.append(f"Upside to target: {self.upside_potential:.1f}%")
        if self.catalyst:
            parts.append(f"Catalyst: {self.catalyst}")
        return " | ".join(parts)
