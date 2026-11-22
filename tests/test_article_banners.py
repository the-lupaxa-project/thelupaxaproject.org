from datetime import date
from pathlib import Path

from articles_lib import (
    ARTICLE_BANNER_EXPIRY_DAYS,
    _article_entry,
    rebuild_articles_index,
)

TODAY = date(2026, 7, 31)


def _meta(**overrides):
    meta = {
        "title": "Example Article",
        "published": True,
        "description": "An example article used by the tests.",
        "tags": ["Engineering"],
    }
    meta.update(overrides)
    return meta


def test_article_expiry_default_is_28_days():
    assert ARTICLE_BANNER_EXPIRY_DAYS == 28


def test_new_banner_renders_for_recent_article():
    entry = _article_entry("example", _meta(banner="new", publish_date="2026-07-20"), today=TODAY)

    assert 'data-banner-status="new"' in entry
    assert "New Article" in entry
    assert "catalogue-banner--blue" in entry


def test_new_banner_sits_between_title_and_image():
    entry = _article_entry("example", _meta(banner="new", publish_date="2026-07-20"), today=TODAY)

    title = entry.index("**[")
    banner = entry.index("catalogue-banner")
    image = entry.index("catalogue-logo")

    assert "    ---" not in entry
    assert title < banner < image


def test_new_banner_hidden_after_expiry():
    entry = _article_entry("example", _meta(banner="new", publish_date="2026-01-01"), today=TODAY)

    assert "catalogue-banner" not in entry


def test_new_banner_hidden_without_publish_date():
    entry = _article_entry("example", _meta(banner="new"), today=TODAY)

    assert "catalogue-banner" not in entry


def test_article_without_banner_is_unchanged():
    entry = _article_entry("example", _meta(publish_date="2026-07-20"), today=TODAY)

    assert "catalogue-banner" not in entry
    assert "![Article](assets/images/articles/example.webp)" in entry


def test_project_presets_do_not_apply_to_articles():
    entry = _article_entry(
        "example", _meta(banner="released", publish_date="2026-07-20"), today=TODAY
    )

    assert "catalogue-banner" not in entry


def _build_index(tmp_path: Path, *, banner: str | None = None) -> str:
    articles = tmp_path / "articles"
    articles.mkdir(parents=True)
    banner_line = f"banner: {banner}\n" if banner else ""
    (articles / "example.md").write_text(
        "---\n"
        "title: Example Article\n"
        "published: true\n"
        "publish_date: '2026-07-20'\n"
        f"{banner_line}"
        "description: An example article.\n"
        "---\n\n"
        "# Example Article\n",
        encoding="utf-8",
    )
    rebuild_articles_index(tmp_path, today=TODAY)
    return (tmp_path / "articles.md").read_text(encoding="utf-8")


def test_index_header_has_status_filter(tmp_path):
    text = _build_index(tmp_path)

    assert 'data-article-status="all"' in text
    assert 'data-article-status="new"' in text
    assert 'id="article-status"' not in text


def test_index_header_documents_expiry_days(tmp_path):
    text = _build_index(tmp_path)

    assert f'data-banner-expiry-days="{ARTICLE_BANNER_EXPIRY_DAYS}"' in text


def test_index_card_keeps_list_structure_with_banner(tmp_path):
    text = _build_index(tmp_path, banner="new")

    assert "-   **[Example Article](articles/example.md)**" in text
    assert 'data-banner-status="new"' in text
