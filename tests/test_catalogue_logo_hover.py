from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = (ROOT / "overrides/main.html").read_text(encoding="utf-8")
CATALOGUE = (ROOT / "mkdocs/assets/stylesheets/40-components/catalogue.css").read_text(encoding="utf-8")
TOKENS = (ROOT / "mkdocs/assets/stylesheets/00-tokens.css").read_text(encoding="utf-8")


def test_layout_defines_alpha_logo_frame_filter():
    assert 'id="lupaxa-logo-frame"' in MAIN
    assert 'operator="dilate"' in MAIN
    assert "feMorphology" in MAIN


def test_card_logo_hover_follows_image_alpha():
    assert 'filter: url("#lupaxa-logo-frame")' in CATALOGUE
    assert "filter: brightness(1.08)" not in CATALOGUE
    assert "--lupaxa-card-hover-border" in TOKENS
    assert "border-radius: 17.1875%" in CATALOGUE
