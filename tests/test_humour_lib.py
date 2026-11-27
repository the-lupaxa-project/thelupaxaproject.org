import pytest

from humour_lib import collect_tags, is_remote_media, load_humour_data, media_stem, published_entries, validate_humour

SAMPLE = {
    "page": {"background": "#111111", "text_color": "#f5f5f5"},
    "entries": [
        {
            "image": "assets/images/humour/a.jpg",
            "comment": "Visible",
            "tags": ["travel", "coast"],
        },
        {
            "image": "assets/images/humour/draft.jpg",
            "comment": "Draft",
            "published": False,
            "tags": ["hidden-tag"],
        },
        {
            "image": "https://example.com/b.jpg",
            "published": True,
            "tags": ["travel"],
        },
        {
            "image": "assets/images/humour/c.jpg",
        },
    ],
}


def test_published_entries_defaults_true_and_respects_false():
    result = published_entries(SAMPLE)
    images = [entry["image"] for entry in result]
    assert images == [
        "assets/images/humour/a.jpg",
        "https://example.com/b.jpg",
        "assets/images/humour/c.jpg",
    ]


def test_collect_tags_unique_sorted_from_given_list():
    entries = published_entries(SAMPLE)
    assert collect_tags(entries) == ["coast", "travel"]


def test_collect_tags_excludes_reserved_media_tags():
    entries = [
        {"image": "a.jpg", "tags": ["travel", "images"]},
        {"video": "b.mp4", "tags": ["videos", "animals"]},
    ]
    assert collect_tags(entries) == ["animals", "travel"]


def test_load_humour_data_reads_yaml(tmp_path):
    path = tmp_path / "humour.yml"
    path.write_text("page:\n  background: '#1a1a1a'\n  text_color: '#f5f5f5'\nentries:\n  - image: assets/images/humour/x.jpg\n    comment: Hi\n", encoding="utf-8")
    data = load_humour_data(path)
    assert data["page"]["background"] == "#1a1a1a"
    assert data["entries"][0]["image"] == "assets/images/humour/x.jpg"


def test_load_humour_data_rejects_non_mapping_yaml(tmp_path):
    path = tmp_path / "humour.yml"
    path.write_text("- image: assets/images/humour/x.jpg\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping at the top level"):
        load_humour_data(path)


def test_validate_humour_rejects_missing_media():
    data = {"entries": [{"comment": "No image field"}]}
    with pytest.raises(ValueError, match="image or video"):
        validate_humour(data)


def test_validate_humour_accepts_video_without_image():
    data = {"entries": [{"video": "https://example.com/clip.mp4", "tags": ["video"]}]}
    validate_humour(data)


def test_validate_humour_rejects_tags_as_string():
    data = {"entries": [{"image": "assets/images/humour/x.jpg", "tags": "travel"}]}
    with pytest.raises(ValueError, match="tags"):
        validate_humour(data)


def test_validate_humour_rejects_non_mapping_entry():
    data = {"entries": ["assets/images/humour/x.jpg"]}
    with pytest.raises(ValueError, match="mapping"):
        validate_humour(data)


def test_validate_humour_ignores_unpublished_entries():
    data = {"entries": [{"published": False, "comment": "Draft only"}]}
    validate_humour(data)


def test_is_remote_media():
    assert is_remote_media("https://example.com/a.jpg")
    assert is_remote_media("http://example.com/a.jpg")
    assert not is_remote_media("assets/images/humour/a.jpg")


def test_media_stem_uses_filename_without_query_or_extension():
    assert media_stem("assets/images/humour/comic-03-password-policy.webp") == ("comic-03-password-policy")
    assert media_stem("assets/images/humour/comic-87-smishing.webp?v=1") == "comic-87-smishing"
    assert media_stem("https://example.com/clips/demo.mp4") == "demo"
    assert media_stem("assets/images/humour/plain") == "plain"
