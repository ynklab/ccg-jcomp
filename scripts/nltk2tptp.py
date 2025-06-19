from nltk.sem.logic import *
from pykakasi import kakasi


kks = kakasi()


def convert_to_tptp_proof(formulas):
    if len(formulas) == 1:
        conjecture = convert_to_tptp(formulas[0])
        return [f"tff(h, conjecture, {conjecture})."]
    else:
        premises, conjecture = formulas[:-1], formulas[-1]
        tptp_script = []
        count = 1
        for formula in premises:
            formula = convert_to_tptp(formula)
            tptp_script.append(f"tff(t{count}, axiom, {formula}).")
            count += 1
        conjecture = convert_to_tptp(conjecture)
        tptp_script.append(f"tff(h, conjecture, {conjecture}).")
        return tptp_script


def convert_to_tptp(expression):
    return convert_tptp(expression)


def convert_tptp(expression):
    if isinstance(expression, ApplicationExpression):
        function, args = expression.uncurry()
        function_str = convert_tptp(function)
        args_str = ",".join(convert_tptp(arg) for arg in args)
        tptp_expr = function_str + "(" + args_str + ")"
        return tptp_expr
    elif isinstance(expression, EqualityExpression):
        lhs = convert_tptp(expression.first)
        rhs = convert_tptp(expression.second)
        tptp_str = "(" + lhs + " = " + rhs + ")"
        return tptp_str
    elif isinstance(expression, AndExpression):
        first = convert_tptp(expression.first)
        second = convert_tptp(expression.second)
        tptp_str = "(" + first + " & " + second + ")"
        return tptp_str
    elif isinstance(expression, OrExpression):
        first = convert_tptp(expression.first)
        second = convert_tptp(expression.second)
        tptp_str = "(" + first + " | " + second + ")"
        return tptp_str
    elif isinstance(expression, ImpExpression):
        first = convert_tptp(expression.first)
        second = convert_tptp(expression.second)
        tptp_str = "(" + first + " => " + second + ")"
        return tptp_str
    elif isinstance(expression, IffExpression):
        first = convert_tptp(expression.first)
        second = convert_tptp(expression.second)
        tptp_str = "(" + first + " <=> " + second + ")"
        return tptp_str
    elif isinstance(expression, NegatedExpression):
        term = convert_tptp(expression.term)
        tptp_str = "(" + "~" + term + ")"
        return tptp_str
    elif isinstance(expression, ExistsExpression):
        variable = convert_tptp(expression.variable).upper()
        term = convert_tptp(expression.term)
        if variable[0] == "D":
            tptp_str = "(" + "?[" + variable + ": $int]: " + term + ")"
        else:
            tptp_str = "(" + "?[" + variable + "]: " + term + ")"
        return tptp_str
    elif isinstance(expression, AllExpression):
        variable = convert_tptp(expression.variable).upper()
        term = convert_tptp(expression.term)
        if variable[0] == "D":
            tptp_str = "(" + "![" + variable + ": $int]: " + term + ")"
        else:
            tptp_str = "(" + "![" + variable + "]: " + term + ")"
        return tptp_str
    elif isinstance(expression, LambdaExpression):
        variable = convert_tptp(expression.variable).upper()
        term = convert_tptp(expression.term)
        tptp_str = "(" + "?[" + variable + "]: " + term + ")"
        return tptp_str
    elif isinstance(expression, IndividualVariableExpression):
        return str(expression.variable).upper()
    elif isinstance(expression, EventVariableExpression):
        return str(expression.variable).upper()
    elif isinstance(expression, FunctionVariableExpression):
        return str(expression.variable).upper()
    elif isinstance(expression, ConstantExpression):
        tptp_str = str(expression).lower()
        if tptp_str == "true":
            tptp_str = "$true"
        if tptp_str[0:2] == "__":
            tptp_str = tptp_str[2:]
        elif tptp_str[0] == "_":
            tptp_str = tptp_str[1:]
        else:
            pass
        tptp_str = "".join([d["hepburn"] for d in kks.convert(tptp_str)])
        # tptp_str = str(tptp_str.encode("utf8")).replace("\\", "").replace("\'", "")
        return tptp_str
    else:
        return str(expression)


if __name__ == "__main__":
    lexpr = Expression.fromstring
    f1 = "forall x. exists y. eat(x, y)"
    f2 = "exists y. exists x. eat(x, y)"
    tptp_script = convert_to_tptp_proof([lexpr(f) for f in [f1, f2]])
    print(tptp_script)