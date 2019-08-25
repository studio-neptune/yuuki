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
        try:
            if lang:
                return self.support[lang].i18nText[text]
            return self.support[self.default].i18nText[text]
        except KeyError:
            return text + "\n\n{Language Package is not Work, please inform the Admin of the Yuuki}"

    def _(self, text, lang=None):
        return self.gettext(text, lang)
