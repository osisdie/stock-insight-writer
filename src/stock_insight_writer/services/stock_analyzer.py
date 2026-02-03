"""Stock analysis service using LLM to select top candidate."""

from stock_insight_writer.clients.llm_client import LLMClient
from stock_insight_writer.models.stock import StockCandidate


class StockAnalyzer:
    """Service to analyze candidates and select the best one for a post."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()

    def select_top_candidate(self, candidates: list[StockCandidate]) -> tuple[StockCandidate, str]:
        """Analyze candidates and select the best one for an investment post.

        Args:
            candidates: List of stock candidates to analyze

        Returns:
            Tuple of (selected candidate, analysis reasoning)
        """
        if not candidates:
            raise ValueError("No candidates provided for analysis")

        if len(candidates) == 1:
            return candidates[0], "Single candidate provided"

        # Build summary for LLM
        summaries = []
        for i, c in enumerate(candidates, 1):
            summaries.append(f"{i}. {c.summary()}")
            if c.news_headlines:
                summaries.append(f"   News: {c.news_headlines[0][:100]}...")

        candidates_text = "\n".join(summaries)

        # Get LLM analysis
        analysis = self.llm.analyze_stocks(candidates_text)

        # Extract selected ticker from analysis
        selected = self._extract_selected_ticker(analysis, candidates)

        return selected, analysis

    def _extract_selected_ticker(self, analysis: str, candidates: list[StockCandidate]) -> StockCandidate:
        """Extract the selected ticker from LLM analysis.

        Args:
            analysis: LLM analysis text
            candidates: Original candidate list

        Returns:
            The selected StockCandidate
        """
        analysis_upper = analysis.upper()

        # Try to find ticker mentions
        for candidate in candidates:
            if candidate.ticker.upper() in analysis_upper:
                return candidate

        # Fallback: return first candidate (highest movement)
        return candidates[0]
