"""OpenRouter LLM client using OpenAI-compatible API."""

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from stock_insight_writer.config import get_settings


class LLMClient:
    """Client for interacting with LLMs via OpenRouter."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.openrouter_api_key.get_secret_value(),
            base_url=settings.openrouter_base_url,
        )
        self.model = settings.openrouter_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            The generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def analyze_stocks(self, candidates_summary: str) -> str:
        """Analyze stock candidates and select the best one.

        Args:
            candidates_summary: Summary of all stock candidates

        Returns:
            Analysis and selection reasoning
        """
        system_prompt = """You are an expert investment analyst. Your task is to analyze
stock candidates and select the single best one for an investment post.

Focus on:
1. Is the stock undervalued or overvalued vs consensus?
2. Has negative news been over-reacted to, or positive news not yet priced in?
3. Does the company have a long-term structural moat (data, scale, AI, essential demand)?

Select stocks where market sentiment severely disconnects from fundamentals.
Prefer defensive sector leaders or AI-related transformation plays after major drops."""

        prompt = f"""Analyze these stock candidates and select the TOP 1 most compelling for an investment post:

{candidates_summary}

Respond with:
1. Your selected ticker
2. Brief reasoning (2-3 sentences)
3. Key investment thesis angle"""

        return self.complete(prompt, system_prompt, temperature=0.5)

    def generate_post(
        self,
        ticker: str,
        company_name: str,
        stock_data: str,
        news_summary: str,
        analyst_data: str,
    ) -> str:
        """Generate an investment post for the selected stock.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            stock_data: Price and valuation data
            news_summary: Recent news and catalysts
            analyst_data: Analyst targets and ratings

        Returns:
            Generated post content in markdown
        """
        system_prompt = """You are a professional investment writer for a Stock Insight newsletter.
Write in a calm, data-driven, professional tone. No questions, no emotional language.
Focus on structural opportunities and fundamental analysis.

Style guidelines:
- 350-550 words
- Lead with current price and key catalyst
- Include chart reference (ycharts.com)
- List analyst targets with firms
- Explain core thesis (structural demand, moat, mispricing)
- End with balanced personal view (with implicit disclaimers)
- Use Google Finance links for tickers: (#[TICKER](https://www.google.com/finance/quote/TICKER:EXCHANGE))"""

        prompt = f"""Write an investment post for {company_name} (#{ticker}).

Stock Data:
{stock_data}

Recent News & Catalysts:
{news_summary}

Analyst Data:
{analyst_data}

Generate the post body only (no title, no references section - those are added separately).
Include a placeholder for the chart image: [CHART_PLACEHOLDER]
Reference the chart source: (Source: https://ycharts.com/companies/{ticker}/chart/)"""

        return self.complete(prompt, system_prompt, temperature=0.7, max_tokens=1500)

    def generate_title(self, ticker: str, company_name: str, thesis: str) -> str:
        """Generate an engaging post title.

        Args:
            ticker: Stock ticker
            company_name: Company name
            thesis: Investment thesis summary

        Returns:
            Post title with ticker
        """
        prompt = f"""Generate a compelling Stock Insight post title for {company_name} (#{ticker}).

Thesis: {thesis}

Requirements:
- Clear stance (bullish/cautious opportunity)
- Include (#{ticker}) in title
- Professional but attention-grabbing
- Examples: "UnitedHealth Group (#UNH) Hits 2026 Lows: A Structural Buy in Essential Healthcare"

Return only the title, nothing else."""

        return self.complete(prompt, temperature=0.8, max_tokens=100).strip()

    def generate_tags(self, ticker: str, company_name: str, content: str) -> list[str]:
        """Generate relevant hashtags for the post.

        Args:
            ticker: Stock ticker
            company_name: Company name
            content: Post content

        Returns:
            List of hashtags (without # prefix)
        """
        prompt = f"""Generate 3-5 relevant hashtags for this investment post about {company_name} (#{ticker}).

Post content summary:
{content[:500]}...

Return hashtags one per line, without the # symbol. Include the company name and ticker.
Example:
UnitedHealth
UNH
AI
Healthcare"""

        response = self.complete(prompt, temperature=0.5, max_tokens=100)
        tags = [line.strip() for line in response.strip().split("\n") if line.strip()]
        return tags[:5]  # Limit to 5 tags
