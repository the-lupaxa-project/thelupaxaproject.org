import re
from datetime import date, timedelta
from pathlib import Path

import yaml

import main

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


def _synthetic_project(**overrides) -> dict:
    project = {
        "id": "synthetic-project",
        "published": True,
        "name": "Synthetic Project",
        "icon": "material-source-repository",
        "publish_date": "2025-01-01",
        "description": "A synthetic project used for testing.",
        "categories": ["Testing"],
        "organisation": "Test Org",
        "logo": "https://example.com/logo.png",
        "repository": "https://github.com/example/synthetic",
    }
    project.update(overrides)
    return project


def _catalogue_grid(tmp_path: Path, monkeypatch, projects: list[dict]):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_yaml(data_dir / "organisations.yml", [])
    _write_yaml(data_dir / "policies.yml", [])
    _write_yaml(data_dir / "projects.yml", projects)

    monkeypatch.setattr(main, "DATA_DIR", data_dir)

    env = _FakeEnv(ROOT)
    main.define_env(env)
    return env.macros["catalogue_grid"]


def test_project_card_shows_language_outside_the_category_filters(tmp_path, monkeypatch):
    catalogue_grid = _catalogue_grid(
        tmp_path,
        monkeypatch,
        [_synthetic_project(language="Python", categories=["CLI"])],
    )

    markup = catalogue_grid("project", "project")

    assert 'class="catalogue-language"' in markup
    assert 'class="catalogue-language__name" translate="no">Python</span>' in markup
    assert 'class="catalogue-category">CLI</button>' in markup
    assert 'catalogue-category">Python' not in markup


def test_website_card_shows_the_language_chip(tmp_path, monkeypatch):
    catalogue_grid = _catalogue_grid(
        tmp_path,
        monkeypatch,
        [
            _synthetic_project(
                website=True,
                language="Python",
                categories=["CLI"],
            )
        ],
    )

    markup = catalogue_grid("website", "website")

    assert 'class="catalogue-language__name" translate="no">Python</span>' in markup
    assert 'class="catalogue-category">CLI</button>' in markup

    websites_page = (ROOT / "mkdocs" / "websites.md").read_text(encoding="utf-8")
    projects_page = (ROOT / "mkdocs" / "projects.md").read_text(encoding="utf-8")
    assert "include_language=True" in websites_page
    assert "include_language=True" in projects_page


def test_project_card_defaults_missing_banner_to_in_development(tmp_path, monkeypatch):
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, [_synthetic_project()])

    markup = catalogue_grid("project", "project")

    assert "In Development" in markup
    assert "v0.1.0" not in markup
    assert 'data-banner-status="in-development"' in markup
    assert "catalogue-banner--red" in markup


