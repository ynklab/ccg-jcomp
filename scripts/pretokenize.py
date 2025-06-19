from janome.tokenizer import Tokenizer, Token
from janome.tokenfilter import *
from janome.analyzer import Analyzer
import argparse


# class SentencelikeAdjectiveFilter(TokenFilter):
#     def apply(self, tokens):
#         waiting = []
#         for token in tokens:
#             if token.surface == "背":
#                 waiting.append(token)
#             elif token.surface == "が":
#                 if len(waiting) > 0 and waiting[0].surface == "背":
#                     waiting.append(token)
#                 else:
#                     for t in waiting:
#                         yield t
#                     waiting = []
#                     yield token
#             elif token.base_form == "高い" or token.base_form == "低い":
#                 if len(waiting) > 1 and waiting[0].surface == "背" \
#                     and waiting[1].surface == "が":
#                     waiting[0].surface += waiting[1].surface + token.surface
#                     waiting[0].base_form += waiting[1].base_form + token.base_form
#                     waiting[0].reading += waiting[1].reading + token.reading
#                     waiting[0].phonetic += waiting[1].phonetic + token.phonetic
#                     waiting[0].infl_type = token.infl_type
#                     waiting[0].infl_form = token.infl_form
#                     waiting[0].part_of_speech = "形容詞,自立,*,*"
#                     yield waiting[0]
#                     waiting = []
#                 else:
#                     for t in waiting:
#                         yield t
#                     waiting = []
#                     yield token
#             else:
#                 for t in waiting:
#                     yield t
#                 waiting = []
#                 yield token
#         for t in waiting:
#             yield t


class NominalAdjectiveFilter(TokenFilter):
    def __init__(self):
        super().__init__()
        self.targets = [
            "早起き",
            "裕福"
        ]

    def apply(self, tokens):
        waiting = []
        for token in tokens:
            if token.base_form in self.targets:
                waiting.append(token)
            elif token.base_form != "する":
                if len(waiting) > 0 and waiting[0].base_form in self.targets:
                    waiting[0].part_of_speech = "名詞,形容動詞語幹,*,*"
                    yield waiting[0]
                    yield token
                    waiting = []
                else:
                    for t in waiting:
                        yield t
                    waiting = []
                    yield token
            else:
                for t in waiting:
                    yield t
                yield token
        for t in waiting:
            yield t


class ConcatFilter(TokenFilter):
    def __init__(self):
        super().__init__()
        self.cwords = [
            ["背", "が", "高い"],
            ["背", "が", "低い"],
            ["という", "わけ", "で", "は", "ない"],
            ["かも", "しれ", "ない"],
            ["で", "ない"]
        ]

    def concat_adj(self, tokens):
        for i in range(len(tokens) - 1):
            tokens[0].surface += tokens[i+1].surface
            tokens[0].base_form += tokens[i+1].base_form
            tokens[0].reading += tokens[i+1].reading
            tokens[0].phonetic += tokens[i+1].phonetic
        tokens[0].infl_type = tokens[len(tokens)-1].infl_type
        tokens[0].infl_form = tokens[len(tokens)-1].infl_form
        tokens[0].part_of_speech = "形容詞,自立,*,*"
        return tokens[0]

    def concat_aux(self, tokens):
        for i in range(len(tokens) - 1):
            tokens[0].surface += tokens[i+1].surface
            if tokens[i+1].base_form == "しれる":
                tokens[0].base_form += "しれ"
            else:
                tokens[0].base_form += tokens[i+1].base_form
            tokens[0].reading += tokens[i+1].reading
            tokens[0].phonetic += tokens[i+1].phonetic
        tokens[0].infl_type = tokens[len(tokens)-1].infl_type
        tokens[0].infl_form = tokens[len(tokens)-1].infl_form
        tokens[0].part_of_speech = "助動詞,*,*,*"
        return tokens[0]

    def apply(self, tokens):
        waiting = []
        phrase_ids = []
        word_ids = []
        for token in tokens:
            if len(phrase_ids) == 0:
                appended = False
                for i in range(len(self.cwords)):
                    if token.surface == self.cwords[i][0]:
                        if not appended:
                            waiting.append(token)
                            appended = True
                        phrase_ids.append(i)
                        word_ids.append(0)
                if not appended:
                    yield token
            else:
                appended = False
                for i in range(len(phrase_ids)):
                    if token.surface == self.cwords[phrase_ids[i]][word_ids[i]+1]:
                        if not appended:
                            waiting.append(token)
                            appended = True
                        word_ids[i] += 1
                        if word_ids[i] == len(self.cwords[phrase_ids[i]]) - 1:
                            if phrase_ids[i] in [0, 1]:
                                new_token = self.concat_adj(waiting)
                            elif phrase_ids[i] in [2, 3, 4]:
                                new_token = self.concat_aux(waiting)
                            yield new_token
                            waiting = []
                            phrase_ids = []
                            word_ids = []
                            break
                if not appended:
                    for t in waiting:
                        yield t
                    yield token
                    waiting = []
                    phrase_ids = []
                    word_ids = []
        for t in waiting:
            yield t


def pretokenize_sentence(sentence):
    token_filters = [NominalAdjectiveFilter(),
                     ConcatFilter()]
    tokenizer = Tokenizer()
    analyzer = Analyzer(tokenizer=tokenizer, token_filters=token_filters)
    tokens = analyzer.analyze(sentence)
    return tokens


def pretokenize_file(file_name):
    res = []
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            res.append(pretokenize_sentence(line))
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("--token-output",
                        required=True)
    parser.add_argument("--tag-output",
                        required=True)
    args = parser.parse_args()

    tagged_sentences = pretokenize_file(args.file_name)
    with open(args.token_output, "w", encoding="utf-8") as f_token, \
         open(args.tag_output, "w", encoding="utf-8") as f_tag:
        for sentence in tagged_sentences:
            for token in sentence:
                f_token.write(token.surface + " ")
                f_tag.write(str(token) + "\n")
            f_token.write("\n")