"""Bot-level i18n wiring: greetings must come from the catalogue."""

from pathlib import Path

import pytest

from src.bot import Yuuki
from src.config import Config


@pytest.fixture
def bot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Yuuki:
    monkeypatch.chdir(tmp_path)
    return Yuuki(Config())


def test_greeting_uses_catalogue(bot: Yuuki) -> None:
    assert bot.greeting() == (
        "Helllo^^\nMy name is Yuuki ><\nNice to meet you OwO"
    )


def test_greeting_respects_default_language(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    config = Config()
    config.yuuki.default_language = "zh-tw"
    assert Yuuki(config).greeting() == (
        "安安^^\n我是Yuuki呦><\n請多多指教OwO"
    )


def test_get_text_interpolation(bot: Yuuki) -> None:
    assert bot.get_text("security.disabled", name="Yuuki") == (
        "SecurityService of Yuuki was disable"
    )
