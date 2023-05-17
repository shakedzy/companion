from google.cloud import translate_v2 as translate

translate_client = translate.Client()


def translate(text, to):
    result = translate_client.translate(text, target_language=to)
    return result["translatedText"]
