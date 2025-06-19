import deepl
import os
import xml.etree.ElementTree as ET

API_KEY = os.environ["DEEPL_API_KEY"]
file_name = "cad_2021-03-18.xml"

source_lang = "EN"
target_lang = "JA"
translator = deepl.Translator(API_KEY)

tree = ET.parse(file_name)
root = tree.getroot()

for sentence in root.iter("script"):
    text = sentence.text
    result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
    sentence.text = str(result)

tree.write("data.xml", encoding="UTF-8")