import xml.etree.ElementTree as ET
import argparse
from adj_posneg import sentiwordnet as swn


def add_posneg_tag(token):
    # This part needs to be improved
    Fpos = ["高い", "速い", "良い", "大きい", "重い", "面白い", "鋭い", "遠い", "強い", "太い", "明るい"]
    Fneg = ["低い", "遅い", "悪い", "小さい", "軽い", "つまらない", "鈍い", "近い", "弱い", "細い", "暗い"]
    Fabs = []
    word = token.attrib["base"]
    if word in Fpos or word + "だ" in Fpos or ("が" in word and word.split("が")[1] in Fpos):
        token.attrib["entity"] = "POS"
    elif word in Fneg or word + "だ" in Fneg or ("が" in word and word.split("が")[1] in Fneg):
        token.attrib["entity"] = "NEG"
    elif word in Fabs or word + "だ" in Fabs or ("が" in word and word.split("が")[1] in Fabs):
        token.attrib["entity"] = "ABS"
    else:
        if not swn.senti_synset("a", word) is None:
            pos_score = swn.senti_synset("a", word).pos_score()
            neg_score = swn.senti_synset("a", word).neg_score()
        elif not swn.senti_synset("a", word + "だ") is None:
            pos_score = swn.senti_synset("a", word + "だ").pos_score()
            neg_score = swn.senti_synset("a", word + "だ").neg_score()
        elif "が" in word and not swn.senti_synset("a", word.split("が")[1]) is None:
            pos_score = swn.senti_synset("a", word.split("が")[1]).pos_score()
            neg_score = swn.senti_synset("a", word.split("が")[1]).neg_score()
        else:
            token.attrib["entity"] = "PRE"
            return
        if pos_score > neg_score:
            token.attrib["entity"] = "POS"
        elif neg_score > pos_score:
            token.attrib["entity"] = "NEG"
        else:
            token.attrib["entity"] = "PRE"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("tag_file")
    args = parser.parse_args()

    tree = ET.parse(args.file_name)
    root = tree.getroot()
    sentences = root.findall("./document/sentences/sentence")
    with open(args.tag_file, "r") as f:
        for sentence in sentences:
            tokens = sentence.findall("tokens/token")
            for token in tokens:
                tag = next(f).split("\t")[1]
                pos, pos1, pos2, pos3, inflectionForm, inflectionType, base, reading, phonetic\
                = tag.split(",")
                token.attrib.pop("entity", None)
                token.attrib.pop("chunk", None)
                token.set("pos", pos)
                token.set("pos1", pos1)
                token.set("pos2", pos2)
                token.set("pos3", pos3)
                token.set("inflectionForm", inflectionForm)
                token.set("inflectionType", inflectionType)
                token.set("base", base)
                token.set("reading", reading)
                token.set("phonetic", phonetic)
                if token.attrib["pos"] == "形容詞" or token.attrib["pos1"] == "形容動詞語幹":
                    add_posneg_tag(token)
                else:
                    token.set("entity", "*")
    tree.write(args.file_name, encoding="utf-8")