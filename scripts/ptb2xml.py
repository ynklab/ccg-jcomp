import argparse
from depccg.tools.reader import read_trees_guess_extension
from depccg.printer import print_
from depccg.tokens import Token
import xml.etree.ElementTree as ET


def get_init_tags(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    lst = []
    for token in root.iter("token"):
        lst.append(
            {
                "word": token.attrib["surf"],
                "entity": token.attrib["entity"],
                "pos": token.attrib["pos"],
                "pos1": token.attrib["pos1"],
                "pos2": token.attrib["pos2"],
                "pos3": token.attrib["pos3"],
                "inflectionForm": token.attrib["inflectionForm"],
                "inflectionType": token.attrib["inflectionType"],
                "reading": token.attrib["reading"],
                "base": token.attrib["base"]
            }
        )
    return lst


def add_tags(filename, doc):
    lst = get_init_tags(filename)
    empty = ["cmp"]
    proper_noun = ["PC-6082", "ITEL-XZ", "ITEL-ZX", "ITEL-ZY"]
    post_pp = ["よりも", "に比べると", "以上に", "と同じ", "と同じくらいの", "と同じくらい", "と少なくとも同じくらいの"]
    cat_adjpos = ["多くの"]
    aux_vrb = ["ではない"]
    res = []
    for sentence in doc:
        tokens = []
        for token in sentence:
            token = str(token)
            found = False
            if token in empty:
                tokens.append(
                    Token(
                        word=token,
                        pos="EMP",
                        pos1="*",
                        pos2="*",
                        pos3="*",
                        inflectionForm="*",
                        inflectionType="*",
                        entity="*",
                        reading="*",
                        base=token
                    )
                )
                found = True
            elif token in proper_noun:
                tokens.append(
                    Token(
                        word=token,
                        pos="名詞",
                        pos1="固有名詞",
                        pos2="*",
                        pos3="*",
                        inflectionForm="*",
                        inflectionType="*",
                        entity="*",
                        reading="*",
                        base=token
                    )
                )
                found = True
            elif token in post_pp:
                tokens.append(
                    Token(
                        word=token,
                        pos="助詞",
                        pos1="格助詞",
                        pos2="一般",
                        pos3="*",
                        inflectionForm="*",
                        inflectionType="*",
                        entity="*",
                        reading="*",
                        base=token
                    )
                )
                found = True
            elif token in cat_adjpos:
                tokens.append(
                    Token(
                        word=token,
                        pos="形容詞",
                        pos1="自立",
                        pos2="*",
                        pos3="*",
                        inflectionForm="*",
                        inflectionType="*",
                        entity="POS",
                        reading="*",
                        base=token
                    )
                )
                found = True
            elif token in aux_vrb:
                tokens.append(
                    Token(
                        word=token,
                        pos="助動詞",
                        pos1="*",
                        pos2="*",
                        pos3="*",
                        inflectionForm="*",
                        inflectionType="*",
                        entity="*",
                        reading="*",
                        base=token
                    )
                )
                found = True
            if not found:
                for d in lst:
                    if token == d["word"]:
                        tokens.append(
                            Token(
                                surf=token,
                                pos=d["pos"],
                                pos1=d["pos1"],
                                pos2=d["pos2"],
                                pos3=d["pos3"],
                                inflectionForm=d["inflectionForm"],
                                inflectionType=d["inflectionType"],
                                entity=d["entity"],
                                reading=d["reading"],
                                base=d["base"]
                            )
                        )
                        lst.remove(d)
                        break
        res.append(tokens)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser("convert Penn Treebank format into jigg.xml format")
    parser.add_argument("PATH")
    args = parser.parse_args()

    doc, trees = [], []
    for _, tokens, tree in read_trees_guess_extension(args.PATH, lang="ja"):
        doc.append([token.word for token in tokens])
        trees.append([(tree, 0)])
        filename = args.PATH.replace("tsgn.mod.ptb", "init.jigg.xml")
    tagged_doc = add_tags(filename, doc)

    print_(trees, tagged_doc, format="jigg_xml", lang="ja")
