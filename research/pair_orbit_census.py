"""Rebuild the historical five-pair census; output explicit proof objects.

Search is not verification: verify_pair_orbits.py independently rebuilds every
graph and checks every positive word / negative geometric witness.
"""
import gzip
import json
from itertools import combinations
from pathlib import Path

PAIRS = list(combinations(range(5), 2))
LISTS = (([1, 2, 3],)*3 + ([0, 2, 3],)*2,
         ([1, 2, 3],)*3 + ([0, 2, 3],) + ([0, 1, 3],),
         ([1, 2, 3],)*2 + ([0, 2, 3],)*2 + ([0, 1, 3],),
         ([1, 2, 3],)*2 + ([0, 2, 3],) + ([0, 1, 3],) + ([0, 1, 2],))


def graph(code):
    adj = [set() for _ in range(10)]
    for i, j in PAIRS:
        code, digit = divmod(code, 3)
        if digit:
            for sign in (0, 1):
                u, v = 2*i+sign, 2*j+(sign ^ (digit-1))
                adj[u].add(v)
                adj[v].add(u)
    return adj


def color(adj, lists):
    word = [-1]*10
    def visit(left):
        if not left:
            return word[:]
        choices = [(set(lists[v//2]) - {word[u] for u in adj[v]}, v) for v in left]
        allowed, v = min(choices, key=lambda p: (len(p[0]), -len(adj[p[1]]), p[1]))
        for c in sorted(allowed):
            word[v] = c
            found = visit(left - {v})
            if found is not None:
                return found
        word[v] = -1
        return None
    return visit(set(range(10)))


def cycle_square(adj):
    # C10^2: the next vertex must neighbor the previous two; exact wrap checked.
    def visit(path):
        if len(path) == 10:
            if all(((j-i) % 10 in (1, 2, 8, 9)) == (path[j] in adj[path[i]])
                   for i in range(10) for j in range(10) if i != j):
                return path
            return None
        candidates = adj[path[-1]] - set(path)
        if len(path) >= 2:
            candidates &= adj[path[-2]]
        for v in sorted(candidates):
            result = visit(path+[v])
            if result is not None:
                return result
        return None
    return visit([0])


def build():
    records = []
    counts = dict(k23=0, k4=0, rhombus=0, positive=0)
    for code in range(3**10):
        adj = graph(code)
        forbidden = next(([a, b]+sorted(adj[a] & adj[b])[:3]
                          for a, b in combinations(range(10), 2)
                          if len(adj[a] & adj[b]) >= 3), None)
        if forbidden is not None:
            records.append(['k23', forbidden])
            counts['k23'] += 1
            continue
        clique = next((list(vs) for vs in combinations(range(10), 4)
                       if all(b in adj[a] for a, b in combinations(vs, 2))), None)
        if clique is not None:
            records.append(['k4', clique])
            counts['k4'] += 1
            continue
        word = color(adj, ([0, 1, 2],)*5)
        if word is None:
            cycle = cycle_square(adj)
            assert cycle is not None, ('UNCLASSIFIED', code)
            records.append(['rhombus', cycle])
            counts['rhombus'] += 1
            continue
        words = [word] + [color(adj, pattern) for pattern in LISTS]
        assert all(w is not None for w in words), ('BAD_NONUNIFORM_LIST', code)
        records.append(['positive', [''.join(map(str, w)) for w in words]])
        counts['positive'] += 1
    return dict(schema=1, pair_count=5, ordering='lex pairs, little-endian ternary; 1 straight, 2 crossed',
                counts=counts, records=records,
                scope='Anchored complete two-point real Galois orbits; base contains sqrt(3).',
                historical_source='HN_mature_framework_reducibility_and_finite_cases_2026-09-07.md',
                original_certificate_recovered=False)


if __name__ == '__main__':
    result = build()
    target = Path(__file__).resolve().parents[1]/'certificates/pair_orbits_five.json.gz'
    target.write_bytes(gzip.compress(json.dumps(result, separators=(',', ':')).encode(), mtime=0))
    print(json.dumps(result['counts'], indent=2))
