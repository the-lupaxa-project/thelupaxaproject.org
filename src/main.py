"""MkDocs macros for catalogue pages.

Loads YAML catalogue data and exposes Jinja macros that emit the same
HTML/Markdown structure previously hand-authored in the page files.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Repo root (data/, mkdocs/); this file lives in src/
ROOT = Path(__file__).resolve().parent.parent
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from banner_lib import (
    DEFAULT_BANNER_EXPIRY_DAYS,
    DEFAULT_PROJECT_VERSION,
    POLICY_BANNER_PRESETS,
    PROJECT_BANNER_PRESETS,
    format_publish_date_attr,
    normalise_project_version,
    parse_iso_date,
)
from banner_lib import (
    banner_markup as _shared_banner_markup,
)
from banner_lib import (
    resolve_banner as _shared_resolve_banner,
)
from humour_lib import (
    collect_tags as collect_humour_tags,
)
from humour_lib import (
    is_remote_media,
    load_humour_data,
    published_entries,
    validate_humour,
)

DATA_DIR = ROOT / "data"

# Shared brand mark for policy cards (same visual slot as project/org logos).
DEFAULT_POLICY_LOGO = "assets/images/organisations/organisation-the-lupaxa-project-logo.png"
DEFAULT_POLICY_LOGO_ALT = "The Lupaxa Project"


def catalogue_media_src(path: str) -> str:
    """Return an img src that resolves from any site page, not only ``/``.

    Catalogue cards emit raw HTML, so MkDocs does not rewrite these paths.
    Site-root paths (``/assets/...``) stay valid on ``/projects/`` and friends.
    Remote URLs are left unchanged.
    """
    value = (path or "").strip()
    if not value or value.startswith(("http://", "https://", "/")):
        return value
    return f"/{value}"


# Material filter-variant / filter-off icons for Show / Hide Filters.
FILTER_EXPAND_ICONS = """\
<span class="filter-panel-expand__icon filter-panel-expand__icon--show" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" focusable="false">
                <path d="M6 13h12v-2H6m-3-5v2h18V6M10 18h4v-2h-4v2Z"/>
            </svg>
        </span>
        <span class="filter-panel-expand__icon filter-panel-expand__icon--hide" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" focusable="false">
                <path d="M14.76 20.83 17.6 18l-2.84-2.83 1.41-1.41L19 16.57l2.83-2.81 1.41 1.41L20.41 18l2.83 2.83-1.41 1.41L19 19.41l-2.83 2.83-1.41-1.41M6 13h7.07c.14-.71.4-1.38.76-2H6m-3-5v2h18V6H3Z"/>
            </svg>
        </span>"""


def filter_panel_toolbar(*, prefix: str, summary_text: str) -> str:
    """Shared Show/Hide Filters button + live summary row for catalogues."""
    return f"""
    <div class="filter-panel-toolbar">
        <button
            type="button"
            class="md-button lupaxa-button filter-panel-expand"
            data-filter-expand
            aria-expanded="false"
        >
            {FILTER_EXPAND_ICONS}
            <span class="filter-panel-expand__label">Show Filters</span>
        </button>
        <div
            class="filter-panel-summary"
            aria-live="polite"
            data-{prefix}-summary
        >
            {summary_text}
        </div>
    </div>"""


def _load_yaml(name: str) -> list[dict]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if not isinstance(data, list):
        raise TypeError(f"{path} must contain a YAML list")
    return data


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(
        f"{prefix}{line}" if line else prefix.rstrip() for line in text.strip().splitlines()
    )


def _normalise_catalogue_value(value: str) -> str:
    return " ".join(value.casefold().split())


def _categories_markup(categories: list[str]) -> str:
    return "\n".join(
        f'    <button type="button" class="catalogue-category">{category}</button>'
        for category in sorted(categories, key=str.casefold)
    )


def _organisation_logo_title(name: str) -> str:
    if name.startswith("The "):
        return f"View projects in {name}"
    return f"View projects in the {name}"


def catalogue_card_heading(item: dict) -> str:
    """Card title as a heading so site search can deep-link to the card."""
    return f"-   ### :{item['icon']}: {item['name']} {{ #{item['id']} .no_toc translate=no }}"


def _action_link(modifier: str, href: str, label: str, icon: str) -> str:
    return (
        f"    <a\n"
        f'        class="catalogue-action catalogue-action--{modifier}"\n'
        f'        href="{href}"\n'
        f'        target="_blank"\n'
        f'        rel="noopener noreferrer">\n'
        f'        <span class="md-icon">:{icon}:</span>\n'
        f"        {label}\n"
        f"    </a>"
    )


def _resolve_banner(raw: Any) -> tuple[str, str, str] | None:
    """Return (label, tone, filter_key) for a project banner, or None."""
    return _shared_resolve_banner(raw)


def _banner_markup(raw: Any) -> str:
    return _shared_banner_markup(raw)


def sort_catalogue_by_name(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return catalogue items in A–Z name order. YAML file order is ignored."""

    return sorted(items, key=lambda item: str(item.get("name") or "").casefold())


