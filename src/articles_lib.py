"""Helpers for article front matter and the articles index page."""

from __future__ import annotations

import html
import textwrap
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from banner_lib import (
    ARTICLE_BANNER_PRESETS,
    banner_markup,
    format_publish_date_attr,
    parse_iso_date,
)
from main import filter_panel_toolbar

# Days a "New Article" banner stays visible after `publish_date`.
ARTICLE_BANNER_EXPIRY_DAYS = 28
_ARTICLE_TIME_LIMITED = frozenset({"new"})

# Optional shorter titles for cards / pager (page H1 can stay longer).
ARTICLE_CARD_TITLES: dict[str, str] = {}

ARTICLE_TAGS: dict[str, list[str]] = {
    "certificates-without-the-jargon": ["Security", "Tools", "Certificates"],
    "cli-design": ["Engineering", "Tools", "CLI"],
    "coding-standards": ["Engineering", "Standards"],
    "config-design": ["Engineering", "Tools", "Configuration"],
    "containers-for-cli-tools": ["Security", "Tools", "Containers"],
    "contributing-without-the-drama": ["Open Source", "Community", "Contributing"],
    "cybersecurity-and-chess": ["Security", "Strategy"],
    "dependency-hygiene": ["Security", "Engineering", "Dependencies"],
    "deprecation-without-chaos": ["Open Source", "Engineering", "Process"],
    "docs-that-dont-rot": ["Documentation", "Open Source"],
    "encryption-at-rest-for-repos": ["Security", "Git", "Encryption"],
    "error-handling-people-can-use": ["Engineering", "Tools", "CLI"],
    "git-workflows-for-tiny-teams": ["Engineering", "Process", "Git"],
    "github-actions": ["CI/CD", "GitHub"],
    "input-validation-that-sticks": ["Security", "Engineering"],
    "key-lifecycle": ["Security", "Engineering", "Encryption"],
    "least-privilege-for-ci": ["Security", "CI/CD"],
    "licenses-for-humans": ["Open Source", "Community", "Licenses"],
    "maintainer-boundaries": ["Open Source", "Community", "Maintainers"],
    "mtls-and-client-certificates": ["Security", "Certificates"],
    "observability-for-small-projects": ["Engineering", "DevOps", "Observability"],
    "programming-fundamentals": ["Engineering", "Fundamentals"],
    "readme-as-product": ["Open Source", "Documentation"],
    "red-team-vs-blue-team": ["Security", "Ops"],
    "release-automation": ["CI/CD", "Open Source", "Automation"],
    "reproducible-builds": ["Security", "Engineering"],
    "responsible-dependency-updates": ["Security", "Engineering", "Dependencies"],
    "right-tools-for-the-job": ["Tools", "Engineering"],
    "sast-and-dast": ["Security", "Engineering", "Testing"],
    "secrets-management": ["Security", "DevOps"],
    "secure-defaults": ["Security", "Design"],
    "secure-logging": ["Security", "Engineering"],
    "security-by-design": ["Security", "Design"],
    "security-disclosures-that-work": ["Security", "Open Source", "Vulnerability Reporting"],
    "semantic-versioning": ["Open Source", "Engineering", "Standards"],
    "supply-chain-signing": ["Security", "Open Source"],
    "testing-what-matters": ["Engineering", "Testing"],
    "the-cybersecurity-rainbow": ["Security", "Ops"],
    "the-optimization-trap": ["Engineering", "Mindset"],
    "threat-modelling-for-small-tools": ["Security", "Engineering", "Design"],
    "understanding-ci-cd": ["CI/CD", "DevOps"],
    "practical-security-md": ["Security", "Open Source", "Documentation"],
}


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Return (meta, body) for a Markdown document with optional YAML front matter."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta = yaml.safe_load(raw) or {}
    if not isinstance(meta, dict):
        return {}, text
    return meta, body


def is_published(meta: dict[str, Any]) -> bool:
    """Articles are published unless explicitly set to false."""
    return bool(meta.get("published", True))


def load_article_meta(path: Path) -> dict[str, Any]:
    return split_front_matter(path.read_text(encoding="utf-8"))[0]


def display_title(slug: str, meta: dict[str, Any]) -> str:
    if slug in ARTICLE_CARD_TITLES:
        return ARTICLE_CARD_TITLES[slug]
    title = meta.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return slug.replace("-", " ").title()


def article_tags(slug: str, meta: dict[str, Any]) -> list[str]:
    tags = meta.get("tags")
    if isinstance(tags, list) and tags:
        return [str(tag) for tag in tags]
    return list(ARTICLE_TAGS.get(slug, ["Engineering"]))


def format_front_matter(
    *,
    title: str,
    published: bool = True,
    description: str = "",
    tags: list[str] | None = None,
    publish_date: str = "",
) -> str:
    payload: dict[str, Any] = {
        "title": title,
        "published": published,
        "hide": ["navigation", "toc"],
    }
    if publish_date:
        payload["publish_date"] = publish_date
    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags
    dumped = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    return f"---\n{dumped}\n---\n\n"


