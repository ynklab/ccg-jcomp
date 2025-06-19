import argparse
import os
import sys
import subprocess
import time
from multiprocessing import Pool
import xml.etree.ElementTree as ET
from nltk.sem.logic import *
from pykakasi import kakasi
from vampire_axioms_v2 import vampire_axioms
from nltk2tptp import convert_to_tptp_proof


kks = kakasi()
lexpr = Expression.fromstring


def get_formulas(doc):
    semantics = doc.findall(".//sentence/semantics")
    formulas = [semantic.find("span").get("sem") for semantic in semantics]
    return formulas


def get_predicates(formula):
    def get_predicate_set(expression):
        if isinstance(expression, ApplicationExpression):
            function, args = expression.uncurry()
            preds = set()
            for arg in args:
                preds |= get_predicate_set(arg)
            function_str = str(function)
            if function_str[0] == "_":
                preds |= set([str(function)[1:]])
            else:
                preds |= set([str(function)])
            return preds
        elif isinstance(expression, EqualityExpression) \
             or isinstance(expression, AndExpression) \
             or isinstance(expression, OrExpression) \
             or isinstance(expression, ImpExpression) \
             or isinstance(expression, IffExpression):
            lhs = get_predicate_set(expression.first)
            rhs = get_predicate_set(expression.second)
            return lhs | rhs
        elif isinstance(expression, NegatedExpression) \
             or isinstance(expression, ExistsExpression) \
             or isinstance(expression, AllExpression) \
             or isinstance(expression, LambdaExpression):
            return get_predicate_set(expression.term)
        else:
            return set()
    
    return list(get_predicate_set(lexpr(formula)))


