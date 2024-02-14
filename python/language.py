from langcodes import Language, find
from google.cloud import translate_v2
from google.oauth2.service_account import Credentials
from typing import Optional

translate_client = translate_v2.Client()


def init_language(credentials: Optional[Credentials]) -> None:
    """
    Initialize Google Translate client

    :param credentials: a Google Credentials object
    """
    global translate_client
    translate_client = translate_v2.Client(credentials=credentials)


def translate(text: str, to: str) -> str:
    """
    Translate text

    :param text: text to translate
    :param to: ISO 639-1 code of the language to translate the text to
    :return: translated text
    """
    result = translate_client.translate(text, target_language=to, format_="html")
    return result["translatedText"]


def detect_language(text: str) -> str:
    """
    Detect language of text

    :param text: a string
    :return: ISO 639-1 code of the language detected (as string)
    """
    return translate_client.detect_language(text)["language"]


def is_text_of_language(text: str, language_code: str) -> bool:
    """
    Whether ot not the text is written in this language

    :param text: a string
    :param language_code: ISO 639-1 code of the language
    :return: True or False
    """
    return detect_language(text) == language_code


def language_name_to_iso6391(language_name: str) -> str:
    """
    Convert language name to ISO 639-1 code
    i.e.: English -> en

    :param language_name: string
    :return: ISO 639-1 code (as string)
    """
    return find(language_name).language


def iso6391_to_language_name(language_code: str, name_in_same_language: bool = False) -> str:
    """
    Convert ISO 639-1 code to language name

    :param language_code: ISO 639-1 code (as string)
    :param name_in_same_language: if True, name is returned in that language. Otherwise, name returns in English
                                  True: fr -> Français | False: fr -> French
    :return: language name
    """
    display_lang = language_code if name_in_same_language else "en"
    return Language.get(language_code).display_name(display_lang)


def locale_code_to_language(locale_code: str, name_in_same_language: bool = False):
    """
    Convert language code and locale (i.e. "fr-FR") to language name

    :param locale_code: string
    :param name_in_same_language: if True, name is returned in that language. Otherwise, name returns in English
                                  True: es-US -> Español (Estados Unidos) | False:es-US -> Spanish (United States)
    :return: language name
    """
    display_lang = locale_code.split('-')[0] if name_in_same_language else "en"
    return Language.get(locale_code).display_name(display_lang).title()
