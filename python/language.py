from langdetect import detect
from google.cloud import translate_v2 as translate

translate_client = translate.Client()


def translate(text, to):
    result = translate_client.translate(text, target_language=to)
    return result["translatedText"]


def detect_language(text: str) -> str:
    return detect(text)


def is_text_of_language(text: str, language_code: str) -> bool:
    return detect_language(text) == language_code
