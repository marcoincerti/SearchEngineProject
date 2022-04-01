from nltk.stem import WordNetLemmatizer
from whoosh.analysis import Filter, SubstitutionFilter, RegexTokenizer
from nltk.corpus import stopwords
from whoosh.analysis import StemmingAnalyzer
from whoosh.support.charset import accent_map
from whoosh.analysis.filters import CharsetFilter

Custom_StopWord = frozenset(stopwords.words('english'))

# NOT USED
class CustomLemmatizer(Filter):
    def __call__(self, tokens):
        for token in tokens:
            token.text = WordNetLemmatizer().lemmatize(token.text)
            yield token


class CustomNormalizer(Filter):
    def __call__(self, tokens):
        filtri = SubstitutionFilter("-", " ") | SubstitutionFilter("_", " ")
        return filtri(tokens)


def CustomAnalyzer(stopword_list=Custom_StopWord):
    stemming_charset = StemmingAnalyzer() \
                       | CharsetFilter(accent_map)
    myanalizer = stemming_charset | CustomNormalizer()
    return myanalizer


def LemmatizerAnalizer():
    return RegexTokenizer() | CustomLemmatizer()