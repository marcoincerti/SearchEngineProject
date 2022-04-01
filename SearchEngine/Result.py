

class Result:
    def __init__(self, result, query, terms):
        self._value = result
        self._query = query
        self._terms = terms

    def getValue(self):
        return self._value

    def getURL(self):
        return f'https://en.wikipedia.org/wiki/{self.title.replace(" ", "_")}'

    def getTitle(self) -> str:
        return self._value["title"]

    def getText(self):
        return self._value["text"]

    def getQuery(self):
        return str("[" + (str(self._query).replace("^", " with boost -> ")).replace("(", "").replace(")", "") + "]")

    def getID(self):
        return self._value["id"]

    def getTerms(self):
        return self._terms

