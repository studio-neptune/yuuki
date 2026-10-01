"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

DEFAULT_CONFIG_PATH = "config.yaml"


class YuukiSettings(BaseModel):
    """Runtime behaviour of the bot itself."""

    security_service: bool = False
    default_language: str = "en"
    admin: list[str] = Field(default_factory=list)
    hour_kick_limit: int = 10
    hour_cancel_limit: int = 10
    group_members_demand: int = 100
    webadmin_enabled: bool = False
    webadmin_port: int = 2020
    helper_tokens: list[str] = Field(default_factory=list)
    version_check: bool = True
    project_url: str = "https://tinyurl.com/syb-yuuki"
    man_page: str = "https://tinyurl.com/yuuki-manual"
    copyright: str = "(c)2026 Star Inc."


class LineServerSettings(BaseModel):
    """LINE API endpoints."""

    host: str = ""
    command_path: str = ""
    long_poll_path: str = ""


class LineAccountSettings(BaseModel):
    """Headers identifying the application on LINE API."""

    x_line_application: str = ""
    x_line_access: str = ""
    user_agent: str = ""


class LineSettings(BaseModel):
    server: LineServerSettings = Field(default_factory=LineServerSettings)
    account: LineAccountSettings = Field(default_factory=LineAccountSettings)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-Line-Application": self.account.x_line_application,
            "X-Line-Access": self.account.x_line_access,
            "User-Agent": self.account.user_agent,
        }

    def with_token(self, token: str) -> LineSettings:
        """Return a copy of these settings bound to another access token."""
        account = self.account.model_copy(update={"x_line_access": token})
        return self.model_copy(update={"account": account})


class Config(BaseSettings):
    """Root configuration, loaded from a YAML file and the environment."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
    )

    yuuki: YuukiSettings = Field(default_factory=YuukiSettings)
    line: LineSettings = Field(default_factory=LineSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_source = YamlConfigSettingsSource(
            settings_cls, yaml_file=os.getenv("YUUKI_CONFIG", DEFAULT_CONFIG_PATH)
        )
        return (init_settings, env_settings, yaml_source)

    @classmethod
    def load(cls, path: str | None = None) -> Config:
        if path:
            os.environ["YUUKI_CONFIG"] = path
        resolved = os.getenv("YUUKI_CONFIG", DEFAULT_CONFIG_PATH)
        if not os.path.exists(resolved):
            raise FileNotFoundError(
                f"Config file not found: {resolved} "
                f"(copy config.sample.yaml to {DEFAULT_CONFIG_PATH})"
            )
        return cls()
