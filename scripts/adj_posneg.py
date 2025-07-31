from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader import CorpusReader
from nltk.corpus.reader.sentiwordnet import SentiSynset
import re

class TranslatedSentiWordNetCorpusReader(CorpusReader):
    def __init__(self, root, fileids, encoding="utf8", tagset=None):
        super().__init__(root, fileids, encoding, tagset)
        self._db = {}
        self._my_parse_src_file()

    def _my_parse_src_file(self):
        lines = self.open(self._fileids[0]).read().splitlines()
        lines = filter((lambda x: not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = [field.strip() for field in re.split(r"\t+", line)]
            try:
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except BaseException as e:
                raise ValueError(f"Line {i} formatted incorrectly: {line}\n") from e
            if pos and synset_terms:
                for term in synset_terms.split():
                    self._db[(pos, term)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):
        vals = tuple([vals[0], vals[1] + "#1"])
        if tuple(vals) in self._db:
            pos_score, neg_score = self._db[tuple(vals)]
            return SentiSynset(pos_score, neg_score, None)
        else:
            return None


sentiwordnet = LazyCorpusLoader(
    'sentiwordnet', TranslatedSentiWordNetCorpusReader, 'SentiWordNet_translated.dic', encoding='utf-8')

if __name__ == "__main__":
    print(sentiwordnet.senti_synset("a", "賢い").pos_score())