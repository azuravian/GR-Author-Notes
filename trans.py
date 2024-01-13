from googletrans import Translator
import html

def translate(string: str, lang):
    translator = Translator()
    return html.unescape(translator.translate(string, dest=lang).text)

def translate_list(list: list, lang):
    return [translate(item, lang) for item in list]