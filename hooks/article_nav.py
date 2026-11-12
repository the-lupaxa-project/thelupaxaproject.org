"""MkDocs hook: article pager + rebuild published articles index."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
_SRC = PROJECT_DIR / "src"
for _path in (_SRC, PROJECT_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

_ARTICLE_SEQUENCE: list[dict[str, str]] | None = None

_ARTICLE_H1_RE = re.compile(
    r"(<h1\b[^>]*>)(.*?)(</h1>)",
    re.IGNORECASE | re.DOTALL,
)


def _split_article_h1(match: re.Match[str]) -> str:
    """Put text after the first colon on a new italic line."""
    open_tag, content, close_tag = match.groups()
    colon_at = content.find(":")
    if colon_at < 0:
        return match.group(0)

    lead = content[: colon_at + 1]
    subtitle = content[colon_at + 1 :].lstrip()
    if not subtitle:
        return match.group(0)

    return (
        f"{open_tag}"
        f'<span class="article-title-lead">{lead}</span>'
        f'<span class="article-title-sub">{subtitle}</span>'
        f"{close_tag}"
    )


def _article_lib():
    """Return articles helpers, reloaded during ``mkdocs serve``."""
    import importlib

    import articles_lib
    import banner_lib

    if banner_lib.DEV_SERVER:
        importlib.reload(articles_lib)
    return articles_lib


def _build_sequence(config) -> list[dict[str, str]]:
    lib = _article_lib()
    docs_dir = Path(config["docs_dir"])
    articles_dir = docs_dir / "articles"
    if not articles_dir.is_dir():
        return []

    use_directory_urls = config["use_directory_urls"]
    articles: list[dict[str, str]] = []

    for path in articles_dir.glob("*.md"):
        meta = lib.load_article_meta(path)
        if not lib.is_published(meta):
            continue

        slug = path.stem
        title = lib.display_title(slug, meta)
        if use_directory_urls:
            url = f"articles/{slug}/"
        else:
            url = f"articles/{slug}.html"
        articles.append(
            {
                "slug": slug,
                "title": title,
                "src_uri": f"articles/{slug}.md",
                "url": url,
            }
        )

    articles.sort(key=lambda item: item["title"].casefold())
    return articles


def on_pre_build(config):
    """Keep articles.md in sync with published front matter."""
    global _ARTICLE_SEQUENCE
    docs_dir = Path(config["docs_dir"])
    _article_lib().rebuild_articles_index(docs_dir)
    _ARTICLE_SEQUENCE = _build_sequence(config)


def on_page_content(html, page, config, files):
    """Format article H1 as lead + italic subtitle after the first colon."""
    if not page.file.src_uri.startswith("articles/"):
        return html
    return _ARTICLE_H1_RE.sub(_split_article_h1, html, count=1)


def on_page_context(context, page, config, nav):
    global _ARTICLE_SEQUENCE
    if _ARTICLE_SEQUENCE is None:
        _ARTICLE_SEQUENCE = _build_sequence(config)

    src = page.file.src_uri
    if not src.startswith("articles/"):
        return context

    sequence = _ARTICLE_SEQUENCE
    index = next(
        (i for i, item in enumerate(sequence) if item["src_uri"] == src),
        None,
    )
    if index is None:
        context["article_prev"] = None
        context["article_next"] = None
        return context

    context["article_prev"] = sequence[index - 1] if index > 0 else None
    context["article_next"] = sequence[index + 1] if index < len(sequence) - 1 else None
    context["article_position"] = index + 1
    context["article_count"] = len(sequence)
    return context
