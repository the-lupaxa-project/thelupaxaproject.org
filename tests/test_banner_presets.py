from datetime import date

from banner_lib import (
    DEFAULT_PROJECT_VERSION,
    PROJECT_BANNER_PRESETS,
    banner_markup,
    day_ordinal,
    format_release_date,
    normalise_project_version,
    resolve_banner,
    resolve_project_version,
)

EXPECTED_PROJECT = {
    "in-development": ("In Development", "red"),
    "in-testing": ("In Testing", "magenta"),
    "in-review": ("In Review", "purple"),
    "released": ("Released", "blue"),
    "updated": ("Updated", "blue"),
}


def test_project_presets():
    assert PROJECT_BANNER_PRESETS == EXPECTED_PROJECT


def test_resolve_banner_string_presets():
    for slug, (label, tone) in EXPECTED_PROJECT.items():
        assert resolve_banner(slug) == (label, tone, slug)
    assert resolve_banner("new") is None


def test_unknown_preset_string_does_not_resolve():
    assert resolve_banner("coming-soon") is None


def test_custom_override_still_works():
    assert resolve_banner({"status": "in-testing", "label": "QA", "tone": "orange"}) == (
        "QA",
        "orange",
        "in-testing",
    )


def test_normalise_project_version():
    assert normalise_project_version("1.2.0") == "1.2.0"
    assert normalise_project_version("v1.2.0") == "1.2.0"
    assert normalise_project_version("V2.0") == "2.0"
    assert normalise_project_version("") is None
    assert normalise_project_version(None) is None


def test_resolve_project_version_defaults_to_semver_start():
    assert DEFAULT_PROJECT_VERSION == "0.1.0"
    assert resolve_project_version(None) == "0.1.0"
    assert resolve_project_version("1.2.0") == "1.2.0"


def test_release_date_uses_the_day_ordinal():
    assert [day_ordinal(day) for day in (1, 2, 3, 4, 11, 12, 13, 21, 22, 23, 31)] == [
        "st",
        "nd",
        "rd",
        "th",
        "th",
        "th",
        "th",
        "st",
        "nd",
        "rd",
        "st",
    ]
    assert format_release_date(date(2026, 11, 11)) == "11th Nov 2026"
    assert format_release_date(date(2026, 3, 2)) == "2nd Mar 2026"
    assert format_release_date(date(2020, 1, 1)) == "1st Jan 2020"


def test_released_banner_includes_version_and_date():
    html = banner_markup(
        "released",
        presets=PROJECT_BANNER_PRESETS,
        event_date=date(2026, 11, 11),
        version="1.2.0",
    )
    assert "Version:" in html
    assert "Released:" in html
    assert '<span translate="no">v1.2.0</span>' in html
    assert (
        '<span translate="no">'
        '<span class="catalogue-ordinal" data-ordinal="th">11</span> Nov 2026'
        "</span>"
    ) in html
    assert "11th Nov 2026" in html
    assert "catalogue-banner--split" in html
    assert "catalogue-banner--with-version" in html
    assert "catalogue-banner--blue" in html
    assert "catalogue-banner--dark-blue" not in html
    assert 'data-banner-status="released"' in html
    assert 'class="catalogue-banner__date"' in html


def test_lifecycle_banners_omit_version():
    html = banner_markup(
        "in-testing",
        presets=PROJECT_BANNER_PRESETS,
        version="1.2.0",
        default_version=DEFAULT_PROJECT_VERSION,
        event_date=date(2026, 11, 11),
    )
    assert "In Testing" in html
    assert "v1.2.0" not in html
    assert "v0.1.0" not in html
    assert "11 Nov 2026" not in html
    assert 'data-banner-status="in-testing"' in html


def test_in_review_omits_default_version():
    html = banner_markup(
        "in-review",
        presets=PROJECT_BANNER_PRESETS,
        default_version=DEFAULT_PROJECT_VERSION,
    )
    assert "v0.1.0" not in html
    assert "In Review" in html
