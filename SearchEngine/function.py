# File con Variabili statice e funzioni
import math

size_query = 10
GO_IDCG = 14.8277  # google


def AVG(list_id_se, list_id_google):
    total_precision = 0
    hit = 0
    current_hit = 0
    for x in range(len(list_id_se)):
        if list_id_se[x] in list_id_google:
            hit += 1
            current_hit = 1
        if current_hit == 1:
            precision = round(hit / (x + 1), 2)
            total_precision += precision
        current_hit = 0
    if hit == 0:
        return 0
    return round(total_precision / hit, 3)


def ndgc_score(rel_list):
    res = 0
    for x in range(len(rel_list)):
        res += rel_list[x] / round((math.log((x + 1) + 1, 2)), 2)
    return round(res / GO_IDCG, 4)


def getKeyword(result, docs, word):
    keywords = [keyword for keyword, score in result.key_terms("content", docs=docs, numterms=word)]
    return keywords


def query_execute_keyword(searcher, parser, size_query, keyword, old_results):
    for word in keyword:
        word = word.lower()
        query = parser.parse(word)
        results = searcher.search(query, limit=size_query)
        old_results.upgrade_and_extend(results)
    return old_results

