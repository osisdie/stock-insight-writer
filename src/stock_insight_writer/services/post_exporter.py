"""Post export service to save posts to the filesystem."""

from pathlib import Path

from stock_insight_writer.config import get_settings
from stock_insight_writer.models.post import InvestmentPost


class PostExporter:
    """Service to export posts to the filesystem."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or get_settings().output_dir

    def export(self, post: InvestmentPost) -> Path:
        """Export a post to the output directory.

        Args:
            post: The InvestmentPost to export

        Returns:
            Path to the saved file
        """
        return post.save(self.output_dir)

    def preview(self, post: InvestmentPost) -> str:
        """Generate a preview of the post without saving.

        Args:
            post: The InvestmentPost to preview

        Returns:
            The formatted post content
        """
        return post.format_for_export()

    def get_output_path(self, post: InvestmentPost) -> Path:
        """Get the output path for a post without saving.

        Args:
            post: The InvestmentPost

        Returns:
            Path where the post would be saved
        """
        return self.output_dir / post.filename
