from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, NotValidLength

def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
    """
    Translate a string to the desired language using Google Translate (via deep-translator).
    
    Args:
        text (str): The text you want to translate
        target_lang (str): Target language code (e.g. 'es', 'fr', 'de', 'zh-cn', 'ja')
        source_lang (str): Source language code or 'auto' to detect automatically (default: 'auto')
    
    Returns:
        str: The translated text
    
    Raises:
        ValueError: If translation fails (e.g. empty text, invalid language, network issue)
    
    Examples:
        translate_text("Hello world", "es")          → "Hola mundo"
        translate_text("Bonjour le monde", "en")    → "Hello world"
        translate_text("Ciao mondo", target_lang="fr", source_lang="it")
    """
    if not text or not text.strip():
        return ""
    if source_lang == target_lang:
        return text

    try:
        # Create a fresh translator instance with the requested languages
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        # Perform the translation
        result = translator.translate(text)
        
        return result
        
    except NotValidPayload:
        return text  # return original if nothing to translate
    except NotValidLength:
        # Google has ~5000 char limit per request — you could split long text here if needed
        return text
    except Exception as e:
        # Network error, rate limit, invalid lang code, etc.
        return text