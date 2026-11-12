from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = (ROOT / "overrides/partials/header.html").read_text(encoding="utf-8")
MKDOCS = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
NAV_CSS = (ROOT / "mkdocs/assets/stylesheets/30-navigation.css").read_text(encoding="utf-8")
FOOTER = (ROOT / "overrides/partials/copyright.html").read_text(encoding="utf-8")


def test_header_has_custom_picker_not_alternate():
    assert 'id="lupaxa-lang"' in HEADER
    assert "partials/alternate.html" not in HEADER
    assert "extra.alternate" not in HEADER
    assert 'translate="no"' in HEADER
    assert 'value="en">English<' in HEADER
    assert 'value="fr">Français<' in HEADER
    assert 'value="de">Deutsch<' in HEADER
    assert 'value="es">Español<' in HEADER
    assert 'value="pt">Português<' in HEADER
    assert 'value="it">Italiano<' in HEADER
    assert 'value="nl">Nederlands<' in HEADER
    assert 'value="pl">Polski<' in HEADER
    assert 'value="bg">Български<' in HEADER
    assert 'value="cs">Čeština<' in HEADER
    assert 'value="da">Dansk<' in HEADER
    assert 'value="el">Ελληνικά<' in HEADER
    assert 'value="fi">Suomi<' in HEADER
    assert 'value="hr">Hrvatski<' in HEADER
    assert 'value="hu">Magyar<' in HEADER
    assert 'value="lt">Lietuvių<' in HEADER
    assert 'value="no">Norsk<' in HEADER
    assert 'value="ro">Română<' in HEADER
    assert 'value="sv">Svenska<' in HEADER
    assert 'value="tr">Türkçe<' in HEADER
    assert 'value="uk">Українська<' in HEADER
    assert 'value="ng"' not in HEADER
    assert 'value="eo"' not in HEADER
    assert 'value="la"' not in HEADER
    assert 'value="ja"' not in HEADER
    assert 'value="tlh"' not in HEADER
    assert "lupaxa-lang-picker__label" not in HEADER
    assert ">EN<" not in HEADER
    assert 'id="lupaxa-lang-fallback"' in HEADER
    assert 'class="lupaxa-lang-fallback notranslate"' in HEADER


def test_language_script_follows_page_lifecycle():
    scripts = [
        line.strip()
        for line in MKDOCS.splitlines()
        if line.strip().startswith("- assets/javascript/")
    ]
    assert "- assets/javascript/page-lifecycle.js" in scripts
    assert "- assets/javascript/language-preference.js" in scripts
    assert scripts.index("- assets/javascript/page-lifecycle.js") < scripts.index(
        "- assets/javascript/language-preference.js"
    )
    assert "extra.alternate" not in MKDOCS
    assert "mkdocs-static-i18n" not in MKDOCS
    assert "  language: en" in MKDOCS
    assert "social_locale: en_GB" in MKDOCS
    assert "language_picker: true" in MKDOCS
    assert "{% if config.extra.language_picker %}" in HEADER


def test_header_css_keeps_picker_out_of_nav_flex():
    assert ".lupaxa-lang-picker" in NAV_CSS
    assert ".lupaxa-lang-fallback" in NAV_CSS
    assert "max-width: 90rem" not in NAV_CSS
    assert "flex: 0 0 auto" in NAV_CSS


import main
from banner_lib import banner_markup_from_resolved


class _FakeEnv:
    def __init__(self, project_dir):
        self.project_dir = str(project_dir)
        self.variables = {}
        self.macros = {}

    def macro(self, func):
        self.macros[func.__name__] = func
        return func


def test_catalogue_heading_and_logo_opt_out_of_translate():
    heading = main.catalogue_card_heading(
        {"icon": "material-source-repository", "name": "Synthetic", "id": "synthetic"}
    )
    assert "translate=no" in heading
    env = _FakeEnv(ROOT)
    main.define_env(env)
    source = (ROOT / "src/main.py").read_text(encoding="utf-8")
    assert source.count('translate="no"') >= 3


def test_banner_version_opts_out_of_translate():
    markup = banner_markup_from_resolved(
        "Released",
        "green",
        "released",
        version="1.2.3",
        release_date="11 Nov 2026",
    )
    assert 'class="catalogue-banner__version"' in markup
    assert 'class="catalogue-banner__date"' in markup
    assert '<span translate="no">v1.2.3</span>' in markup
    assert '<span translate="no">11 Nov 2026</span>' in markup
    assert "Version:" in markup
    assert "Released:" in markup


def test_portal_header_has_no_repository_link():
    assert "repo_url:" not in MKDOCS
    assert "partials/source.html" not in HEADER
    assert "lupaxa-header__tools" in HEADER
    assert "lupaxa-lang-picker" in HEADER
    assert ".md-header__source" in NAV_CSS
    assert "display: none !important" in NAV_CSS
    assert 'class="md-copyright notranslate" translate="no"' in FOOTER


def test_footer_hero_sponsor_opt_out_brand_names():
    footer = FOOTER
    index = (ROOT / "mkdocs/index.md").read_text(encoding="utf-8")
    sponsor = (ROOT / "mkdocs/sponsor.md").read_text(encoding="utf-8")
    assert 'class="md-copyright notranslate" translate="no"' in footer
    assert 'class="lupaxa-hero-title"' in index
    assert 'translate="no"' in index
    assert '<strong translate="no">The Lupaxa Project</strong>' in index
    assert '<strong translate="no">The Lupaxa Project</strong>' in sponsor
