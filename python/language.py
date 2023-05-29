from google.cloud import translate_v2 as translate

translate_client = translate.Client()


def translate(text, to) -> str:
    result = translate_client.translate(text, target_language=to, format_="html")
    return result["translatedText"]


def detect_language(text: str) -> str:
    return translate_client.detect_language(text)["language"]


def is_text_of_language(text: str, language_code: str) -> bool:
    return detect_language(text) == language_code
