from babel.support import Translations


def get_translation(lang_code):
    try:
        translation = Translations.load('locales', [lang_code])
    except FileNotFoundError:
        translation = Translations.load('locales', ['en'])
    return translation.gettext

gettext = {'en': get_translation('en'), 'ru': get_translation('ru')}