def _published_site_url() -> str:
    """Return the public site address from mkdocs.yml.

    `mkdocs serve` replaces the live site address with the dev server, so
    page.canonical_url would print http://127.0.0.1:8000/.
    """

    text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    match = re.search(r"(?m)^site_url:\s*(\S+)\s*$", text)
    if match is None:
        raise RuntimeError("site_url is missing from mkdocs.yml")
    return str(match.group(1)).rstrip("/") + "/"


def define_env(env):
    site_url = _published_site_url()

    @env.macro
    def online_page_url() -> str:
        path = str(getattr(env.page, "url", "") or "").lstrip("/")
        return f"{site_url}{path}"

    def _published(items: list[dict]) -> list[dict]:
        return [item for item in items if item.get("published", True)]

    organisations = sort_catalogue_by_name(_published(_load_yaml("organisations.yml")))
    projects = sort_catalogue_by_name(_published(_load_yaml("projects.yml")))
    policies = sort_catalogue_by_name(_published(_load_yaml("policies.yml")))

    env.variables["catalogue_organisations"] = organisations
    env.variables["catalogue_projects"] = projects
    env.variables["catalogue_policies"] = policies

    @env.macro
    def filter_panel(
        prefix: str,
        *,
        compact: bool = False,
        search_label: str,
        search_placeholder: str,
        summary_text: str,
        include_organisation: bool = False,
        include_status: bool = False,
        include_sort: bool = False,
        status_kind: str = "project",
        category_label: str = "Category",
        organisation_label: str = "Organisation",
        status_label: str = "Status",
        clear_label: str = "Clear filters",
    ) -> str:
        classes = ["filter-panel"]
        if compact:
            classes.append("filter-panel--compact")
        if include_sort:
            classes.append("filter-panel--with-sort")
        class_attr = " ".join(classes)
        organisation_block = ""
        if include_organisation:
            # Fixed list from organisations.yml (not derived from project cards).
            org_options = "\n".join(
                f'            <option value="{html.escape(_normalise_catalogue_value(org["name"]), quote=True)}">'
                f"{html.escape(org['name'])}</option>"
                for org in organisations
            )
            organisation_block = f"""
    <div class="filter-panel-select">
        <label for="{prefix}-organisation">{organisation_label}</label>
        <select id="{prefix}-organisation" data-{prefix}-organisation>
            <option value="">All Organisations</option>
{org_options}
        </select>
    </div>"""
        status_block = ""
        if include_status:
            # Fixed lifecycle list (not derived from cards on the page).
            if status_kind == "project":
                presets = PROJECT_BANNER_PRESETS
            elif status_kind == "policy":
                presets = POLICY_BANNER_PRESETS
            else:
                raise ValueError(f"Unrecognised status_kind: {status_kind!r}")

            if status_kind == "policy":
                # Segmented All | New | Updated (same pattern as articles).
                toggle_buttons = [
                    ("all", "All"),
                    ("new", "New"),
                    ("updated", "Updated"),
                ]
                options_markup = "\n".join(
                    f"""            <button
                type="button"
                class="filter-panel-toggle__option"
                data-{prefix}-status="{html.escape(slug, quote=True)}"
                aria-pressed="{"true" if slug == "all" else "false"}"
            >
                {html.escape(label)}
            </button>"""
                    for slug, label in toggle_buttons
                )
                status_block = f"""
    <div class="filter-panel-toggle" role="group" aria-labelledby="{prefix}-status-label">
        <label id="{prefix}-status-label">{status_label}</label>
        <div class="filter-panel-toggle__options">
{options_markup}
        </div>
    </div>"""
            else:
                status_options = "\n".join(
                    f'            <option value="{html.escape(slug, quote=True)}">'
                    f"{html.escape(label)}</option>"
                    for slug, (label, _) in presets.items()
                )
                status_block = f"""
    <div class="filter-panel-select">
        <label for="{prefix}-status">{status_label}</label>
        <select id="{prefix}-status" data-{prefix}-status>
            <option value="">All Statuses</option>
{status_options}
        </select>
    </div>"""

        sort_block = ""
        if include_sort:
            sort_block = f"""
    <div class="filter-panel-toggle" role="group" aria-labelledby="{prefix}-sort-label">
        <label id="{prefix}-sort-label">Sort</label>
        <div class="filter-panel-toggle__options">
            <button
                type="button"
                class="filter-panel-toggle__option"
                data-{prefix}-sort="alpha"
                aria-pressed="true"
            >
                A–Z
            </button>
            <button
                type="button"
                class="filter-panel-toggle__option"
                data-{prefix}-sort="newest"
                aria-pressed="false"
            >
                Newest
            </button>
        </div>
    </div>"""

        toolbar = filter_panel_toolbar(prefix=prefix, summary_text=summary_text)
        return f"""
<div class="{class_attr}" data-{prefix}-filters>
{toolbar}
    <div class="filter-panel-search">
        <label for="{prefix}-search">{search_label}</label>
        <input
            id="{prefix}-search"
            type="search"
            placeholder="{search_placeholder}"
            autocomplete="off"
            data-{prefix}-search
        />
    </div>{organisation_block}
    <div class="filter-panel-select">
        <label for="{prefix}-category">{category_label}</label>
        <select id="{prefix}-category" data-{prefix}-category>
            <option value="">All Categories</option>
        </select>
    </div>{status_block}{sort_block}
    <div class="filter-panel-actions">
        <button
            type="button"
            class="md-button lupaxa-button filter-panel-clear"
            data-{prefix}-clear
        >
            {clear_label}
        </button>
    </div>
</div>
""".strip()

    @env.macro
    def catalogue_empty(prefix: str, heading: str, hint: str) -> str:
        return f"""
<div class="catalogue-empty-state" data-{prefix}-empty hidden markdown>

:material-filter-off:{{ .lg }}

**{heading}**

{hint}

</div>
""".strip()

    def organisation_card(item: dict) -> str:
        categories = _categories_markup(item["categories"])
        description = _indent(item["description"])
        title = _organisation_logo_title(item["name"])
        publish_date_value = format_publish_date_attr(item.get("publish_date"))
        publish_date_attr = (
            f'\n        data-publish-date="{publish_date_value}"'
            if publish_date_value is not None
            else ""
        )
        name_attr = html.escape(item["name"], quote=True)
        action = _action_link(
            "repository",
            item["repository"],
            "View on GitHub",
            "material-github",
        )
        return f"""
{catalogue_card_heading(item)}

    ---

    <img
        class="catalogue-logo"
        translate="no"
        title="{title}"
        data-name="{name_attr}"
        data-organisation="{item["name"]}"{publish_date_attr}
        src="{html.escape(catalogue_media_src(item["logo"]), quote=True)}"
        alt="{item.get("logo_alt", item["name"])}"
    />

{description}

{categories}

    ---

{action}
""".strip()

    def project_card(item: dict, *, expiry_days: int = DEFAULT_BANNER_EXPIRY_DAYS) -> str:
        categories = _categories_markup(item["categories"])
        description = _indent(item["description"])
        raw_banner = item.get("banner")
        if (
            raw_banner is None
            or raw_banner is False
            or (isinstance(raw_banner, str) and not raw_banner.strip())
        ):
            raw_banner = "in-development"
        raw_version = item.get("version")
        has_version = normalise_project_version(raw_version) is not None
        banner = _shared_banner_markup(
            raw_banner,
            presets=PROJECT_BANNER_PRESETS,
            event_date=parse_iso_date(item.get("released_date")),
            expiry_days=expiry_days,
            time_limited_statuses=frozenset({"released"}),
            version=raw_version,
            default_version=DEFAULT_PROJECT_VERSION if has_version else None,
            stable_after_expiry=has_version,
        )
        banner_block = f"{banner}\n\n" if banner else ""
        actions = [
            _action_link(
                "repository",
                item["repository"],
                "View on GitHub",
                "material-github",
            )
        ]
        documentation = item.get("documentation")
        if documentation:
            custom_label = str(item.get("documentation_label") or "").strip()
            label = custom_label or "Documentation"
            icon = "material-web" if custom_label else "material-book-open-page-variant"
            actions.append(
                _action_link(
                    "documentation",
                    documentation,
                    html.escape(label),
                    icon,
                )
            )
        actions_markup = "\n".join(actions)
        publish_date_value = format_publish_date_attr(item.get("publish_date"))
        publish_date_attr = (
            f'\n        data-publish-date="{publish_date_value}"'
            if publish_date_value is not None
            else ""
        )
        released_date_value = format_publish_date_attr(item.get("released_date"))
        released_date_attr = (
            f'\n        data-released-date="{released_date_value}"'
            if released_date_value is not None
            else ""
        )
        name_attr = html.escape(item["name"], quote=True)
        return f"""
{catalogue_card_heading(item)}

    ---

{banner_block}    <img
        class="catalogue-logo"
        translate="no"
        title="{item["organisation"]}"
        data-name="{name_attr}"
        data-organisation="{item["organisation"]}"{publish_date_attr}{released_date_attr}
        src="{html.escape(catalogue_media_src(item["logo"]), quote=True)}"
        alt="{item.get("logo_alt", item["organisation"])}"
    />

{description}

{categories}

    ---

{actions_markup}
""".strip()

    def policy_card(item: dict, *, expiry_days: int = DEFAULT_BANNER_EXPIRY_DAYS) -> str:
        categories = _categories_markup(item["categories"])
        description = _indent(item["description"])
        raw_banner = item.get("banner")
        resolved = _shared_resolve_banner(raw_banner, presets=POLICY_BANNER_PRESETS)
        event_date = None
        if resolved:
            filter_key = resolved[2]
            date_field = "updated_date" if filter_key == "updated" else "publish_date"
            event_date = parse_iso_date(item.get(date_field))
        banner = _shared_banner_markup(
            raw_banner,
            presets=POLICY_BANNER_PRESETS,
            event_date=event_date,
            expiry_days=expiry_days,
            time_limited_statuses=frozenset({"new", "updated"}),
        )
        banner_block = f"{banner}\n\n" if banner else ""
        logo = html.escape(catalogue_media_src(item.get("logo", DEFAULT_POLICY_LOGO)), quote=True)
        logo_alt = html.escape(item.get("logo_alt", DEFAULT_POLICY_LOGO_ALT), quote=True)
        name_attr = html.escape(item["name"], quote=True)
        action = _action_link(
            "repository",
            item["document"],
            "View on GitHub",
            "material-github",
        )
        return f"""
{catalogue_card_heading(item)}

    ---

{banner_block}    <span class="catalogue-logo-wrap">
    <img
        class="catalogue-logo"
        translate="no"
        title="{logo_alt}"
        data-name="{name_attr}"
        src="{logo}"
        alt="{logo_alt}"
    />
    </span>

{description}

{categories}

    ---

{action}
""".strip()

    @env.macro
    def catalogue_grid(
        prefix: str,
        kind: str,
        banner_expiry_days: int = DEFAULT_BANNER_EXPIRY_DAYS,
    ) -> str:
        if kind == "organisation":
            cards = "\n\n".join(
                organisation_card(item) for item in sort_catalogue_by_name(organisations)
            )
        elif kind == "project":
            cards = "\n\n".join(
                project_card(item, expiry_days=banner_expiry_days)
                for item in sort_catalogue_by_name(projects)
                if not item.get("website")
            )
        elif kind == "website":
            cards = "\n\n".join(
                project_card(item, expiry_days=banner_expiry_days)
                for item in sort_catalogue_by_name(projects)
                if item.get("website") is True
            )
        elif kind == "policy":
            cards = "\n\n".join(
                policy_card(item, expiry_days=banner_expiry_days)
                for item in sort_catalogue_by_name(policies)
            )
        else:
            raise ValueError(f"Unknown catalogue kind: {kind}")

        return f"""
<div class="grid cards catalogue-grid" data-{prefix}-catalogue markdown>

{cards}

</div>
""".strip()

    humour_path = Path(env.project_dir) / "data" / "humour.yml"

    def validated_humour():
        data = load_humour_data(humour_path)
        validate_humour(data)
        return data

    @env.macro
    def humour_data():
        return validated_humour()

    @env.macro
    def wall_humour_entries():
        return published_entries(validated_humour())

    @env.macro
    def humour_wall_tags():
        return collect_humour_tags(published_entries(validated_humour()))

    @env.macro
    def humour_media_is_remote(path: str) -> bool:
        return is_remote_media(path)
