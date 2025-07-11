from deep_translator import GoogleTranslator

lang_map = {
    "english": "english",
    "spanish": "spanish",
    "hindi": "hindi",
    "french": "french",
    "chinese": "chinese",
    "gujarati": "gujarati",
    "thai": "thai"
}

def translate(text, src_lang, tgt_lang):
    src = lang_map.get(src_lang.lower(), "english")
    tgt = lang_map.get(tgt_lang.lower(), "english")

    if src == tgt or not text.strip():
        return text
    try:
        return GoogleTranslator(source=src, target=tgt).translate(text)
    except Exception as e:
        return f"[Translation error: {e}]"