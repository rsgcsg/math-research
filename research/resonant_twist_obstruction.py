"""Finite word relations for five-cycle transport along the missing direction.

Only a restricted coloring rule is in scope. The source graph can still be
five-colorable when this rule has no solution.
"""
from collections import defaultdict, deque
from itertools import product
from pathlib import Path
import argparse
import gzip
import hashlib
import json

from resonant_direction_extension import coordinates

ROOT = Path(__file__).resolve().parents[1]


def gain(shift, flip):
    a, b, n, d = coordinates(shift)
    return (4*(a % 2)+2*(b % 2)+d % 2) ^ (flip if n % 2 else 0), n % 5


def local_words(flip):
    forbidden = defaultdict(set)
    for a, b in product(range(-1, 2), repeat=2):
        if a*a+a*b+b*b != 1:
            continue
        for shift in ((a, b, 0, 0), (0, 0, a, b)):
            h, n = gain(shift, flip)
            for q in range(8):
                forbidden[q, q ^ h].add(n)
    normalized = []
    def extend(word):
        q = len(word)
        if q == 8:
            normalized.append(tuple(word))
            return
        if 0 in forbidden.get((q, q), ()):
            return
        for c in (range(5) if q else [0]):
            if all((old-c) % 5 not in forbidden.get((u, q), ()) for u, old in enumerate(word)):
                extend(word+[c])
    extend([])
    return normalized, [tuple((v+t) % 5 for v in word) for word in normalized for t in range(5)]


def relation_system(rows, flip, words):
    pairs = defaultdict(set)
    for i, j, *shift in rows:
        if i != j:
            pairs[i, j].add(gain(shift, flip))
    patterns = {}
    adjacency = [[] for _ in range(509)]
    for (i, j), pattern in sorted(pairs.items()):
        key = tuple(sorted(pattern))
        if key not in patterns:
            patterns[key] = [sum(1 << k for k, target in enumerate(words)
                                 if all(source[q] != (target[q ^ h]+n) % 5
                                        for h, n in key for q in range(8)))
                             for source in words]
        adjacency[i].append((j, patterns[key]))
    return adjacency


def propagate(adjacency, domains):
    queue = deque(range(len(domains)))
    pending = set(queue)
    steps = []
    while queue:
        v = queue.popleft()
        pending.remove(v)
        for u, supports in adjacency[v]:
            old = domains[v]
            removed = sum(1 << w for w, compatible in enumerate(supports)
                          if old & (1 << w) and not compatible & domains[u])
            if not removed:
                continue
            domains[v] ^= removed
            steps.append((v, u, removed))
            if not domains[v]:
                return False, steps
            for x, _ in adjacency[v]:
                if x not in pending:
                    pending.add(x)
                    queue.append(x)
    return True, steps


def explore():
    data = json.loads(gzip.decompress((ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()))
    for flip in range(8):
        normalized, words = local_words(flip)
        if not words:
            print(dict(flip=flip, local_words=0), flush=True)
            continue
        adjacency = relation_system(data['contacts'], flip, words)
        summary = []
        for k in range(len(normalized)):
            domains = [(1 << len(words))-1]*509
            domains[0] = 1 << (5*k)
            status, steps = propagate(adjacency, domains)
            summary.append((status, len(steps), sum(d.bit_count() for d in domains)))
        print(dict(flip=flip, local_words=len(words), branches=summary), flush=True)


def build():
    raw = (ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()
    data = json.loads(gzip.decompress(raw))
    selected = (0, 150, 153)
    rows = [r for r in data['contacts'] if r[0] in selected and r[1] in selected and r[0] < r[1]]
    assert len(rows) == 9
    cases = []
    for flip in range(8):
        normalized, words = local_words(flip)
        by_pair = defaultdict(set)
        for i, j, *shift in rows:
            by_pair[i, j].add(gain(shift, flip))
        def compatible(a, b, pair):
            return all(a[q] != (b[q ^ h]+n) % 5 for h, n in by_pair[pair] for q in range(8))
        triples = sum(compatible(a, b, (0, 150)) and compatible(a, c, (0, 153))
                      and compatible(b, c, (150, 153))
                      for a in normalized for b in words for c in words)
        assert triples == 0
        cases.append(dict(flip=flip, normalized_words=normalized,
                          normalized_triples=triples))
    return dict(schema=1, source_sha256=hashlib.sha256(raw).hexdigest(),
                core_labels=selected, listed_contacts=rows, cases=cases,
                three_color_formula='(base[i]+a-b-m+n)%3', base=[0, 2, 1],
                scope='Only five-cycle V transport with arbitrary eight parity words; the full triangle host is three-colorable')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.output:
        Path(args.output).write_text(json.dumps(build(), separators=(',', ':'))+'\n')
    else:
        explore()
