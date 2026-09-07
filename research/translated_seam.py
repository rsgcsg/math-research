"""Search a translated three-lattice joint relation, with exact finite ports.

A=Lambda, B=rho Lambda, C=Lambda+(rho-1)u, N(u)=3.
The A-C matching is satisfied globally by swapping the two color triples.
All remaining nontrivial contacts are the six roots at 0 and at u.
The proof of completeness is separate in docs/proofs/translated_seam.md.
"""
from itertools import permutations, product
from collections import Counter
from pathlib import Path
import argparse
import json

ROOTS = [(-2, 1), (-1, -1), (-1, 2), (1, -2), (1, 1), (2, -1)]


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def color(v, steps, lo):
    m, n = v
    return n % 3 if m % 2 == 0 else 3+(n+sum(steps[:m//2-lo])) % 3


def run(u):
    ports = sorted(set([(0, 0), u]+ROOTS+[plus(u, v) for v in ROOTS]))
    js = [m//2 for m, n in ports if m % 2]
    lo, hi = min(js), max(js)
    words = list(product((0, -1), repeat=hi-lo))
    frames_b = [(0,)+p for p in permutations(range(1, 6))]
    frames_c = [p+q for p in permutations(range(3, 6)) for q in permutations(range(3))]
    rows = []
    for wa, wb, wc in product(words, repeat=3):
        ca = {v: color(v, wa, lo) for v in ports}
        cb = {v: color(v, wb, lo) for v in ports}
        cc = {v: color(v, wc, lo) for v in ports}
        good = []
        for pb in frames_b:
            if any(ca[v] == pb[cb[v]] for v in ROOTS):
                continue
            for pc in frames_c:
                if pb[cb[u]] != pc[cc[u]]:
                    continue
                if any(pb[cb[plus(u, v)]] == pc[cc[plus(u, v)]] for v in ROOTS):
                    continue
                good.append((pb, pc))
        rows.append(dict(words=[wa, wb, wc], count=len(good),
                         witness=good[0] if good else None))
    return dict(translation_root=u, lo=lo, hi=hi, ports=ports,
                word_count=len(words), triples=len(rows),
                excluded=sum(row['count'] == 0 for row in rows),
                count_histogram=dict(Counter(row['count'] for row in rows)),
                rows=rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    results = [run(u) for u in ROOTS]
    if args.output:
        args.output.write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('ports', 'rows')}
                      for r in results], indent=2))