def test_project_card_rejects_article_only_presets(tmp_path, monkeypatch):
    """Project cards must not render banners from the article-only preset set."""
    projects = [_synthetic_project(banner="new")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "catalogue-banner" not in markup
    assert "New Article" not in markup


def test_project_card_shows_fresh_released_banner(tmp_path, monkeypatch):
    fresh = date.today() - timedelta(days=1)
    projects = [_synthetic_project(banner="released", released_date=fresh.isoformat())]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "catalogue-banner" in markup
    assert "Released" in markup
    assert "v0.1.0" not in markup
    assert "Stable" not in markup
    assert f"{fresh.day} " in markup
    assert 'data-banner-status="released"' in markup
    assert "catalogue-banner--blue" in markup


def test_project_card_keeps_released_version_and_date(tmp_path, monkeypatch):
    released = date(2020, 1, 15)
    projects = [
        _synthetic_project(
            banner="released",
            released_date=released.isoformat(),
            version="1.2.0",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Released" in markup
    assert "Stable" not in markup
    assert "v1.2.0" in markup
    assert "15 Jan 2020" in markup
    assert 'data-banner-status="released"' in markup
    assert "catalogue-banner--blue" in markup
    assert "catalogue-banner--dark-blue" not in markup


def test_project_card_shows_released_version_without_date(tmp_path, monkeypatch):
    projects = [_synthetic_project(banner="released", version="0.3.1")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Version:" in markup
    assert "v0.3.1" in markup
    assert "Released:" not in markup
    assert "Stable" not in markup
    assert 'data-banner-status="released"' in markup
    assert "catalogue-banner--blue" in markup


def test_project_card_shows_non_time_limited_preset(tmp_path, monkeypatch):
    projects = [_synthetic_project(banner="in-development")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "catalogue-banner" in markup
    assert "In Development" in markup
    assert "v0.1.0" not in markup
    assert "catalogue-banner--red" in markup


def test_project_card_explicit_stable_without_version_omits_sash(tmp_path, monkeypatch):
    projects = [_synthetic_project(banner="stable")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "catalogue-banner" not in markup
    assert "Stable" not in markup
    assert "Released" not in markup
    assert "In Development" not in markup


def test_project_card_stable_with_version_renders_as_released(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            banner="stable",
            version="0.4.0",
            released_date="2026-03-02",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Released" in markup
    assert "Stable" not in markup
    assert "v0.4.0" in markup
    assert "2 Mar 2026" in markup
    assert 'data-banner-status="released"' in markup


def test_project_card_false_banner_omits_sash(tmp_path, monkeypatch):
    projects = [_synthetic_project(banner=False, released_date="2026-11-10")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "catalogue-banner" not in markup
    assert "In Development" not in markup
    assert "Released" not in markup


def test_project_card_unversioned_released_keeps_status_and_date(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            banner="released",
            released_date="2020-01-15",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Released:" in markup
    assert "15 Jan 2020" in markup
    assert "Version:" not in markup
    assert "v0.1.0" not in markup
    assert "Stable" not in markup
    assert 'data-banner-status="released"' in markup


def test_project_card_released_keeps_status_and_shows_version(tmp_path, monkeypatch):
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    projects = [
        _synthetic_project(
            banner="released",
            released_date=fresh_date,
            version="0.1.0",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Released" in markup
    assert "v0.1.0" in markup
    assert 'data-banner-status="released"' in markup
    assert "catalogue-banner--blue" in markup
    assert "catalogue-banner--dark-blue" not in markup


def test_project_card_later_version_stays_released(tmp_path, monkeypatch):
    fresh_date = (date.today() - timedelta(days=1)).isoformat()
    projects = [
        _synthetic_project(
            banner="released",
            released_date=fresh_date,
            version="1.2.0",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "Released" in markup
    assert "v1.2.0" in markup
    assert 'data-banner-status="released"' in markup
    assert "catalogue-banner--blue" in markup


def test_project_card_in_testing_omits_version(tmp_path, monkeypatch):
    projects = [_synthetic_project(banner="in-testing", version="1.2.0")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "In Testing" in markup
    assert "v1.2.0" not in markup
    assert 'data-banner-status="in-testing"' in markup
    assert "catalogue-banner--magenta" in markup


def test_website_updated_banner_centers_the_date_in_the_footer(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            website=True,
            banner="updated",
            released_date="2026-11-10T14:00:53",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("website", "website")

    assert "Updated:" in markup
    assert "10 Nov 2026" in markup
    assert "Version:" not in markup
    assert "catalogue-banner--split" not in markup
    assert 'data-banner-status="updated"' in markup
    assert "catalogue-banner--blue" in markup
    assert markup.index("catalogue-logo") < markup.index("catalogue-banner")


def test_lifecycle_banners_stay_centred_status_words(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(id="dev", name="Dev", banner="in-development"),
        _synthetic_project(id="test", name="Test", banner="in-testing"),
        _synthetic_project(id="review", name="Review", banner="in-review"),
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "In Development" in markup
    assert "In Testing" in markup
    assert "In Review" in markup
    assert "catalogue-banner--split" not in markup
    assert "Version:" not in markup


def test_website_card_uses_the_same_released_sash(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            website=True,
            banner="released",
            version="0.2.0",
            released_date="2026-11-11T14:05:53",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("website", "website")

    assert "Released" in markup
    assert "v0.2.0" in markup
    assert "11 Nov 2026" in markup
    assert "Stable" not in markup
    assert "catalogue-banner--blue" in markup


def test_catalogue_has_no_stable_banners():
    projects = yaml.safe_load((ROOT / "data" / "projects.yml").read_text(encoding="utf-8"))
    assert all(project.get("banner") != "stable" for project in projects)


def test_catalogue_grid_projects_emit_in_name_order(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(id="ccc", name="CCC"),
        _synthetic_project(id="action-lint", name="Action Lint"),
        _synthetic_project(id="aaa", name="AAA"),
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")
    names = re.findall(r'data-name="([^"]+)"', markup)

    assert names == ["AAA", "Action Lint", "CCC"]


def test_project_card_local_logo_is_site_root_relative(tmp_path, monkeypatch):
    """Raw HTML img src must work from /projects/, not only the homepage."""
    projects = [
        _synthetic_project(logo="assets/images/organisations/organisation-cicd-toolbox-logo.png")
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert 'src="/assets/images/organisations/organisation-cicd-toolbox-logo.png"' in markup


def test_project_card_keeps_remote_logo_url(tmp_path, monkeypatch):
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, [_synthetic_project()])

    markup = catalogue_grid("project", "project")

    assert 'src="https://example.com/logo.png"' in markup


def test_project_card_includes_publish_date_on_logo(tmp_path, monkeypatch):
    projects = [_synthetic_project(publish_date="2026-08-01")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert 'data-publish-date="2026-08-01"' in markup
    assert 'data-name="Synthetic Project"' in markup
    assert "catalogue-logo" in markup
    assert "data-released-date" not in markup


def test_project_card_omits_repository_and_documentation_links(tmp_path, monkeypatch):
    projects = [_synthetic_project(documentation="https://example.com/docs/")]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert "View on GitHub" not in markup
    assert 'class="catalogue-title-text">Synthetic Project</span>' in markup
    assert 'href="https://github.com/example/synthetic"' in markup
    assert 'title="View Synthetic Project on GitHub"' in markup
    assert 'href="https://example.com/docs/"' in markup
    assert 'title="Visit the Synthetic Project website"' in markup
    assert ":material-github:" in markup
    assert ":material-web:" in markup


def test_website_card_title_opens_the_repository(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            website=True,
            documentation="https://docs.example/site/",
            documentation_label="Visit Site",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("website", "website")

    assert 'class="catalogue-title-text">Synthetic Project</span>' in markup
    assert 'href="https://github.com/example/synthetic"' in markup
    assert 'title="View Synthetic Project on GitHub"' in markup
    assert 'href="https://docs.example/site/"' in markup
    assert 'title="Visit Synthetic Project"' in markup
    assert ":material-web:" in markup
    assert "View on GitHub" not in markup
    assert "Visit Site" not in markup
    assert markup.index("catalogue-logo") < markup.index("catalogue-banner")


def test_site_cards_use_visit_site_label():
    projects = yaml.safe_load((ROOT / "data" / "projects.yml").read_text(encoding="utf-8"))
    by_id = {project["id"]: project for project in projects}
    for project_id in (
        "browser-interrogator",
        "homebrew-tap",
        "opengraphtester.com",
        "snippets",
        "web-toolbox",
    ):
        assert by_id[project_id]["documentation_label"] == "Visit Site"
        assert by_id[project_id]["website"] is True


def test_website_cards_leave_the_projects_grid(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(),
        _synthetic_project(
            id="example-site",
            name="Example Site",
            website=True,
            documentation="https://example.com/",
            documentation_label="Visit Site",
        ),
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    projects_markup = catalogue_grid("project", "project")
    websites_markup = catalogue_grid("website", "website")

    assert "Synthetic Project" in projects_markup
    assert "Example Site" not in projects_markup
    assert "Example Site" in websites_markup
    assert "Synthetic Project" not in websites_markup
    assert "Visit Site" not in websites_markup
    assert 'title="View Example Site on GitHub"' in websites_markup


def test_nav_lists_websites_between_projects_and_articles():
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    projects = "- Projects: projects.md"
    websites = "- Websites: websites.md"
    articles = "- Articles: articles.md"
    assert projects in nav
    assert websites in nav
    assert nav.index(projects) < nav.index(websites) < nav.index(articles)


def test_project_card_title_is_searchable_heading(tmp_path, monkeypatch):
    """Site search deep-links to the card via a heading id matching YAML id."""
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, [_synthetic_project()])

    markup = catalogue_grid("project", "project")

    assert 'class="catalogue-title-text">Synthetic Project</span>' in markup
    assert 'href="https://github.com/example/synthetic"' in markup
    assert 'title="View Synthetic Project on GitHub"' in markup
    assert 'target="_blank"' in markup
    assert ">Synthetic Project</a>" not in markup
    assert "{ #synthetic-project .no_toc translate=no }" in markup
    assert markup.index("catalogue-logo") < markup.index("catalogue-banner")


def test_project_card_includes_released_date_time_on_logo(tmp_path, monkeypatch):
    projects = [
        _synthetic_project(
            publish_date="2026-08-01T09:00:00",
            released_date="2026-08-17T14:00:00",
        )
    ]
    catalogue_grid = _catalogue_grid(tmp_path, monkeypatch, projects)

    markup = catalogue_grid("project", "project")

    assert 'data-publish-date="2026-08-01T09:00:00"' in markup
    assert 'data-released-date="2026-08-17T14:00:00"' in markup
