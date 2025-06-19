import xml.etree.ElementTree as ET
import argparse


def eval_dataset(file_name, semantic_template):
    tree = ET.parse(file_name)
    root = tree.getroot()
    print(root)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("semantic_template")
    args = parser.parse_args()

    assert args.dataset in ["jsem", "cad"]
    file_name = "./data/Comparatives.xml" if args.dataset == "jsem" \
        else "./data/data.xml"
    eval_dataset(file_name, args.semantic_template)