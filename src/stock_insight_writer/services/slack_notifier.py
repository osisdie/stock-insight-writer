"""Slack notification service."""

from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from stock_insight_writer.config import get_settings
from stock_insight_writer.models.post import InvestmentPost


class SlackNotifier:
    """Service to send notifications to Slack."""

    def __init__(self, webhook_url: str | None = None) -> None:
        settings = get_settings()
        if webhook_url:
            self.webhook_url = webhook_url
        elif settings.slack_webhook_url:
            self.webhook_url = settings.slack_webhook_url.get_secret_value()
        else:
            self.webhook_url = None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def notify(self, post: InvestmentPost, output_path: Path) -> bool:
        """Send a notification about a new post to Slack.

        Args:
            post: The generated InvestmentPost
            output_path: Path where the post was saved

        Returns:
            True if notification was sent, False if webhook not configured
        """
        if not self.webhook_url:
            return False

        message = self._format_message(post, output_path)

        with httpx.Client() as client:
            response = client.post(
                self.webhook_url,
                json={"text": message},
                timeout=10.0,
            )
            response.raise_for_status()

        return True

    def _format_message(self, post: InvestmentPost, output_path: Path) -> str:
        """Format the Slack notification message.

        Args:
            post: The InvestmentPost
            output_path: Path to saved file

        Returns:
            Formatted message string
        """
        tags_str = " ".join(f"#{tag}" for tag in post.tags[:3])

        return f"""📝 *New Stock Insight Post Generated*

*{post.title}*

Date: {post.post_date.isoformat()}
Tags: {tags_str}
File: `{output_path.name}`

Preview (first 200 chars):
>{post.content[:200]}..."""
