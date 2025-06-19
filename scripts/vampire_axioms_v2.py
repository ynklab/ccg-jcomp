from nltk.sem import Expression
from pykakasi import kakasi
from antonym import search_antonym

lexpr = Expression.fromstring
kks = kakasi()

def vampire_axioms(adjlst, negadjlst, predicates):
    types = []
    axioms = []
    for pred in predicates:
        if pred in adjlst:
            adj = "".join([d["hepburn"] for d in kks.convert(pred)])
            ax1 = lexpr("all x y. ((exists d. (" + adj + "(x, d) & -" + adj + "(y, d))) -> (all d. (" + adj + "(y, d) -> " + adj + "(x, d))))")
            ax2 = lexpr("all x d. (" + adj + "(x, d) => all d1. ($lesseq(d1, d) => " + adj + "(x, d1)))")
            ax3 = lexpr("all x. (" + adj + "(x, $difference(_th, _d0)) <=> " + adj + "(x, $sum(_th, _d0)))")
            axioms.append(ax1)
            axioms.append(ax2)
            axioms.append(ax3)
            antonyms = search_antonym(pred)
            for antonym in antonyms:
                antonym_conv = "".join([d["hepburn"] for d in kks.convert(antonym)])
                ax2 = lexpr("all x d. (" + adj + "(x, d) <-> -" + antonym_conv + "(x, d))")
                axioms.append(ax2)
                if not antonym in predicates:
                    types.append("tff(" + antonym_conv + "_type, type, " + antonym_conv + ": $i * $int > $o).")
        elif pred in negadjlst:
            adj = "".join([d["hepburn"] for d in kks.convert(pred)])
            ax1 = lexpr("all x y. ((exists d. (" + adj + "(x, d) & -" + adj + "(y, d))) -> (all d. (" + adj + "(y, d) -> " + adj + "(x, d))))")
            ax2 = lexpr("all x d. (" + adj + "(x, d) => all d1. ($lesseq(d, d1) => " + adj + "(x, d1)))")
            ax3 = lexpr("all x. (" + adj + "(x, $difference(_th, _d0)) <=> " + adj + "(x, $sum(_th, _d0)))")
            axioms.append(ax1)
            axioms.append(ax2)
            axioms.append(ax3)
            antonyms = search_antonym(pred)
            for antonym in antonyms:
                antonym_conv = "".join([d["hepburn"] for d in kks.convert(antonym)])
                ax2 = lexpr("all x d. (" + adj + "(x, d) <-> -" + antonym_conv + "(x, d))")
                axioms.append(ax2)
                if not antonym in predicates:
                    types.append("tff(" + antonym_conv + "_type, type, " + antonym_conv + ": $i * $int > $o).")
        elif pred == "many":
            ax1 = lexpr("all x y. ((exists d. (many(x, d) & -many(y, d))) -> (all d. (many(y, d) -> many(x, d))))")
            ax2 = lexpr("forall x d. (many(x, d) => forall d1. ($lesseq(d1, d) => many(x, d1)))")
            axioms.append(ax1)
            axioms.append(ax2)
    return types, axioms

# def vampire_axioms(adjlst, predicates):
#     types = []
#     axioms = []
#     for pred in predicates:
#         if pred[0][0] == "_":
#             pred[0] = pred[0][1:]

#         if pred[0] in adjlst:
#             adj = "".join([d["hepburn"] for d in kks.convert(pred[0])])
#             # adj = str(pred[0].encode("utf8")).replace("\\", "").replace("\'", "")
#             ax1 = lexpr("all x y. ((exists d. (" + adj + "(x, d) & -" + adj + "(y, d))) -> (all d. (" + adj + "(y, d) -> " + adj + "(x, d))))")
#             axioms.append(ax1)

#             antonyms = search_antonym(pred[0])
#             for antonym in antonyms:
#                 antonym = "".join([d["hepburn"] for d in kks.convert(antonym)])
#                 ax2 = lexpr("all x d. (" + adj + "(x, d) <-> -" + antonym + "(x, d))")
#                 types.append("tff(" + antonym + "_type, type, " + antonym + ": $i * $int > $o).")
#                 axioms.append(ax2)
#     ax = lexpr("all x y. ((exists d. (many(x, d) & -many(y, d))) -> (all d. (many(y, d) -> many(x, d))))")
#     axioms.append(ax)
#     return types, axioms