# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from .en import English
from .zh_TW import Traditional_Chinese


class Yuuki_LangSetting:
    def __init__(self, default):
        self.default = default
        self.support = {
            "en": English,
            "zh-tw": Traditional_Chinese
        }

    def gettext(self, text, lang=None):
        try:
            if lang:
                return self.support[lang].i18nText[text]
            return self.support[self.default].i18nText[text]
        except KeyError:
            return text + "\n\n{\n\tLanguage Package not work.\n\tPlease inform the Admin of the Yuuki.\n}"

    def _(self, text, lang=None):
        return self.gettext(text, lang)
