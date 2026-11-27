from pathlib import Path

HUMOUR_CSS = (Path(__file__).resolve().parent.parent / "mkdocs/assets/stylesheets/50-pages/humour.css").read_text(encoding="utf-8")


def test_humour_open_uses_pointer_cursor():
    assert "cursor: zoom-in" not in HUMOUR_CSS
    assert ".humour-open" in HUMOUR_CSS
    assert "cursor: pointer" in HUMOUR_CSS
