"""Catalogue grids always emit A–Z by name, never YAML file order."""

import re
from pathlib import Path

import yaml

import main

ROOT = Path(__file__).resolve().parent.parent


class _FakeEnv:
    def __init__(self, project_dir: Path) -> None:
        self.project_dir = str(project_dir)
        self.variables: dict = {}
        self.macros: dict = {}

    def macro(self, func):
        self.macros[func.__name__] = func
        return func


def _write_yaml(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _grid(tmp_path: Path, monkeypatch, *, organisations=None, projects=None, policies=None):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_yaml(data_dir / "organisations.yml", organisations or [])
    _write_yaml(data_dir / "projects.yml", projects or [])
    _write_yaml(data_dir / "policies.yml", policies or [])
    monkeypatch.setattr(main, "DATA_DIR", data_dir)
    env = _FakeEnv(ROOT)
    main.define_env(env)
    return env.macros["catalogue_grid"]


def _names(markup: str) -> list[str]:
    return re.findall(r'data-name="([^"]+)"', markup)


def test_category_pills_are_alphabetical():
    markup = main._categories_markup(["Zebra", "alpha", "Middle"])
    assert re.findall(r'catalogue-category">([^<]+)', markup) == [
        "alpha",
        "Middle",
        "Zebra",
    ]


def test_language_chip_is_separate_from_categories():
    markup = main._categories_markup(["CLI"], "Python")
    assert 'class="catalogue-language"' in markup
    assert 'class="catalogue-language__label">Lang:</span>' in markup
    assert 'class="catalogue-language__name" translate="no">Python</span>' in markup
    assert 'class="catalogue-category">CLI</button>' in markup
    assert 'catalogue-category">Python' not in markup


def test_sort_catalogue_by_name_ignores_yaml_order():
    items = [{"name": "Zebra"}, {"name": "alpha"}, {"name": "Middle"}]
    assert [item["name"] for item in main.sort_catalogue_by_name(items)] == [
        "alpha",
        "Middle",
        "Zebra",
    ]


def test_organisation_grid_is_alphabetical(tmp_path, monkeypatch):
    organisations = [
        {
            "id": "zebra",
            "published": True,
            "name": "Zebra Org",
            "icon": "material-domain",
            "publish_date": "2026-01-01",
            "description": "Z",
            "categories": ["Testing"],
            "logo": "https://example.com/z.png",
            "repository": "https://github.com/example/z",
        },
        {
            "id": "alpha",
            "published": True,
            "name": "Alpha Org",
            "icon": "material-domain",
            "publish_date": "2026-01-01",
            "description": "A",
            "categories": ["Testing"],
            "logo": "https://example.com/a.png",
            "repository": "https://github.com/example/a",
        },
    ]
    grid = _grid(tmp_path, monkeypatch, organisations=organisations)
    assert _names(grid("organisation", "organisation")) == ["Alpha Org", "Zebra Org"]


def test_organisation_card_local_logo_is_site_root_relative(tmp_path, monkeypatch):
    organisations = [
        {
            "id": "alpha",
            "published": True,
            "name": "Alpha Org",
            "icon": "material-domain",
            "publish_date": "2026-01-01",
            "description": "A",
            "categories": ["Testing"],
            "logo": "assets/images/organisations/organisation-actions-toolbox-logo.png",
            "repository": "https://github.com/example/a",
        }
    ]
    grid = _grid(tmp_path, monkeypatch, organisations=organisations)
    markup = grid("organisation", "organisation")
    assert 'src="/assets/images/organisations/organisation-actions-toolbox-logo.png"' in markup
    assert 'href="https://github.com/example/a"' in markup
    assert 'title="View the Alpha Org organisation on GitHub"' in markup
    assert "View on GitHub" not in markup


def test_policy_grid_is_alphabetical(tmp_path, monkeypatch):
    policies = [
        {
            "id": "support",
            "published": True,
            "name": "Support Guide",
            "icon": "material-book-open-page-variant",
            "description": "S",
            "categories": ["Testing"],
            "document": "https://github.com/example/s",
        },
        {
            "id": "conduct",
            "published": True,
            "name": "Code of Conduct",
            "icon": "material-book-open-page-variant",
            "description": "C",
            "categories": ["Testing"],
            "document": "https://github.com/example/c",
        },
    ]
    grid = _grid(tmp_path, monkeypatch, policies=policies)
    assert _names(grid("policy", "policy")) == ["Code of Conduct", "Support Guide"]
