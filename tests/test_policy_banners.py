from datetime import date, timedelta
from pathlib import Path

import yaml

import main
from banner_lib import POLICY_BANNER_PRESETS, banner_markup

ROOT = Path(__file__).resolve().parent.parent


class _FakeEnv:
    """Minimal stand-in for the mkdocs-macros environment used by define_env."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = str(project_dir)
        self.variables: dict = {}
        self.macros: dict = {}

    def macro(self, func):
        self.macros[func.__name__] = func
        return func


def _write_yaml(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _synthetic_policy(**overrides) -> dict:
    policy = {
        "id": "synthetic-policy",
        "published": True,
        "name": "Synthetic Policy",
        "icon": "material-book-open-page-variant",
        "description": "A synthetic policy used for testing.",
        "categories": ["Testing"],
        "document": "https://github.com/example/synthetic",
    }
    policy.update(overrides)
    return policy


def _catalogue_grid(tmp_path: Path, monkeypatch, policies: list[dict]):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_yaml(data_dir / "organisations.yml", [])
    _write_yaml(data_dir / "projects.yml", [])
    _write_yaml(data_dir / "policies.yml", policies)

    monkeypatch.setattr(main, "DATA_DIR", data_dir)

    env = _FakeEnv(ROOT)
    main.define_env(env)
    return env.macros["catalogue_grid"]


def test_policy_presets():
    assert POLICY_BANNER_PRESETS["new"] == ("New Policy", "blue")
    assert POLICY_BANNER_PRESETS["updated"] == ("Updated Policy", "purple")


def test_new_policy_fresh():
    html = banner_markup("new", presets=POLICY_BANNER_PRESETS, event_date=date(2026, 7, 31), today=date(2026, 7, 31), expiry_days=28, time_limited_statuses=frozenset({"new", "updated"}))
    assert "New Policy" in html and "catalogue-banner--blue" in html


def test_updated_policy_fresh():
    html = banner_markup("updated", presets=POLICY_BANNER_PRESETS, event_date=date(2026, 7, 20), today=date(2026, 7, 31), expiry_days=28, time_limited_statuses=frozenset({"new", "updated"}))
    assert "Updated Policy" in html and "catalogue-banner--purple" in html


def test_policy_new_does_not_use_article_label():
    html = banner_markup("new", presets=POLICY_BANNER_PRESETS, event_date=date(2026, 7, 31), today=date(2026, 7, 31), expiry_days=28, time_limited_statuses=frozenset({"new", "updated"}))
    assert "New Article" not in html


def test_policy_card_categories_are_labels(tmp_path, monkeypatch):
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, [_synthetic_policy()])

    markup = catalogue_grid("policy", "policy")

    assert 'class="catalogue-category">Testing</span>' in markup
    assert 'class="catalogue-category">Testing</button>' not in markup


def test_policy_card_shows_fresh_new_banner(tmp_path, monkeypatch):
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    policies = [_synthetic_policy(banner="new", publish_date=fresh_date)]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" in markup
    assert "New Policy" in markup
    assert "catalogue-banner--blue" in markup


def test_policy_card_shows_fresh_updated_banner(tmp_path, monkeypatch):
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    policies = [_synthetic_policy(banner="updated", updated_date=fresh_date)]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" in markup
    assert "Updated Policy" in markup
    assert "catalogue-banner--purple" in markup


def test_policy_card_hides_expired_new_banner(tmp_path, monkeypatch):
    expired_date = (date.today() - timedelta(days=400)).isoformat()
    policies = [_synthetic_policy(banner="new", publish_date=expired_date)]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" not in markup


def test_policy_card_hides_new_banner_without_publish_date(tmp_path, monkeypatch):
    policies = [_synthetic_policy(banner="new")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" not in markup


def test_policy_card_uses_updated_date_not_publish_date_for_updated_banner(tmp_path, monkeypatch):
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    expired_date = (date.today() - timedelta(days=400)).isoformat()
    policies = [_synthetic_policy(banner="updated", publish_date=fresh_date, updated_date=expired_date)]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" not in markup


def test_policy_card_without_banner_is_unchanged(tmp_path, monkeypatch):
    policies = [_synthetic_policy()]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "catalogue-banner" not in markup
    assert "Synthetic Policy" in markup
    assert 'href="https://github.com/example/synthetic"' in markup
    assert 'title="View Synthetic Policy on GitHub"' in markup
    assert "View on GitHub" not in markup


def test_policy_card_includes_default_brand_logo(tmp_path, monkeypatch):
    policies = [_synthetic_policy()]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert 'class="catalogue-logo-wrap"' in markup
    assert 'class="catalogue-logo"' in markup
    assert 'data-name="Synthetic Policy"' in markup
    assert 'src="/assets/images/organisations/organisation-the-lupaxa-project-logo.png"' in markup
    assert 'alt="The Lupaxa Project"' in markup


def test_policy_card_allows_logo_override(tmp_path, monkeypatch):
    policies = [_synthetic_policy(logo="https://example.com/custom-policy.png", logo_alt="Custom Policy Mark")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, policies)

    markup = catalogue_grid("policy", "policy")

    assert "https://example.com/custom-policy.png" in markup
    assert 'alt="Custom Policy Mark"' in markup
