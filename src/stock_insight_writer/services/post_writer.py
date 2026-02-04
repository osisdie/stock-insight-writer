"""Post writing service using LLM to generate content."""

from datetime import date

from stock_insight_writer.clients.llm_client import LLMClient
from stock_insight_writer.config import Language, get_settings
from stock_insight_writer.models.post import InvestmentPost


class PostWriter:
    """Service to generate investment posts using LLM."""

    def __init__(self, llm_client: LLMClient | None = None, language: Language | None = None) -> None:
        settings = get_settings()
        self.language = language or settings.language
        self.llm = llm_client or LLMClient(language=self.language)

    def write_post(self, materials: dict) -> InvestmentPost:
        """Generate a complete investment post from gathered materials.

        Args:
            materials: Dictionary from DataGatherer containing:
                - ticker, company_name, stock_data, analyst_data
                - news_items, news_summary, chart_url, candidate

        Returns:
            InvestmentPost ready for export
        """
        ticker = materials["ticker"]
        company_name = materials["company_name"]

        # Generate post content
        content = self.llm.generate_post(
            ticker=ticker,
            company_name=company_name,
            stock_data=materials["stock_data"],
            news_summary=materials["news_summary"],
            analyst_data=materials["analyst_data"],
        )

        # Generate title
        thesis = self._extract_thesis(content)
        title = self.llm.generate_title(ticker, company_name, thesis)

        # Ensure title has ticker
        if f"#{ticker}" not in title and f"(#{ticker})" not in title:
            title = f"{title} (#{ticker})"

        # Generate tags
        tags = self.llm.generate_tags(ticker, company_name, content)

        # Build references from news items
        references = [(headline, url) for headline, url in materials.get("news_items", []) if headline and url][
            :3
        ]  # Limit to top 3 references

        return InvestmentPost(
            title=title,
            ticker=ticker,
            post_date=date.today(),
            tags=tags,
            content=content,
            references=references,
        )

    def _extract_thesis(self, content: str) -> str:
        """Extract a brief thesis summary from content for title generation.

        Args:
            content: The generated post content

        Returns:
            Brief thesis summary (first 200 chars of first paragraph)
        """
        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if paragraphs:
            # Remove markdown formatting
            first = paragraphs[0].replace("**", "").replace("*", "")
            return first[:200]
        return content[:200]
