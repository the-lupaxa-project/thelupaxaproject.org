"""Shared catalogue status banners and expiry helpers."""

from __future__ import annotations

import html
from datetime import UTC, date, datetime
from typing import Any

PROJECT_BANNER_PRESETS: dict[str, tuple[str, str]] = {
    "in-development": ("In Development", "red"),
    "in-testing": ("In Testing", "magenta"),
    "in-review": ("In Review", "purple"),
    "released": ("Released", "dark-blue"),
    "stable": ("Stable", "blue"),
}
ARTICLE_BANNER_PRESETS: dict[str, tuple[str, str]] = {
    "new": ("New Article", "blue"),
}
POLICY_BANNER_PRESETS: dict[str, tuple[str, str]] = {
    "new": ("New Policy", "blue"),
    "updated": ("Updated Policy", "purple"),
}
# Deliberately not merged into BANNER_PRESETS — the "new" slug clashes with
# ARTICLE_BANNER_PRESETS, and policy resolve/markup calls always pass
# presets=POLICY_BANNER_PRESETS explicitly so labels never leak across kinds.
BANNER_PRESETS: dict[str, tuple[str, str]] = {
    **PROJECT_BANNER_PRESETS,
    **ARTICLE_BANNER_PRESETS,
}
BANNER_TONES = frozenset(
    {
        "red",
        "green",
        "purple",
        "blue",
        "dark-blue",
        "orange",
        "neutral",
        "silver",
        "magenta",
    }
)
DEFAULT_BANNER_EXPIRY_DAYS = 28
# SemVer pre-1.0 default. Quote ``version`` in YAML (``"0.1.0"``) so it stays a string.
DEFAULT_PROJECT_VERSION = "0.1.0"


def normalise_project_version(value: Any) -> str | None:
    """Return a version string without a leading ``v``, or ``None``."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        text = str(value)
    elif isinstance(value, float):
        text = str(int(value)) if value.is_integer() else str(value)
    else:
        text = str(value).strip()
    if not text:
        return None
    if text[:1] in {"v", "V"} and len(text) > 1 and text[1].isdigit():
        text = text[1:]
    return text or None


def resolve_project_version(value: Any, *, default: str = DEFAULT_PROJECT_VERSION) -> str:
    """Return a display version, defaulting to ``0.1.0`` when unset."""

    return normalise_project_version(value) or default


def parse_iso_datetime(value: Any) -> datetime | None:
    """Parse an ISO calendar date or date-time into a ``datetime``.

    Date-only values (``YYYY-MM-DD``) become midnight on that day. Strings may
    use ``T`` or a space between date and time. Banner expiry still uses the
    calendar date via :func:`parse_iso_date`; newest-project sorting uses the
    full timestamp.
    """

    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace(" ", "T", 1)
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def parse_iso_date(value: Any) -> date | None:
    """Parse an ISO date or date-time and return the calendar date."""

    parsed = parse_iso_datetime(value)
    return parsed.date() if parsed is not None else None


def format_publish_date_attr(value: Any) -> str | None:
    """Format ``data-publish-date`` for catalogue cards.

    Date-only inputs stay ``YYYY-MM-DD``. Values with a time use UTC
    ``YYYY-MM-DDTHH:MM:SS`` so client-side newest sort can break same-day ties.
    """

    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is not None:
            dt = dt.astimezone(UTC).replace(tzinfo=None)
        return dt.replace(microsecond=0).isoformat(sep="T")
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    parsed = parse_iso_datetime(text)
    if parsed is None:
        return None
    normalised = text.replace(" ", "T", 1)
    if "T" in normalised and len(text) > 10:
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(UTC).replace(tzinfo=None)
        return parsed.replace(microsecond=0).isoformat(sep="T")
    return parsed.date().isoformat()


def banner_still_active(
    event_date: date | None,
    *,
    today: date,
    expiry_days: int,
) -> bool:
    if event_date is None:
        return False
    delta = (today - event_date).days
    if delta < 0:
        return True
    return delta <= expiry_days


def _banner_filter_key(status: str | None, label: str) -> str:
    if status:
        return status
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in label)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def resolve_banner(
    raw: Any,
    *,
    presets: dict[str, tuple[str, str]] | None = None,
) -> tuple[str, str, str] | None:
    presets = presets if presets is not None else BANNER_PRESETS
    if raw is None or raw is False:
        return None
    status: str | None = None
    label: str | None = None
    tone: str | None = None
    if isinstance(raw, str):
        status = raw.strip() or None
    elif isinstance(raw, dict):
        status_val = raw.get("status")
        if isinstance(status_val, str) and status_val.strip():
            status = status_val.strip()
        label_val = raw.get("label")
        if isinstance(label_val, str) and label_val.strip():
            label = label_val.strip()
        tone_val = raw.get("tone")
        if isinstance(tone_val, str) and tone_val.strip():
            tone = tone_val.strip()
    else:
        return None
    preset = presets.get(status) if status else None
    if label is None and preset:
        label = preset[0]
    if tone is None and preset:
        tone = preset[1]
    if tone is None or tone not in BANNER_TONES:
        tone = "neutral"
    if not label:
        return None
    # Unknown bare string with no preset and no explicit label → None
    if isinstance(raw, str) and preset is None:
        return None
    return label, tone, _banner_filter_key(status, label)


def banner_markup_from_resolved(
    label: str,
    tone: str,
    filter_key: str,
    *,
    version: str | None = None,
) -> str:
    safe_label = html.escape(label, quote=True)
    safe_key = html.escape(filter_key, quote=True)
    version_class = ""
    version_html = ""
    aria_label = f"Status: {safe_label}"
    if version:
        safe_version = html.escape(f"v{version}", quote=True)
        version_class = " catalogue-banner--with-version"
        version_html = (
            f'<span class="catalogue-banner__version" translate="no">{safe_version}</span>'
        )
        aria_label = f"Status: {safe_label} {safe_version}"
    return (
        f'    <span class="catalogue-banner catalogue-banner--{tone}'
        f'{version_class}" '
        f'data-banner-status="{safe_key}" '
        f'data-banner-label="{safe_label}" '
        f'aria-label="{aria_label}" '
        f'role="button" tabindex="0">'
        f'<span class="catalogue-banner__band" aria-hidden="true">'
        f'<span class="catalogue-banner__text">{safe_label}{version_html}</span>'
        f"</span></span>"
    )


def banner_markup(
    raw: Any,
    *,
    presets: dict[str, tuple[str, str]] | None = None,
    event_date: date | None = None,
    today: date | None = None,
    expiry_days: int | None = None,
    time_limited_statuses: frozenset[str] = frozenset({"released", "new"}),
    version: Any = None,
    default_version: str | None = None,
    stable_after_expiry: bool = False,
) -> str:
    resolved = resolve_banner(raw, presets=presets)
    if not resolved:
        return ""
    label, tone, filter_key = resolved
    if filter_key in time_limited_statuses:
        days = DEFAULT_BANNER_EXPIRY_DAYS if expiry_days is None else expiry_days
        day = today or date.today()
        if not banner_still_active(event_date, today=day, expiry_days=days):
            if stable_after_expiry and default_version is not None and filter_key == "released":
                return banner_markup_from_resolved(
                    "Stable",
                    "blue",
                    "stable",
                    version=resolve_project_version(version, default=default_version),
                )
            return ""
    version_text = None
    if default_version is not None:
        version_text = resolve_project_version(version, default=default_version)
    return banner_markup_from_resolved(label, tone, filter_key, version=version_text)
