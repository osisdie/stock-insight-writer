"""Slug generation utilities."""

from slugify import slugify as _slugify


def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate a URL-safe slug from text.

    Args:
        text: Input text to slugify
        max_length: Maximum length of the slug

    Returns:
        URL-safe slug string
    """
    return _slugify(text, max_length=max_length, word_boundary=True)
