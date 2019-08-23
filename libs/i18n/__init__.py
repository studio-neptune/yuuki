#!/usr/bin/python3
# coding=UTF-8

from .en import English

class Yuuki_LangSetting:
    def __init__(self, default):
        self.default = default
        self.support = {
            "en":English
        }

    def gettext(self, text, lang=None):
        if lang:
            return self.support[lang].i18nText[text]
        return self.support[self.default].i18nText[text]

    def _(self, text, lang=None):
        return self.gettext(text, lang)
