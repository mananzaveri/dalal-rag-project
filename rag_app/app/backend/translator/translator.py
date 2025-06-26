from transformers import MarianMTModel, MarianTokenizer

translation_models = {}

def load_model(src_lang, tgt_lang):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    if model_name not in translation_models:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        translation_models[model_name] = (tokenizer, model)
    return translation_models[model_name]

def translate(text, src_lang, tgt_lang):
    if src_lang == tgt_lang:
        return text
    try:
        tokenizer, model = load_model(src_lang, tgt_lang)
        tokens = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt", padding=True)
        output = model.generate(**tokens)
        return tokenizer.decode(output[0], skip_special_tokens=True)
    except Exception as e:
        return f"[Translation error: {e}]"