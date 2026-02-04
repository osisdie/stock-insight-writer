"""OpenRouter LLM client using OpenAI-compatible API."""

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from stock_insight_writer.config import Language, get_settings

# System prompts for different tasks in both languages
SYSTEM_PROMPTS = {
    "analyzer": {
        Language.EN: """You are an expert investment analyst. Your task is to analyze
stock candidates and select the single best one for an investment post.

Focus on:
1. Is the stock undervalued or overvalued vs consensus?
2. Has negative news been over-reacted to, or positive news not yet priced in?
3. Does the company have a long-term structural moat (data, scale, AI, essential demand)?

Select stocks where market sentiment severely disconnects from fundamentals.
Prefer defensive sector leaders or AI-related transformation plays after major drops.""",
        Language.ZH_TW: """你是一位專業投資分析師。你的任務是分析股票候選人並選出最適合投資文章的標的。

重點關注：
1. 該股票相對於市場共識是被低估還是高估？
2. 負面消息是否被過度反應，或正面消息尚未反映在價格中？
3. 該公司是否具有長期結構性護城河（數據、規模、AI、必需性需求）？

選擇市場情緒與基本面嚴重脫節的股票。
優先考慮防禦性行業龍頭或大跌後的AI轉型題材。""",
    },
    "post_writer": {
        Language.EN: """You are a professional investment writer for a Stock Insight newsletter.
Write in a calm, data-driven, professional tone. No questions, no emotional language.
Focus on structural opportunities and fundamental analysis.

Style guidelines:
- 350-550 words
- Lead with current price and key catalyst
- Include chart reference (ycharts.com)
- List analyst targets with firms
- Explain core thesis (structural demand, moat, mispricing)
- End with balanced personal view (with implicit disclaimers)
- Use Google Finance links for tickers: (#[TICKER](https://www.google.com/finance/quote/TICKER:EXCHANGE))""",
        Language.ZH_TW: """你是一位專業的Stock Insight電子報投資撰稿人。
以冷靜、數據導向、專業的語調寫作。不使用疑問句，不使用情緒化語言。
專注於結構性機會和基本面分析。

風格指南：
- 350-550字
- 以當前價格和關鍵催化劑開頭
- 包含圖表參考（ycharts.com）
- 列出分析師目標價及其機構
- 解釋核心投資論點（結構性需求、護城河、錯誤定價）
- 以平衡的個人觀點結尾（隱含免責聲明）
- 使用Google Finance連結標記股票代碼：(#[代碼](https://www.google.com/finance/quote/代碼:交易所))""",
    },
}


class LLMClient:
    """Client for interacting with LLMs via OpenRouter."""

    def __init__(self, language: Language | None = None) -> None:
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.openrouter_api_key.get_secret_value(),
            base_url=settings.openrouter_base_url,
        )
        self.model = settings.openrouter_model
        self.language = language or settings.language

    def _get_system_prompt(self, task: str) -> str:
        """Get the system prompt for a task in the current language.

        Args:
            task: Task identifier (analyzer, post_writer)

        Returns:
            System prompt string
        """
        prompts = SYSTEM_PROMPTS.get(task, {})
        return prompts.get(self.language, prompts.get(Language.EN, ""))

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
        system_prompt = self._get_system_prompt("analyzer")

        if self.language == Language.ZH_TW:
            prompt = f"""分析這些股票候選人並選出最適合投資文章的標的：

{candidates_summary}

請回覆：
1. 你選擇的股票代碼
2. 簡要理由（2-3句）
3. 核心投資論點角度"""
        else:
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
        system_prompt = self._get_system_prompt("post_writer")

        if self.language == Language.ZH_TW:
            prompt = f"""為 {company_name} (#{ticker}) 撰寫一篇投資分析文章。

股票數據：
{stock_data}

近期新聞與催化劑：
{news_summary}

分析師數據：
{analyst_data}

只生成文章內容（不需要標題和參考文獻部分，這些會另外添加）。
包含圖表佔位符：[CHART_PLACEHOLDER]
引用圖表來源：(來源: https://ycharts.com/companies/{ticker}/chart/)
使用繁體中文撰寫。"""
        else:
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
        if self.language == Language.ZH_TW:
            prompt = f"""為 {company_name} (#{ticker}) 生成一個吸引人的Stock Insight文章標題。

投資論點：{thesis}

要求：
- 明確立場（看多/謹慎機會）
- 標題中包含 (#{ticker})
- 專業但吸引人
- 範例："聯合健康集團(#UNH)跌至2026年低點：必需醫療領域的結構性買入機會"
- 使用繁體中文

只回傳標題，不要其他內容。"""
        else:
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
        if self.language == Language.ZH_TW:
            prompt = f"""為這篇關於 {company_name} (#{ticker}) 的投資文章生成3-5個相關標籤。

文章內容摘要：
{content[:500]}...

以每行一個標籤的格式回傳，不要#符號。包含公司名稱和股票代碼。
中英文標籤皆可。
範例：
聯合健康
UNH
AI
醫療保健"""
        else:
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
