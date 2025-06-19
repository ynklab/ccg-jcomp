import xml.etree.ElementTree as ET


def extract(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    problems = root.findall("problem")
    for problem in problems:
        premises = problem.findall("p")
        hypothesis = problem.find("h")
        file_name = "jsem_" + problem.get("jsem_id")
        with open("./jsem_plain/" + file_name + ".txt", "w", encoding="utf-8") as ftxt, \
             open("./jsem_plain/" + file_name + ".answer", "w", encoding="utf-8") as fanswer:
            for premise in premises:
                ftxt.write(premise.find("script").text + "\n")
            ftxt.write(hypothesis.find("script").text + "\n")
            fanswer.write(problem.get("answer"))


if __name__ == "__main__":
    file_name = "./data/Comparatives.xml"
    extract(file_name)