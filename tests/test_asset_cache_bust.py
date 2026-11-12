import os
from pathlib import Path

import asset_cache_bust
from asset_cache_bust import apply_asset_version, dev_asset_token, extra_asset_paths


def test_extra_asset_paths_strips_queries_and_dict_javascript():
    paths = extra_asset_paths(
        {
            "extra_css": ["assets/stylesheets/00-tokens.css?v=old"],
            "extra_javascript": [
                "assets/javascript/page-lifecycle.js",
                {"path": "assets/javascript/humour.js", "type": "module"},
            ],
        }
    )
    assert paths == [
        "assets/stylesheets/00-tokens.css",
        "assets/javascript/page-lifecycle.js",
        "assets/javascript/humour.js",
    ]


def test_apply_asset_version_rewrites_relative_extra_assets_only():
    html = """
<link rel="stylesheet" href="../assets/stylesheets/main.ec1eaa64.min.css">
<link rel="stylesheet" href="../assets/stylesheets/catalogue.css">
<script src="../assets/javascripts/bundle.d7400e89.min.js"></script>
<script src="../assets/javascript/catalogue-filters.js"></script>
"""
    out = apply_asset_version(
        html,
        [
            "assets/stylesheets/catalogue.css",
            "assets/javascript/catalogue-filters.js",
        ],
        "9ee1eb2",
    )
    assert 'href="../assets/stylesheets/catalogue.css?v=9ee1eb2"' in out
    assert 'src="../assets/javascript/catalogue-filters.js?v=9ee1eb2"' in out
    assert "main.ec1eaa64.min.css?" not in out
    assert "bundle.d7400e89.min.js?" not in out


def test_apply_asset_version_replaces_an_existing_query():
    html = '<link rel="stylesheet" href="assets/stylesheets/99-overrides.css?v=old">'
    out = apply_asset_version(
        html,
        ["assets/stylesheets/99-overrides.css"],
        "abc1234",
    )
    assert out == ('<link rel="stylesheet" href="assets/stylesheets/99-overrides.css?v=abc1234">')


def test_mkdocs_registers_the_hook():
    yml = (Path(__file__).resolve().parent.parent / "mkdocs.yml").read_text(encoding="utf-8")
    assert "- hooks/article_nav.py" in yml
    assert "- hooks/asset_cache_bust.py" in yml
    assert yml.index("- hooks/article_nav.py") < yml.index("- hooks/asset_cache_bust.py")
    for entry in (
        "- main.py",
        "- data",
        "- hooks",
        "- src",
        "- overrides",
        "- mkdocs/assets/stylesheets",
        "- mkdocs/assets/javascript",
    ):
        assert entry in yml


def test_dev_asset_token_follows_the_newest_file(tmp_path):
    css = tmp_path / "catalogue.css"
    css.write_text("a", encoding="utf-8")
    first = dev_asset_token([css, tmp_path / "missing.js"])
    stamped = css.stat().st_mtime_ns + 1_000_000
    os.utime(css, ns=(stamped, stamped))
    second = dev_asset_token([css])
    assert first.startswith("dev")
    assert first != second


def test_serve_uses_file_time_for_asset_urls(tmp_path):
    css = tmp_path / "catalogue.css"
    css.write_text("body{}", encoding="utf-8")
    asset_cache_bust._DEV_SERVER = False
    try:
        published = asset_cache_bust.asset_version()
        assert published != "dev"
        assert not published.startswith("dev")
        asset_cache_bust.on_serve(object(), {})
        served = asset_cache_bust.asset_version(asset_paths=[css])
        assert served == dev_asset_token([css])
    finally:
        asset_cache_bust._DEV_SERVER = False
        import banner_lib

        banner_lib.DEV_SERVER = False
