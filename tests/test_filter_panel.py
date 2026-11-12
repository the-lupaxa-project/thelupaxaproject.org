import re
from pathlib import Path

import pytest
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


def _filter_panel():
    env = _FakeEnv(ROOT)
    main.define_env(env)
    return env.macros["filter_panel"]


def test_filter_panel_status_options_project_lifecycle_only():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "project",
        search_label="Search",
        search_placeholder="Search projects",
        summary_text="Showing all projects",
        include_status=True,
    )

    assert "Released" in markup
    assert "In Review" in markup
    assert "In Planning" not in markup
    assert "Closed Alpha" not in markup
    assert "Open Beta" not in markup
    assert "New Article" not in markup
    assert "Updated Policy" not in markup


def test_filter_panel_without_status_does_not_crash():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "organisation",
        search_label="Search",
        search_placeholder="Search organisations",
        summary_text="Showing all organisations",
        include_status=False,
    )

    assert "filter-panel" in markup
    assert "Released" not in markup


def test_filter_panel_status_options_project_has_released_not_stable():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "project",
        search_label="Search",
        search_placeholder="Search projects",
        summary_text="Showing all projects",
        include_status=True,
    )

    assert markup.count('value="released"') == 1
    assert ">Released<" in markup
    assert markup.count('value="updated"') == 1
    assert ">Updated<" in markup
    assert 'value="stable"' not in markup
    assert ">Stable<" not in markup


def test_filter_panel_policy_page_omits_status_toggle():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "policy",
        compact=True,
        search_label="Search policies",
        search_placeholder="Search by policy name or description",
        summary_text="Showing…",
    )

    assert "View Policies" not in markup
    assert "data-policy-status" not in markup
    assert "filter-panel-toggle" not in markup
    assert "data-policy-search" in markup
    assert "data-policy-category" in markup
    assert "data-policy-clear" in markup


def test_filter_panel_status_options_policy_presets_no_stable():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "policy",
        compact=True,
        search_label="Search",
        search_placeholder="Search policies",
        summary_text="Showing all policies",
        include_status=True,
        status_kind="policy",
        status_label="View Policies",
    )

    assert "View Policies" in markup
    assert 'data-policy-status="all"' in markup
    assert 'data-policy-status="new"' in markup
    assert 'data-policy-status="updated"' in markup
    assert "filter-panel-toggle" in markup
    assert 'id="policy-status"' not in markup
    assert "Stable" not in markup
    assert "In Development" not in markup


def test_filter_panel_status_kind_unrecognised_raises():
    filter_panel = _filter_panel()

    with pytest.raises(ValueError):
        filter_panel(
            "policy",
            search_label="Search",
            search_placeholder="Search policies",
            summary_text="Showing all policies",
            include_status=True,
            status_kind="bogus",
        )


def test_filter_panel_includes_collapse_toolbar():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "organisation",
        compact=True,
        search_label="Search",
        search_placeholder="Search organisations",
        summary_text="Showing all organisations",
    )

    assert "filter-panel-toolbar" in markup
    assert "data-filter-expand" in markup
    assert "filter-panel-expand__icon--show" in markup
    assert "filter-panel-expand__icon--hide" in markup
    assert "filter-panel-expand__label" in markup
    assert "Show Filters" in markup
    assert "data-organisation-summary" in markup
    # Summary sits in the toolbar (same row as Show Filters)
    assert markup.index("filter-panel-toolbar") < markup.index("data-organisation-summary")
    assert markup.index("data-organisation-summary") < markup.index("filter-panel-search")


def test_filter_panel_lists_every_organisation_from_yaml():
    filter_panel = _filter_panel()
    organisations = yaml.safe_load((ROOT / "data" / "organisations.yml").read_text())
    published_names = [item["name"] for item in organisations if item.get("published", True)]

    markup = filter_panel(
        "project",
        search_label="Search",
        search_placeholder="Search projects",
        summary_text="Showing all projects",
        include_organisation=True,
    )

    for name in published_names:
        assert f">{name}</option>" in markup

    org_labels = re.findall(
        r'<select id="project-organisation"[^>]*>.*?</select>',
        markup,
        flags=re.S,
    )[0]
    option_labels = re.findall(r"<option[^>]*>(.*?)</option>", org_labels)
    assert option_labels[0] == "All Organisations"
    assert option_labels[1:] == sorted(published_names, key=str.casefold)
    assert "AWS Toolbox" in option_labels
    assert "The Lupaxa Lab" in option_labels


def test_filter_panel_category_options_stay_empty_in_markup():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "project",
        search_label="Search",
        search_placeholder="Search projects",
        summary_text="Showing all projects",
        include_organisation=True,
        include_status=True,
    )

    category_block = re.findall(
        r'<select id="project-category"[^>]*>.*?</select>',
        markup,
        flags=re.S,
    )[0]
    assert category_block.count("<option") == 1
    assert "All Categories" in category_block


def test_filter_panel_include_sort_adds_toggle():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "project",
        search_label="Search",
        search_placeholder="Search projects",
        summary_text="Showing all projects",
        include_organisation=True,
        include_status=True,
        include_sort=True,
    )

    assert "filter-panel--with-sort" in markup
    assert 'id="project-sort-label">Sort</label>' in markup
    assert 'data-project-sort="alpha"' in markup
    assert 'data-project-sort="newest"' in markup
    assert "A–Z" in markup
    assert "Newest" in markup
    assert markup.index("project-status") < markup.index("project-sort-label")
    assert markup.index("project-sort-label") < markup.index("filter-panel-actions")


def test_filter_panel_organisation_sort_toggle():
    filter_panel = _filter_panel()

    markup = filter_panel(
        "organisation",
        compact=True,
        search_label="Search",
        search_placeholder="Search organisations",
        summary_text="Showing all organisations",
        include_sort=True,
    )

    assert "filter-panel--compact" in markup
    assert "filter-panel--with-sort" in markup
    assert 'data-organisation-sort="alpha"' in markup
    assert 'data-organisation-sort="newest"' in markup
