from google.cloud import translate_v2 as translate

translate_client = translate.Client()

def translate(text, origin, to):
    result = translate_client.translate(text, target_language=to, source_language=origin)
    return result["translatedText"]
