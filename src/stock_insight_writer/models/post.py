"""Investment post data model and formatter."""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from slugify import slugify


@dataclass
class InvestmentPost:
    """A completed investment post ready for export."""

    title: str
    ticker: str
    post_date: date
    tags: list[str]
    content: str  # The markdown content body
    references: list[tuple[str, str]] = field(default_factory=list)  # (title, url) pairs

    @property
    def filename(self) -> str:
        """Generate filename in YYYYMMDD_slug-title format (no extension)."""
        date_str = self.post_date.strftime("%Y%m%d")
        # Create slug from title, limit length
        title_slug = slugify(self.title, max_length=50, word_boundary=True)
        return f"{date_str}_{title_slug}"

    def format_for_export(self) -> str:
        """Format the post in the exact Stock Insight export format."""
        # Build tags section
        tags_section = "\n".join(f"- #{tag}" for tag in self.tags)

        # Build references section
        references_md = "\n".join(f"*   [{title}]({url})" for title, url in self.references)

        # Combine into final format
        return f"""# Title
`{self.title}`

# Date
`{self.post_date.isoformat()}`

# Tags
{tags_section}

# Content
```md
**References**

{references_md}

{self.content}
```"""

    def save(self, output_dir: Path) -> Path:
        """Save the post to the output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.filename
        output_path.write_text(self.format_for_export(), encoding="utf-8")
        return output_path