def _article_entry(slug: str, meta: dict[str, Any], *, today: date | None = None) -> str:
    title = display_title(slug, meta)
    desc = str(meta.get("description") or "").strip()
    tags = article_tags(slug, meta)
    desc_lines = textwrap.wrap(desc, width=72) or [""]
    desc_block = "\n    ".join(desc_lines)
    tag_spans = "\n    ".join(
        f'<span class="catalogue-category">{tag}</span>' for tag in sorted(tags, key=str.casefold)
    )
    publish_date = parse_iso_date(meta.get("publish_date"))
    banner = banner_markup(
        meta.get("banner"),
        presets=ARTICLE_BANNER_PRESETS,
        event_date=publish_date,
        today=today,
        expiry_days=ARTICLE_BANNER_EXPIRY_DAYS,
        time_limited_statuses=_ARTICLE_TIME_LIMITED,
    )
    banner_block = f"{banner}\n\n" if banner else ""
    publish_date_value = format_publish_date_attr(meta.get("publish_date"))
    date_attr = (
        f' data-publish-date="{publish_date_value}"' if publish_date_value is not None else ""
    )
    name_attr = f' data-name="{html.escape(title, quote=True)}"'
    return (
        f"-   **[{title}](articles/{slug}.md)**\n"
        f"\n"
        f"{banner_block}"
        f'    ![Article](assets/images/articles/{slug}.webp){{ class="catalogue-logo"{name_attr}{date_attr} }}\n'
        f"\n"
        f"    {desc_block}\n"
        f"\n"
        f"    {tag_spans}\n"
    )


def rebuild_articles_index(docs_dir: Path, *, today: date | None = None) -> int:
    """Rewrite articles.md from published article front matter. Returns count."""
    articles_dir = docs_dir / "articles"
    index_path = docs_dir / "articles.md"
    items: list[tuple[str, dict[str, Any]]] = []

    for path in sorted(articles_dir.glob("*.md")):
        meta = load_article_meta(path)
        if not is_published(meta):
            continue
        items.append((path.stem, meta))

    items.sort(key=lambda item: display_title(item[0], item[1]).casefold())
    entries = "\n".join(_article_entry(slug, meta, today=today) for slug, meta in items)

    # Insert toolbar after dedent — embedding it in the f-string breaks
    # textwrap.dedent (zero-indent line) and corrupts YAML front matter.
    header = textwrap.dedent(
        f"""\
        ---
        hide:
          - navigation
          - toc
        ---

        <div class="filter-panel filter-panel--with-sort" data-article-filters data-banner-expiry-days="{ARTICLE_BANNER_EXPIRY_DAYS}" markdown="0">
        __FILTER_TOOLBAR__
          <div class="filter-panel-search">
            <label for="article-search">Search articles</label>
            <input
              id="article-search"
              type="search"
              placeholder="Search by title, description, or tag"
              autocomplete="off"
              data-article-search
            />
          </div>
          <div class="filter-panel-select">
            <label for="article-category">Tag</label>
            <select id="article-category" data-article-category>
              <option value="">All Tags</option>
            </select>
          </div>
          <div class="filter-panel-toggle" role="group" aria-labelledby="article-status-label">
            <label id="article-status-label">View Articles</label>
            <div class="filter-panel-toggle__options">
              <button
                type="button"
                class="filter-panel-toggle__option"
                data-article-status="all"
                aria-pressed="true"
              >
                All
              </button>
              <button
                type="button"
                class="filter-panel-toggle__option"
                data-article-status="new"
                aria-pressed="false"
              >
                New
              </button>
            </div>
          </div>
          <div class="filter-panel-toggle" role="group" aria-labelledby="article-sort-label">
            <label id="article-sort-label">Sort</label>
            <div class="filter-panel-toggle__options">
              <button
                type="button"
                class="filter-panel-toggle__option"
                data-article-sort="alpha"
                aria-pressed="true"
              >
                A–Z
              </button>
              <button
                type="button"
                class="filter-panel-toggle__option"
                data-article-sort="newest"
                aria-pressed="false"
              >
                Newest
              </button>
            </div>
          </div>
          <div class="filter-panel-actions">
            <button
              type="button"
              class="md-button lupaxa-button filter-panel-clear"
              data-article-clear
            >
              Clear filters
            </button>
          </div>
        </div>

        <div class="grid cards catalogue-grid catalogue-grid--articles" data-article-catalogue markdown>

        """
    ).replace(
        "__FILTER_TOOLBAR__",
        filter_panel_toolbar(prefix="article", summary_text="Showing…").rstrip("\n"),
    )
    footer = textwrap.dedent(
        """
        </div>

        <div class="catalogue-empty-state" data-article-empty hidden markdown>

        :material-magnify: No articles match the current filters.

        Try clearing the search or choosing a different tag or status.

        </div>
        """
    )
    # Only write when content changes — unconditional writes retrigger
    # `mkdocs serve` watch and cause a rebuild loop.
    content = header + entries + footer
    if index_path.exists() and index_path.read_text(encoding="utf-8") == content:
        return len(items)

    index_path.write_text(content, encoding="utf-8")
    return len(items)
