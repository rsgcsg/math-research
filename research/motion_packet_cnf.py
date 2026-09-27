"""Search-side encoding of a single invariant *partition*, not a joint law.

Each motion gets an independent, existential palette permutation. No relations
between permutations are assumed. Tautological clauses are removed to satisfy
the existing independent RUP checker's input contract.
"""
from itertools import combinations
import hashlib


def singleton_formula(n, edges, k, mappings):
    if type(n) is not int or n < 1 or type(k) is not int or not 2 <= k <= 10:
        raise ValueError('invalid dimensions')
    if n*k > 1000000:
        raise ValueError('search resource limit')
    clauses = []
    top = n*k
    palettes = []
    def color(v, c):
        return v*k+c+1
    def exact_one(row):
        clauses.append(list(row))
        clauses.extend([[-a, -b] for a, b in combinations(row, 2)])
    for v in range(n):
        exact_one([color(v,c) for c in range(k)])
    seen = set()
    for edge in edges:
        if (len(edge) != 2 or any(type(v) is not int for v in edge)
                or not 0 <= edge[0] < edge[1] < n or tuple(edge) in seen):
            raise ValueError('invalid edge')
        seen.add(tuple(edge))
        clauses.extend([[-color(edge[0], c), -color(edge[1], c)] for c in range(k)])
    for mapping in mappings:
        if (any(len(pair)!=2 or any(type(v) is not int or not 0<=v<n for v in pair)
                for pair in mapping) or len({a for a,b in mapping}) != len(mapping)
                or len({b for a,b in mapping}) != len(mapping)):
            raise ValueError('not a partial bijection')
        palette = [[top+1+c*k+d for d in range(k)] for c in range(k)]
        top += k*k
        palettes.append(palette)
        for row in palette + list(zip(*palette)):
            exact_one(row)
        for a,b in mapping:
            for c in range(k):
                for d in range(k):
                    clauses.append([-color(a,c), -palette[c][d], color(b,d)])
    # This removes only logical tautologies or duplicate occurrences, never
    # restricts the coloring space or silently changes a geometry obligation.
    clauses = [list(dict.fromkeys(c)) for c in clauses if not any(-x in c for x in c)]
    raw = ('p cnf %d %d\n' % (top, len(clauses)) +
           ''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode()
    return dict(nv=top, clauses=clauses, palettes=palettes,
                cnf_sha256=hashlib.sha256(raw).hexdigest())
