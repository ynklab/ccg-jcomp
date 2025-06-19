import argparse
from depccg.tools.reader import read_jigg_xml


def convert(tree, tokens):
    def replace_bracket(s):
        return s.replace("(", "<") \
                .replace(")", ">") \
                .replace("=", "~") \
                .replace("[", "`") \
                .replace("]", "\'")

    def convert_rec(node):
        if node.is_leaf:
            cat = replace_bracket(str(node.cat))
            word = node.word
            for token in tokens:
                if token["surf"] == word:
                    pos = token["pos"]
                    pos1 = token["pos1"]
                    pos2 = token["pos2"]
                    pos3 = token["pos3"]
            return f"({cat};{pos};{pos1};{pos2};{pos3} {word})"
        else:
            cat = replace_bracket(str(node.cat))
            children = " ".join(convert_rec(child) for child in node.children)
            return f"({cat} {children})"

    return f"(ROOT {convert_rec(tree)})"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert jigg.xml format into Penn Treebank format")
    parser.add_argument("fname")

    args = parser.parse_args()
    for name, tokens, tree in read_jigg_xml(args.fname):
        print(convert(tree, tokens))