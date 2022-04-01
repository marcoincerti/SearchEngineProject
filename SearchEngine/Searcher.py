from functools import reduce
from whoosh import scoring
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.scoring import TF_IDF, BM25F
from whoosh.searching import Searcher as Whoosh_Searcher
import SearchEngine.Result as Result
import enchant


MODELS = {
    'bm25': scoring.BM25F,
    'pl2': scoring.PL2,
    'tf_idf': scoring.TF_IDF,
    'freq': scoring.Frequency,
    'mw': scoring.MultiWeighting
}


class Searcher:
    def __init__(self, index):
        self.index = index
        self.parser = MultifieldParser(["title", "content"], fieldboosts={'title': 3.0, 'content': 1.0},
                                       schema=self.index.schema)

        self.searcher = {
            'bm25': Whoosh_Searcher(reader=self.index.reader, weighting=scoring.BM25F),
            'pl2': Whoosh_Searcher(reader=self.index.reader, weighting=scoring.PL2),
            'tf_idf': Whoosh_Searcher(reader=self.index.reader, weighting=scoring.TF_IDF),
            'freq': Whoosh_Searcher(reader=self.index.reader, weighting=scoring.Frequency),
            'mw': Whoosh_Searcher(reader=self.index.reader, weighting=scoring.MultiWeighting(default=BM25F(), title=(), content=TF_IDF())),
        }

    def search(self, text):
        query = self.parser.parse(text)

        results = []
        max_query_result = 10

        model = MODELS['bm25']
        searcher = self.searcher['bm25']

        key_sort = lambda result: result.score

        try:
            results = []
            results = searcher.search(query, limit=max_query_result, terms=True)
            terms = results.matched_terms()

            # QUERY EXPANSION CON MORE LIKE THIS
            # first_hit = results[0]
            # more_result = first_hit.more_like_this("content")
            # results.upgrade_and_extend(more_result)

            # QUERY EXPANSION CON KEYWORD NEI PRIMI 10 DOCUMENTI
            keywords= [keyword for keyword, score
                        in results.key_terms("content", docs=3, numterms=5)]
            query_keyword = self.parser.parse((reduce(lambda a, b: a + ' ' + b, keywords)))
            results_keyword = searcher.search(query_keyword, limit=max_query_result, terms=True)
            results.upgrade_and_extend(results_keyword)

            results = sorted(results, key=key_sort, reverse=True) # NECESSARIA
            if len(results) >= 10:
                results_short = [results[x] for x in range(10)]
            else:
                results_short = [results[x] for x in range(len(results))]

            return [Result.Result(i, query, terms) for i in results_short]
        except Exception as e:
            print(e)
            return []

    def search_title(self, title):
        tmpparser = QueryParser("title", self.index.schema)
        searcher_tmp = Whoosh_Searcher(reader=self.index.reader, weighting=scoring.BM25F)
        query = tmpparser.parse(title)
        results = searcher_tmp.search(query, limit=1)
        return results[0]['content']

    @staticmethod
    def suggestion_word(query):
        chkr = enchant.Dict("en_US")
        return [word for word in chkr.suggest(query)]





