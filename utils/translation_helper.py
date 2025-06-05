from google.cloud import translate_v2 as translate

translate_client = translate.Client()

def detect_language(text):
    result = translate_client.detect_language(text)
    return result['language']

def translate_to_english(text):
    result = translate_client.translate(text, target_language='en')
    return result['translatedText']

def translate_from_english(text, target_lang):
    if target_lang == 'en':
        return text
    result = translate_client.translate(text, target_language=target_lang)
    return result['translatedText']
