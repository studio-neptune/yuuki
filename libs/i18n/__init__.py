#!/usr/bin/python3
# coding=UTF-8

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
