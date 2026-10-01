"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from pathlib import Path

import pytest

from src.config import Config
from src.data import DataStore, GroupSecurity

SAMPLE = """
yuuki:
  security_service: true
  default_language: zh-tw
  admin:
    - "u1"
  hour_kick_limit: 5
  group_members_demand: 20
line:
  server:
    host: https://example.com
    command_path: /cmd
    long_poll_path: /poll
  account:
    x_line_application: app
    x_line_access: token
    user_agent: agent
"""


def test_config_load(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(SAMPLE, encoding="utf8")
    config = Config.load(str(config_file))
    assert config.yuuki.security_service is True
    assert config.yuuki.default_language == "zh-tw"
    assert config.yuuki.admin == ["u1"]
    assert config.yuuki.hour_kick_limit == 5
    assert config.yuuki.group_members_demand == 20
    assert config.line.server.host == "https://example.com"
    assert config.line.server.command_path == "/cmd"
    assert config.line.headers["X-Line-Application"] == "app"


def test_config_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Config.load(str(tmp_path / "nope.yaml"))


def test_with_token():
    from src.config import LineSettings

    settings = LineSettings()
    bound = settings.with_token("abc")
    assert bound.account.x_line_access == "abc"
    assert settings.account.x_line_access == ""


def test_store_roundtrip(tmp_path: Path) -> None:
    store = DataStore(data_path=str(tmp_path / "d"), log_path=str(tmp_path / "l"))
    assert store.store.global_data.security_service is False
    store.store.global_data.security_service = True
    store.add_blacklist("u9")
    group = store.group_data("g1")
    group.security = GroupSecurity()
    group.security.configure([0, 3])
    store.reset_limits(["a", "b"], kick_limit=4, cancel_limit=2)
    store.save()

    reloaded = DataStore(
        data_path=str(tmp_path / "d"), log_path=str(tmp_path / "l")
    )
    assert reloaded.store.global_data.security_service is True
    assert reloaded.in_blacklist("u9")
    assert reloaded.add_blacklist("u9") is False
    security = reloaded.group_data("g1").security
    assert security is not None
    assert security.switches[11] is True  # NOTIFIED_UPDATE_GROUP
    assert security.switches[19] is True  # NOTIFIED_KICKOUT_FROM_GROUP
    assert security.switches[13] is False
    assert reloaded.limit_of("kick", "a") == 4
    reloaded.limit_decrease("kick", "a")
    assert reloaded.limit_of("kick", "a") == 3
    shuffled = reloaded.limit_shuffled("kick", ["a", "b"])
    assert sorted(shuffled) == ["a", "b"]


def test_store_logs(tmp_path: Path) -> None:
    store = DataStore(data_path=str(tmp_path / "d"), log_path=str(tmp_path / "l"))
    store.append_log("BlackList", (store.now(), "u1", "g1"))
    content = (tmp_path / "l" / "BlackList.html").read_text(encoding="utf8")
    assert "<li>" in content
    assert "u1" in content
