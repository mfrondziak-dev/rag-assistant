from rag.i18n import LANGUAGES, TRANSLATIONS, translate


def test_all_languages_share_the_same_keys():
    reference = set(TRANSLATIONS["pl"])
    for lang, table in TRANSLATIONS.items():
        assert set(table) == reference, f"key mismatch in {lang}"


def test_languages_registry_matches_translations():
    assert set(LANGUAGES) == set(TRANSLATIONS)


def test_translate_formats_fields():
    assert "3" in translate("pl", "docs_present", count=3)
    assert "3" in translate("en", "docs_present", count=3)


def test_translate_falls_back_to_english():
    assert translate("de", "app_title") == TRANSLATIONS["en"]["app_title"]


def test_unknown_key_returns_the_key():
    assert translate("en", "definitely_missing") == "definitely_missing"
