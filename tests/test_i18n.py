"""Yuuki i18n: vue-i18n style key-value catalogues."""

import re

from src.i18n import Language
from src.i18n.en import ENGLISH
from src.i18n.zh_tw import TRADITIONAL_CHINESE


def make_language():
    return Language("zh-tw")


def test_key_value_lookup():
    language = make_language()
    assert language.gettext("common.bye") == "掰掰 ><"


def test_named_interpolation():
    language = make_language()
    assert language.gettext("greeting", name="Yuuki") == (
        "安安^^\n我是Yuuki呦><\n請多多指教OwO"
    )
    assert Language("en").gettext("greeting", name="Yuuki") == (
        "Helllo^^\nMy name is Yuuki ><\nNice to meet you OwO"
    )


def test_default_language_used_without_lang():
    language = make_language()
    assert language.gettext("common.okay") == "好的"
    assert language.gettext("common.okay", lang="en") == "Okay"


def test_missing_key_falls_back_to_key():
    language = make_language()
    assert language.gettext("no.such.key") == "no.such.key"


def test_unsupported_language_falls_back_to_english():
    language = make_language()
    assert language.gettext("common.okay", lang="fr") == "Okay"


PLACEHOLDER = re.compile(r"\{(\w+)\}")


def test_catalogues_have_identical_keys():
    assert set(ENGLISH) == set(TRADITIONAL_CHINESE)
    # every message must interpolate the same placeholders
    for key, template in ENGLISH.items():
        assert set(PLACEHOLDER.findall(template)) == set(
            PLACEHOLDER.findall(TRADITIONAL_CHINESE[key])
        ), key