def get_types(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    adjlst =[]
    negadjlst =[]
    objlst = []
    vrblst = []

    for token in root.iter("token"):
        if token.attrib["pos"] == "形容詞" \
           or token.attrib["pos1"] == "形容動詞語幹":
            if token.attrib["entity"] == "NEG":
                negadjlst.append(token.attrib["base"])
            else:
                adjlst.append(token.attrib["base"])
        elif token.attrib["pos"] == "名詞":
            objlst.append(token.attrib["base"])
        elif token.attrib["pos"] == "動詞":
            vrblst.append(token.attrib["base"])

    return list(set(adjlst)), list(set(negadjlst)), list(set(objlst)), list(set(vrblst))


def is_theorem_in_vampire(lines):
    if lines:
        return ("% Refutation found. Thanks to Tanya!" in lines)
    else:
        return False


def prove_vampire(premises, conclusion, predicates, negated, mode=None):
    adjlst, negadjlst, objlst, vrblst = get_types(ARGS.sem_file.replace(".sem.xml", ".jigg.xml"))
    types, axioms = vampire_axioms(adjlst, negadjlst, predicates)
    axioms.append(lexpr("forall x y. ((x = y) => exists e.((Nom(e) = x) & (Nom(e) = y)))"))

    premises = axioms + premises
    premises.append(conclusion)
    fols = convert_to_tptp_proof(premises)

    type_f = []
    type_f_adj = types

    for pred in predicates:
        if pred in adjlst:
            adj = "".join([d["hepburn"] for d in kks.convert(pred)])
            # adj = str(adj.encode("utf8")).replace("\\", "").replace("\'", "")
            adj_type = "tff(" + adj + "_type, type, " + adj + ": $i * $int > $o)."
            type_f_adj.append(adj_type)
        elif pred in negadjlst:
            adj = "".join([d["hepburn"] for d in kks.convert(pred)])
            # adj = str(adj.encode("utf8")).replace("\\", "").replace("\'", "")
            adj_type = "tff(" + adj + "_type, type, " + adj + ": $i * $int > $o)."
            type_f_adj.append(adj_type)
        elif pred == "many":
            adj_type = "tff(many_type, type, many: $i * $int > $o)."
            type_f_adj.append(adj_type)
        elif pred in objlst:
            obj = "".join([d["hepburn"] for d in kks.convert(pred)]).lower()
            # obj = str(obj.encode("utf8")).replace("\\", "").replace("\'", "")
            obj_type = "tff(" + obj + "_type, type, " + obj + ": $i > $o)."
            type_f.append(obj_type)
        elif pred in vrblst:
            vrb = "".join([d["hepburn"] for d in kks.convert(pred)])
            # vrb = str(vrb.encode("utf8")).replace("\\", "").replace("\'", "")
            vrb_type = "tff(" + vrb + "_type, type, " + vrb + ": $i > $o)."
            type_f.append(vrb_type)
        elif pred == "Acc":
            type_f.append("tff(acc_type, type, acc: $i > $i)." )
        elif pred == "Nom":
            type_f.append("tff(nom_type, type, nom: $i > $i)." )
        elif pred == "Past":
            type_f.append("tff(past_type, type, past: $i > $o).")
        elif pred == "$dia":
            type_f.append("tff(dia_type, type, $dia: $o > $o).")

    type_f.append("tff(th_type, type, th: $int).")
    type_f.append("tff(d0_type, type, d0: $int).")

    fols = type_f + type_f_adj + fols

    file_basename = os.path.basename(ARGS.sem_file)
    file_basename = file_basename.replace(".sem.xml", "")
    tptp_filename = "tptp/" + file_basename + ".tptp" if not negated else "tptp/" + file_basename + "_neg.tptp"
    with open(tptp_filename, "w", encoding="utf-8") as z:
        for f in fols:
            z.write(f + "\n")

    tptp_script = " ".join(fols)
    ps = subprocess.Popen(("echo", tptp_script), stdout=subprocess.PIPE)
    try:
        if not mode is None:
            timeout = "20"
            output = subprocess.check_output(
                (vampire_dir + "/vampire", "-t", timeout, "--mode", mode),
                stdin=ps.stdout,
                stderr=subprocess.STDOUT
            )
        else:
            timeout = "20"
            output = subprocess.check_output(
                (vampire_dir + "/vampire", "-t", timeout),
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
    res = prove_vampire(premises, conclusion, predicates, False, "casc")
    if res:
        return "yes"
    else:
        negated_conclusion = NegatedExpression(conclusion)
        res = prove_vampire(premises, negated_conclusion, predicates, True, "casc")
        if res:
            return "no"
        else:
            res = prove_vampire(premises, conclusion, predicates, False)
            if res:
                return "yes"
            else:
                res = prove_vampire(premises, negated_conclusion, predicates, True)
                return "no" if res else "unknown"


def multi_theorem_proving(premises, conclusion, predicates):
    negated_conclusion = NegatedExpression(conclusion)
    p = Pool()
    res_yes = p.apply_async(prove_vampire, args=[premises, conclusion, predicates, False, "casc"])
    res_no = p.apply_async(prove_vampire, args=[premises, negated_conclusion, predicates, True, "casc"])
    while True:
        if res_yes.ready():
            p.terminate()
            p.join()
            break
        elif res_no.ready():
            p.terminate()
            p.join()
            break
        time.sleep(1)
    if res_yes.ready() and res_yes.get():
        return "yes"
    elif res_no.ready() and res_no.get():
        return "no"
    else:
        p = Pool()
        res_yes = p.apply_async(prove_vampire, args=[premises, conclusion, predicates, False])
        res_no = p.apply_async(prove_vampire, args=[premises, negated_conclusion, predicates, True])
        while True:
            if res_yes.ready():
                p.terminate()
                p.join()
                break
            elif res_no.ready():
                p.terminate()
                p.join()
                break
            time.sleep(1)
        if res_yes.ready() and res_yes.get():
            return "yes"
        elif res_no.ready() and res_no.get():
            return "no"
        else:
            return "unknown"

        
    

if __name__ == "__main__":
    global ARGS
    with open("./scripts/vampire_location.txt", "r") as f:
        vampire_dir = f.read().strip()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("sem_file")
    ARGS = arg_parser.parse_args()
    if not os.path.exists(ARGS.sem_file):
        print(f"File does not exist: {ARGS.sem_file}", file=sys.stderr)
        sys.exit(1)

    tree = ET.parse(ARGS.sem_file)
    root = tree.getroot()
    doc = root.find("./document")
    try:
        formulas = get_formulas(doc)
    except Exception:
        print("unknown")
        exit(0)
    formulas_split = []
    for i in range(len(formulas) - 1):
        try:
            formula_lexpr = lexpr(formulas[i])
            term = formula_lexpr.term
            function, args = term.uncurry()
        except Exception:
            print("unknown")
            exit(0)
        for arg in args:
            formulas_split.append(str(arg))
    hypo_lexpr = lexpr(formulas[-1])
    term = hypo_lexpr.term
    function, args = term.uncurry()
    formulas_split.append(str(args[0]) + " & " + str(args[1]))

    new_formulas = []
    predicates = []
    for formula in formulas_split:
        formula = formula.replace("--", "")
        new_formulas.append(formula)
    for formula in new_formulas:
        preds = get_predicates(formula)
        predicates += preds
    predicates = list(set(predicates))

    formulas = [lexpr(formula) for formula in new_formulas]
    premises = formulas[:-1]
    conclusion = formulas[-1]
    # prediction = theorem_proving(premises, conclusion, predicates)
    prediction = multi_theorem_proving(premises, conclusion, predicates)
    print(prediction)