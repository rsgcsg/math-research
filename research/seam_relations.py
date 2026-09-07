"""Exact bounded seam experiment for the binary column family.

Two radius-R triangular patches share their origin; the second is rotated by
(5+i*sqrt(11))/6. Enumerates all binary increment words visible on the patches
and all relative palette permutations fixing the common-origin color.
This is a restricted-family relation, never the whole 6-coloring relation.
"""
from collections import Counter
from itertools import permutations, product
from fractions import Fraction as F
from pathlib import Path
import argparse
import json

from exact_geometry import field, cmul, distance_squared, ONE


def patch(r):
    return sorted((m, n) for m in range(-r, r+1) for n in range(-r, r+1)
                  if max(abs(m), abs(n), abs(m+n)) <= r)


def point(v):
    m, n = v
    return field(F(2*m+n, 2)), field(0, F(n, 2))


def words(points):
    js = sorted({m//2 for m, n in points if m % 2})
    lo, hi = min(js), max(js)
    for steps in product((0, -1), repeat=hi-lo):
        s = {lo: 0}
        for j, d in zip(range(lo+1, hi+1), steps):
            s[j] = (s[j-1] + d) % 3
        colors = [n % 3 if m % 2 == 0 else 3 + (n+s[m//2]) % 3 for m, n in points]
        yield dict(steps=list(steps), colors=colors)


def run(r):
    points = patch(r)
    physical = list(map(point, points))
    rho = field(F(5, 6)), field(0, 0, F(1, 6))
    rotated = [cmul(rho, x) for x in physical]
    coincidences = [(i, j) for i, a in enumerate(physical) for j, b in enumerate(rotated) if a == b]
    zero = points.index((0, 0))
    assert coincidences == [(zero, zero)]
    cross = [(i, j) for i, a in enumerate(physical) for j, b in enumerate(rotated)
             if distance_squared(a, b) == ONE]
    states = list(words(points))
    palette_maps = [(0,)+p for p in permutations(range(1, 6))]
    counts = []
    for a in states:
        row = []
        for b in states:
            good = [p for p in palette_maps
                    if all(a['colors'][i] != p[b['colors'][j]] for i, j in cross)]
            row.append(len(good))
        counts.append(row)
    return dict(radius=r, vertices_per_patch=len(points), coordinates='axial Q(sqrt(3))',
                rotation='(5+i*sqrt(11))/6', points=points,
                cross_edges=cross, coincident_pairs=coincidences,
                words=[a['steps'] for a in states],
                allowed_relative_permutation_counts=counts,
                state_pairs=len(states)**2,
                excluded_state_pairs=sum(n == 0 for row in counts for n in row),
                allowed_permutation_count_histogram=dict(Counter(n for row in counts for n in row)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--radius', type=int, default=3)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = run(args.radius)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('points', 'cross_edges', 'coincident_pairs', 'words',
                                   'allowed_relative_permutation_counts')}, indent=2))
