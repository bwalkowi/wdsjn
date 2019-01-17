from functools import lru_cache


@lru_cache(maxsize=2**16)
def levenshtein_dist(a, b):
    if a == '':
        return len(b)
    elif b == '':
        return len(a)
    else:
        cost = 0 if a[-1] == b[-1] else 1
       
        return min(levenshtein_dist(a[:-1], b) + 1, 
                   levenshtein_dist(a, b[:-1]) + 1, 
                   levenshtein_dist(a[:-1], b[:-1]) + cost)
