"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import logging

from .en import ENGLISH
from .zh_tw import TRADITIONAL_CHINESE

logger = logging.getLogger(__name__)


class Language:
    """Key-value catalogue with named interpolation, vue-i18n style.

    Lookup by semantic key; missing keys fall back to the key itself
    (logged), and named ``{placeholders}`` are interpolated on request::

        language.gettext("greeting", name="Yuuki")
    """

    def __init__(self, default: str = "en") -> None:
        self.default = default
        self.packages: dict[str, dict[str, str]] = {
            "en": ENGLISH,
            "zh-tw": TRADITIONAL_CHINESE,
        }

    def gettext(
        self, key: str, lang: str | None = None, **kwargs: object
    ) -> str:
        package = self.packages.get(lang or self.default, ENGLISH)
        template = package.get(key)
        if template is None:
            logger.warning("Missing i18n key %r (lang=%r)", key, lang)
            return key
        if kwargs:
            return template.format(**kwargs)
        return template

    def supports(self) -> list[str]:
        return sorted(self.packages)
