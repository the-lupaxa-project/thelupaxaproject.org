from datetime import date, datetime

from banner_lib import (
    banner_markup,
    banner_still_active,
    format_publish_date_attr,
    parse_iso_date,
    parse_iso_datetime,
)


def test_parse_iso_date():
    assert parse_iso_date("2026-07-01") == date(2026, 7, 1)
    assert parse_iso_date("2026-07-01T17:30:00") == date(2026, 7, 1)
    assert parse_iso_date("2026-07-01 17:30:00") == date(2026, 7, 1)
    assert parse_iso_date(None) is None
    assert parse_iso_date("nope") is None


def test_parse_iso_datetime():
    assert parse_iso_datetime("2026-07-01") == datetime(2026, 7, 1, 0, 0, 0)
    assert parse_iso_datetime("2026-07-01T17:30:00") == datetime(2026, 7, 1, 17, 30, 0)
    assert parse_iso_datetime("2026-07-01 17:30:00") == datetime(2026, 7, 1, 17, 30, 0)
    assert parse_iso_datetime(None) is None
    assert parse_iso_datetime("nope") is None


def test_format_publish_date_attr():
    assert format_publish_date_attr("2026-07-01") == "2026-07-01"
    assert format_publish_date_attr("2026-07-01T17:30:00") == "2026-07-01T17:30:00"
    assert format_publish_date_attr("2026-07-01 17:30:00") == "2026-07-01T17:30:00"
    assert format_publish_date_attr(None) is None
    assert format_publish_date_attr("nope") is None


def test_banner_still_active_window():
    today = date(2026, 7, 31)
    assert banner_still_active(date(2026, 7, 31), today=today, expiry_days=28) is True
    assert banner_still_active(date(2026, 7, 3), today=today, expiry_days=28) is True
    assert banner_still_active(date(2026, 7, 2), today=today, expiry_days=28) is False
    assert banner_still_active(date(2026, 8, 5), today=today, expiry_days=28) is True  # future
    assert banner_still_active(None, today=today, expiry_days=28) is False


def test_released_markup_stays_after_the_old_window():
    html = banner_markup(
        "released",
        event_date=date(2020, 1, 1),
        today=date(2026, 7, 31),
        version="1.2.0",
    )
    assert "Released" in html
    assert "Stable" not in html
    assert "v1.2.0" in html
    assert "1 Jan 2020" in html
    assert 'data-banner-status="released"' in html
    assert "catalogue-banner--blue" in html


def test_released_markup_shown_when_fresh():
    html = banner_markup(
        "released",
        event_date=date(2026, 7, 20),
        today=date(2026, 7, 31),
        version="0.1.0",
    )
    assert "catalogue-banner--blue" in html
    assert "catalogue-banner--dark-blue" not in html
    assert "Released" in html
    assert "v0.1.0" in html
    assert "20 Jul 2026" in html
    assert "Stable" not in html


def test_new_article_markup():
    html = banner_markup(
        "new",
        presets={"new": ("New Article", "blue")},
        event_date=date(2026, 7, 20),
        today=date(2026, 7, 31),
        expiry_days=28,
        time_limited_statuses=frozenset({"new"}),
    )
    assert "New Article" in html
    assert 'data-banner-status="new"' in html
