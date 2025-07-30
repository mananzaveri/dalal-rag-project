from deep_translator import GoogleTranslator
import time
import random

lang_map = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "Russian": "ru",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Chinese (Simplified)": "zh-CN",
    "Thai": "th"
}

def translate(text, src_lang, tgt_lang):
    print(f"Translating from {src_lang} to {tgt_lang}")
    print(f"Text length: {len(text)} characters")
    
    src = lang_map.get(src_lang.strip(), "en")
    tgt = lang_map.get(tgt_lang.strip(), "en")

    if src == tgt or not text.strip():
        print("Same language or empty text, returning original")
        return text
    
    try:
        # Add small delay to avoid rate limiting
        time.sleep(random.uniform(0.3, 0.8))
        
        # Split long text into smaller chunks (Google Translate has limits)
        max_length = 500
        if len(text) > max_length:
            # Split by sentences
            sentences = text.replace('. ', '.|').split('|')
            translated_parts = []
            
            for sentence in sentences:
                if sentence.strip():
                    translator = GoogleTranslator(source=src, target=tgt)
                    translated_part = translator.translate(sentence.strip())
                    translated_parts.append(translated_part)
                    time.sleep(0.2)  # Small delay between chunks
            
            result = ' '.join(translated_parts)
        else:
            # Translate normally for shorter text
            translator = GoogleTranslator(source=src, target=tgt)
            result = translator.translate(text)
        
        if result and result.strip() and result != text:
            print(f"Translation successful: {result[:100]}...")
            return result
        else:
            print("Translation returned empty or identical text")
            return text
            
    except Exception as e:
        print(f"Translation error: {e}")
        return text