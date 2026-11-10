<p align="center">
    <a href="https://github.com/the-lupaxa-project">
        <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/the-lupaxa-project/readme-logo.png" alt="Organisation Logo" />
    </a>
</p>

<h1 align="center">The Lupaxa Project portal</h1>

Central MkDocs Material site for organisations, projects, and policies across
The Lupaxa Project ecosystem.

Published at <https://thelupaxaproject.org/>.

## Prerequisites

- Python 3.13+
- Node.js 22+ (only required for markdownlint)
- `yamllint` (optional; `python -m pip install yamllint`)

## Local development

```bash
make init
make install-dev
make mkdocs-serve
```

Or without Make:

```bash
python -m pip install -r requirements.txt
python -m mkdocs serve
```

Open the local URL MkDocs prints (typically port `8000` on `127.0.0.1`).

`mkdocs.yml` watches `data/`, `hooks/`, `src/`, and
`mkdocs/assets/stylesheets/`, so catalogue YAML, macro, and CSS edits
reload automatically while `mkdocs serve` is running. Add new build
scripts to `watch` when you create them — MkDocs does not support globs
there.

Strict production build:

```bash
python -m mkdocs build --strict
```

Markdown lint:

```bash
npx markdownlint-cli "mkdocs/**/*.md" --config .markdownlint.yml
```

YAML lint:

```bash
yamllint -c .yamllint.yml .github data mkdocs.yml .markdownlint.yml .yamllint.yml
```

## Catalogue content

Catalogue entries live in YAML under `data/`:

| File | Page |
| --- | --- |
| `data/organisations.yml` | Organisations |
| `data/humour.yml` | Humour masonry wall (`page.show_count: all` or a number; `page.show_media_filters: true` for images/videos filters) |
| `data/projects.yml` | Projects, and Websites when `website: true` |
| `data/policies.yml` | Policies |

`publish_date` and `released_date` accept either a calendar day (`YYYY-MM-DD`) or a
UTC timestamp (`YYYY-MM-DDTHH:MM:SS`). Banner expiry still uses the calendar day.
Catalogue “newest” sorts use `released_date` when it is set, otherwise
`publish_date`, including the time so same-day stamps stay in order.

Quote `version` as a string (`"0.1.0"`) when the project has tagged releases.
HEAD-only catalogues (no GitHub Release tags) omit `version` and use
`banner: stable` so the sash is **Stable** with no SemVer. Set
`released_date` from the latest commit on `master` (not a tag) so Newest
sorts the card when the catalogue itself moves. That stamp does not change
the Stable sash.
If `banner` is omitted, the card is **In Development**.
`documentation` is the docs or site URL. The link reads **Documentation** with
a book icon unless `documentation_label` is set. Product sites use
`documentation_label: Visit Site`, which also switches the icon to a globe.
Set `website: true` to list that card on Websites instead of Projects.
`banner: released` still expires 28 days after `released_date`. On versioned
cards the Released sash is dark navy; after expiry the card keeps a lighter
Lupaxa-blue **Stable** sash with the version on the projects catalogue.

Catalogue pages (organisations, projects, websites, policies, articles) always render A–Z
by name/title. YAML or filename order is never used. Newest is an explicit sort,
not the default.

`src/main.py` (via a thin root `main.py` shim) loads that data for `mkdocs-macros-plugin`. Pages call macros such as
`filter_panel` and `catalogue_grid` so card markup stays
in one place.

MkDocs brand logos are local copies under `mkdocs/assets/images/brand/`.

## Layout overview

```text
data/                     Catalogue YAML
src/*.py                  Portal macros and helpers
main.py                   Thin mkdocs-macros shim → src/main.py
mkdocs/                   Page Markdown and static assets
overrides/                Material theme overrides
requirements.txt          Pinned MkDocs dependencies
.github/workflows/        Publish + PR validate
```

CSS is numbered by cascade layer under `mkdocs/assets/stylesheets/`.
JavaScript is split under `mkdocs/assets/javascript/`:

- `page-lifecycle.js` — load + Material instant navigation helpers (`onPageRender`)
- `language-preference.js` — viewer language picker (`extra.language_picker`)
- `header-active-nav.js` — header active state
- `catalogue-filters.js` — catalogue search / filter / URL sync
- `masonry-wall.js` — shared masonry layout and text filters
- `humour.js` — humour wall + lightbox (uses masonry-wall)

The header can include a viewer language picker (`language-preference.js`)
when `extra.language_picker` is `true`. English stays the source language
and the URL does not change. Desktop Chromium translates the page on-device;
the first choice of a language may download a language pack (the banner
shows progress). Other browsers and phones use the same picker and cache
with an in-page network fallback. Later visits reuse Chrome’s pack (when
present) and a per-locale string cache in `localStorage`
(`lupaxa-lang-strings`). The footer and brand names stay English
(`translate="no"` / `.notranslate`).

## Page social metadata

Site-wide defaults are set in `mkdocs.yml` under `extra`:

```yaml
extra:
  generator: false
  social_image: https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/social-media/social-card.png
  social_image_width: 1200
  social_image_height: 630
  social_logo: >-
    https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/the-lupaxa-project/readme-logo.png
  social_locale: en_GB
  theme_color: "#203959"
  twitter_card: summary_large_image
```

Optional per-page overrides in front matter:

```yaml
---
description: Short page description for search and social cards.
social_title: Custom social title
social_image: https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/social-media/social-card.png
---
```

`overrides/main.html` omits image meta tags when no social image path is set.

## Publishing

Push to `master` or the nightly schedule (about 02:18 UTC) triggers
`.github/workflows/publish-mkdocs.yml`, which calls the org reusable MkDocs
publisher. That rebuild picks up banner expiry (Released to Stable, policy
New/Updated dropping) without a YAML edit. The workflow installs from
`requirements.txt` when the file is present.

Pull requests run `.github/workflows/validate-mkdocs.yml`, which calls the org
reusable MkDocs site validator (`mkdocs build --strict` + optional markdownlint).

> Note: both the reusable publisher (conditional `requirements.txt`) and the
> reusable validator must be merged in `the-lupaxa-project/workflows` before
> GitHub Actions can use them from `@master`.

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
