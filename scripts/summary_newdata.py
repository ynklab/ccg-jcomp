import argparse
import datetime
import json

RED_COLOR = "rgb(255, 0, 0)"
GREEN_COLOR = "rgb(0, 255, 0)"

def generate_section_result(problems, system_answer_dir):
    section_name = problems[0]["id"].rsplit("_", 1)[0]
    gold_answers = []
    system_answers = []
    num_problems = len(problems)
    num_correct = 0
    for problem in problems:
        id = problem["id"]
        gold_answer = problem["answer"]
        with open(f"{system_answer_dir}/{id}.answer", "r") as fans:
            system_answer = fans.readline().rstrip("\n")
        gold_answers.append(gold_answer)
        system_answers.append(system_answer)
        if system_answer == gold_answer:
            num_correct += 1
    accuracy = num_correct / num_problems
    head = f"""\
    <!doctype html>
    <html lang='ja'>
    <head>
    <meta charset='UTF-8'>
    <title>Evaluation results of NewData </title>
    <style>
        body {{
        font-size: 1.5em;
        }}
        #table {{
            margin: auto;
        }}
        td {{
            padding: 5px;
        }}
    </style>
    </head>
    <body>
    <ul>
        <li>Section: {section_name}</li>
        <li># of problems: {num_problems}</li>
        <li>Accuracy: {accuracy}</li>
    </ul>
    <table id=\"table\" border=\"1\">
    <tr>
        <th colspan=\"3\"> problem </th>
        <th> gold answer </th>
        <th> system answer </th>
    </tr>"""

    with open(f"{system_answer_dir}/{section_name}.html", "w") as f:
        f.write(head)
        for i, d in enumerate(problems):
            id = d["id"]
            gold_answer = gold_answers[i]
            system_answer = system_answers[i]
            sentences = d["premises"] + [d["hypothesis"]]
            num_sentences = len(sentences)
            if system_answer == gold_answer:
                color = GREEN_COLOR
            else:
                color = RED_COLOR
            for i, sentence in enumerate(sentences):
                if i == 0:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td rowspan=\"{num_sentences}\">{id}</td>\n" +\
                            "\t<td>premise 1</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\">{gold_answer}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\"><a style=\"background-color:{color}\" href=\"{id}.html\">{system_answer}</a></td>\n" +\
                        "\t</tr>")
                elif i < num_sentences - 1:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td>premise {i + 1}</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
                else:
                    f.write(\
                        "<tr>\n" +\
                            "\t<td>hypothesis</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
    return num_problems, num_correct

def generate_category_results(problems, category, system_answer_dir):
    section_name = ""
    section_problems = []
    total_num_problems = 0
    total_num_correct = 0
    example_problems = []
    accuracies = []
    for problem in problems:
        section_name_ = problem["id"].rsplit("_", 1)[0]
        if section_name == section_name_:
            section_problems.append(problem)
        else:
            if section_problems:
                num_problems, num_correct = generate_section_result(section_problems, system_answer_dir)
                total_num_problems += num_problems
                total_num_correct += num_correct
                accuracies.append(num_correct / num_problems)
            example_problems.append(problem)
            section_name = section_name_
            section_problems = [problem]
    num_problems, num_correct = generate_section_result(section_problems, system_answer_dir)
    total_num_problems += num_problems
    total_num_correct += num_correct
    accuracies.append(num_correct / num_problems)
    accuracy = total_num_correct / total_num_problems
    head = f"""\
    <!doctype html>
    <html lang='ja'>
    <head>
    <meta charset='UTF-8'>
    <title>Evaluation results of NewData </title>
    <style>
        body {{
        font-size: 1.5em;
        }}
        #table {{
            margin: auto;
        }}
        td {{
            padding: 5px;
        }}
    </style>
    </head>
    <body>
    <ul>
        <li>Category: {category}</li>
        <li># of problems: {total_num_problems}</li>
        <li>Accuracy: {accuracy}</li>
    </ul>
    <table id=\"table\" border=\"1\">
    <tr>
        <th> section </th>
        <th colspan=\"2\"> example </th>
        <th> gold answer </th>
        <th> accuracy </th>
    </tr>"""
    with open(f"{system_answer_dir}/{category}.html", "w") as f:
        f.write(head)
        for i, problem in enumerate(example_problems):
            section_name = problem["id"].rsplit("_", 1)[0]
            gold_answer = problem["answer"]
            accuracy = accuracies[i]
            sentences = problem["premises"] + [problem["hypothesis"]]
            num_sentences = len(sentences)
            for i, sentence in enumerate(sentences):
                if i == 0:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td rowspan=\"{num_sentences}\">{section_name}</td>\n" +\
                            "\t<td>premise 1</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\">{gold_answer}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\"><a href=\"{section_name}.html\">{accuracy}</td>\n" +\
                        "\t</tr>")
                elif i < num_sentences - 1:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td>premise {i + 1}</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
                else:
                    f.write(\
                        "<tr>\n" +\
                            "\t<td>hypothesis</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
    
    return total_num_problems, total_num_correct

def get_accuracy(problems, system_answer_dir):
    num_problems = len(problems)
    num_correct = 0
    for problem in problems:
        id = problem["id"]
        gold_answer = problem["answer"]
        with open(f"{system_answer_dir}/{id}.answer", "r") as fans:
            system_answer = fans.readline().rstrip("\n")
        if system_answer == gold_answer:
            num_correct += 1
    accuracy = num_correct / num_problems
    return accuracy

def generate_total_results(problems, system_answer_dir):
    total_accuracy = get_accuracy(problems, system_answer_dir)
    total_num_problems = len(problems)
    category_dic = {}
    accuracies = {}
    example_problems = {}
    for problem in problems:
        categories = problem["category"]
        for category in categories:
            if category not in category_dic:
                category_dic[category] = [problem]
                example_problems[category] = problem
            category_dic[category].append(problem)
    for category, problems in category_dic.items():
        num_problems, num_correct = generate_category_results(problems, category,  system_answer_dir)
        accuracy = num_correct / num_problems
        accuracies[category] = accuracy
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    head = f"""\
    <!doctype html>
    <html lang='ja'>
    <head>
    <meta charset='UTF-8'>
    <title>Evaluation results of NewData </title>
    <style>
        body {{
        font-size: 1.5em;
        }}
        #table {{
            margin: auto;
        }}
        td {{
            padding: 5px;
        }}
    </style>
    </head>
    <body>
    <ul>
        <li>Date: {date}</li>
        <li># of problems: {total_num_problems}</li>
        <li>Accuracy: {total_accuracy}</li>
    </ul>
    <table id=\"table\" border=\"1\">
    <tr>
        <th> category </th>
        <th colspan=\"2\"> example </th>
        <th> gold answer </th>
        <th> accuracy </th>
    </tr>"""
    with open(f"{system_answer_dir}/main_results_newdata.html", "w") as f:
        f.write(head)
        for category, problem in example_problems.items():
            gold_answer = problem["answer"]
            accuracy = accuracies[category]
            sentences = problem["premises"] + [problem["hypothesis"]]
            num_sentences = len(sentences)
            for i, sentence in enumerate(sentences):
                if i == 0:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td rowspan=\"{num_sentences}\">{category}</td>\n" +\
                            "\t<td>premise 1</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\">{gold_answer}</td>\n" +\
                            f"\t<td style=\"text-align: center;\" rowspan=\"{num_sentences}\"><a href=\"{category}.html\">{accuracy}</td>\n" +\
                        "\t</tr>")
                elif i < num_sentences - 1:
                    f.write(\
                        "<tr>\n" +\
                            f"\t<td>premise {i + 1}</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
                else:
                    f.write(\
                        "<tr>\n" +\
                            "\t<td>hypothesis</td>\n" +\
                            f"\t<td>{sentence}</td>\n" +\
                        "\t</tr>")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("system_answer_dir")
    args = parser.parse_args()

    with open("jsem_templates/jsem.json", "r") as f:
        problems = json.load(f)

    generate_total_results(problems, args.system_answer_dir)