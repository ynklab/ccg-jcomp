import argparse
import os
import sys
import subprocess
from lxml import etree
from nltk.sem.logic import *
from functools import reduce
import time
import xml.etree.ElementTree as ET
from pykakasi import kakasi

from nltk2tptp import convert_to_tptp_proof
from vampire_axioms import vampire_axioms


kks = kakasi()


def get_formulas_from_xml(doc):
    formulas = [s.get("sem", None) for s in doc.xpath(
        "./sentences/sentence/semantics[1]/span[1]"
    )]
    return formulas


def get_predicates(formula):
    def get_predicate_set(formula_lexpr):
        if isinstance(formula_lexpr, ApplicationExpression):
            return set([formula_lexpr])
        elif isinstance(formula_lexpr, EqualityExpression):
            return set()
        elif isinstance(formula_lexpr, AbstractVariableExpression):
            return set()
        else:
            return formula_lexpr.visit(
                get_predicate_set,
                lambda parts: reduce(operator.or_, parts, set())
            )

    predlst = []
    for pred in get_predicate_set(lexpr(formula)):
        predicate, args = pred.uncurry()
        pred_str = str(predicate)
        args_str = [str(arg) for arg in args]
        item = [pred_str, args_str]
        if item not in predlst:
            predlst.append(item)
    return predlst


def get_types(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    adjlst = []
    objlst = []
    vrblst = []

    for token in root.iter("token"):
        if token.attrib["pos"] in ["形容詞", "形容動詞"]:
            adjlst.append(token.attrib["base"])
        elif token.attrib["base"] == "早起き":
            adjlst.append(token.attrib["base"])
        elif token.attrib["pos"] == "名詞" \
            and not token.attrib["pos1"] == "固有名詞" \
            and not token.attrib["pos1"] == "数" \
            and not token.attrib["pos2"] == "助数詞" \
            and not token.attrib["surf"] == "多く":
            objlst.append(token.attrib["base"])
        elif token.attrib["pos"] == "動詞":
            vrblst.append(token.attrib["base"])

    return adjlst, objlst, vrblst


def is_theorem_in_vampire(lines):
    if lines:
        return ("% Refutation found. Thanks to Tanya!" in lines)
    else:
        return False


def prove_vampire(premises, conclusion, predicates):
    adjlst, objlst, vrblst = get_types(ARGS.sem_file.replace(".sem.xml", ".jigg.xml"))
    # >> add axioms
    types, axioms = vampire_axioms(adjlst, predicates)
    axioms = list(set(axioms))

    ax = lexpr("forall x d. (many(x, d) => forall d1. ($lesseq(d1, d) => many(x, d1)))")
    axioms.append(ax)
    # << add axioms

    premises = axioms + premises
    premises.append(conclusion)
    fols = convert_to_tptp_proof(premises)

    type_f = []
    type_f_adj = types

    for adj in adjlst:
        adj = "".join([d["hepburn"] for d in kks.convert(adj)])
        # adj = str(adj.encode("utf8")).replace("\\", "").replace("\'", "")
        adj_type = "tff(" + adj + "_type, type, " + adj + ": $i * $int > $o)."
        type_f_adj.append(adj_type)

    for obj in objlst:
        obj = "".join([d["hepburn"] for d in kks.convert(obj)])
        # obj = str(obj.encode("utf8")).replace("\\", "").replace("\'", "")
        obj_type = "tff(" + obj + "_type, type, " + obj + ": $i > $o)."
        type_f.append(obj_type)

    for vrb in vrblst:
        vrb = "".join([d["hepburn"] for d in kks.convert(vrb)])
        # vrb = str(vrb.encode("utf8")).replace("\\", "").replace("\'", "")
        vrb_type = "tff(" + vrb + "_type, type, " + vrb + ": $i > $o)."
        type_f.append(vrb_type)


    acc_type = "tff(acc_type, type, acc: $i > $i)." 
    nom_type = "tff(nom_type, type, nom: $i > $i)."
    th_type = "tff(ty_type, type, th: $int)."
    many_type = "tff(many_type, type, many: $i * $int > $o)."
    past_type = "tff(past_type, type, past: $i > $o)."
    type_f.append(acc_type)
    type_f.append(nom_type)
    type_f.append(th_type)
    type_f.append(many_type)
    type_f.append(past_type)

    type_f_adj = list(set(type_f_adj))
    type_f = list(set(type_f))

    fols = type_f + type_f_adj + fols

    file_basename = os.path.basename(ARGS.sem_file)
    file_basename = file_basename.replace(".sem.xml", "")
    with open("tptp/" + file_basename + ".tptp", "w", encoding="utf-8") as z:
        for f in fols:
            z.write(f + "\n")

    tptp_script = " ".join(fols)
    ps = subprocess.Popen(("echo", tptp_script), stdout=subprocess.PIPE)
    try:
        timeout = "8"
        output = subprocess.check_output(
            (vampire_dir + "/vampire", "-t", timeout), # --mode casc?
            stdin=ps.stdout,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return False
    ps.wait()
    output_lines = [
        str(line).strip() for line in output.decode("utf-8").split("\n")
    ]
    return is_theorem_in_vampire(output_lines)


def theorem_proving(premises, conclusion, predicates):
    res = prove_vampire(premises, conclusion, predicates)
    if res:
        return "yes"
    else:
        negated_conclusion = NegatedExpression(conclusion)
        res = prove_vampire(premises, negated_conclusion, predicates)
        return "no" if res else "unknown"


if __name__ == "__main__":
    global ARGS
    file = open("./scripts/vampire_location.txt")
    vampire_dir = file.read().strip()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("sem_file")
    ARGS = arg_parser.parse_args()
    if not os.path.exists(ARGS.sem_file):
        print(f"File does not exist: {ARGS.sem_file}", file=sys.stderr)
        sys.exit(1)

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(ARGS.sem_file, parser)
    DOCS = root.findall(".//document")
    doc = DOCS[0]
    formulas = get_formulas_from_xml(doc)

    lexpr = Expression.fromstring

    lst = []
    predicates = []
    new_formulas = []
    for formula in formulas:
        if "--" in formula:
            formula = formula.replace("--", "")
        new_formulas.append(str(formula))
    for formula in new_formulas:
        preds = get_predicates(formula)
        for pred in preds:
            if pred not in predicates:
                predicates.append(pred)

    # >> add axioms
    # << add axioms

    formulas = [lexpr(formula) for formula in new_formulas]
    premises = formulas[:-1]
    conclusion = formulas[-1]
    start = time.time()
    prediction = theorem_proving(premises, conclusion, predicates)
    end = time.time()
    time_elapsed = end - start
    print(prediction)