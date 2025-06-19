import deepl
import os

API_KEY = os.environ["DEEPL_API_KEY"]
file_name = "SentiWordNet_3.0.0_adj.txt"
# file_name = "mini.txt"
output_file = "SentiWordNet_translated.txt"

source_lang = "EN"
target_lang = "JA"
translator = deepl.Translator(API_KEY)

count = 0
with open(file_name, "r") as fs, open(output_file, "w") as fd:
    for line in fs:
        if line.startswith("#"):
            fd.write(line)
            continue
        items = line.split("\t")
        pre_words = items[4].split()
        nums = list(map(lambda x: x.split("#")[1], pre_words))
        words = list(map(lambda x: x.split("#")[0], pre_words))
        words_translated = list(map(lambda x: translator.translate_text(x, source_lang=source_lang, target_lang=target_lang), words))
        for i in range(len(words)):
            words_translated[i] = words_translated[i].text + "#" + nums[i]
        translated_str = " ".join(words_translated)
        post_items = items[:4] + [translated_str] + items[5:]
        post_line = "\t".join(post_items)
        fd.write(post_line)
        count += 1
        if count % 10 == 0:
            print(count)

# for sentence in root.iter("script"):
#     text = sentence.text
#     result = translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
#     sentence.text = str(result)
