"""Sponsor page nav, copy, and Ko-fi embed."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MKDOCS_YML = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
INDEX_MD = (ROOT / "mkdocs/index.md").read_text(encoding="utf-8")
SPONSOR_MD = (ROOT / "mkdocs/sponsor.md").read_text(encoding="utf-8")


def test_nav_lists_humour_then_policies_then_sponsor():
    articles = "- Articles: articles.md"
    humour = "- Humour: humour.md"
    policies = "- Policies: policies.md"
    sponsor = "- Sponsor: sponsor.md"
    assert articles in MKDOCS_YML
    assert humour in MKDOCS_YML
    assert policies in MKDOCS_YML
    assert sponsor in MKDOCS_YML
    assert (
        MKDOCS_YML.index(articles)
        < MKDOCS_YML.index(humour)
        < MKDOCS_YML.index(policies)
        < MKDOCS_YML.index(sponsor)
    )
    assert "assets/stylesheets/50-pages/sponsor.css" in MKDOCS_YML


def test_sponsor_page_states_time_then_costs_and_embeds_kofi():
    time_at = SPONSOR_MD.index("**Time**")
    costs_at = SPONSOR_MD.index("**Running costs**")
    ai_at = SPONSOR_MD.index("**AI subscriptions**")
    assert time_at < costs_at < ai_at
    assert "\n# Sponsor\n" not in SPONSOR_MD
    assert (
        'src="https://ko-fi.com/thelupaxaproject/?hidefeed=true&widget=true&embed=true"'
    ) in SPONSOR_MD
    assert 'aria-label="Support The Lupaxa Project on Ko-fi"' in SPONSOR_MD
    assert "title=" not in SPONSOR_MD
    assert 'href="https://ko-fi.com/thelupaxaproject"' in SPONSOR_MD
    assert 'rel="noopener noreferrer"' in SPONSOR_MD
    assert 'target="_blank"' in SPONSOR_MD
    assert "overlay-widget.js" not in SPONSOR_MD


def test_home_who_we_are_links_to_sponsor():
    assert '<a href="sponsor/">Sponsor</a>' in INDEX_MD
    assert "volunteer-led" in INDEX_MD


def test_home_hero_does_not_repeat_navigation():
    hero = INDEX_MD.split("## Who We Are", 1)[0]
    assert "lupaxa-hero-actions" not in hero
    assert "Become a Sponsor" not in hero
    assert "Browse Organisations" not in INDEX_MD
