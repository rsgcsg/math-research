"""Bounded SAT discovery on a triangular torus; models are checked directly.

A torus is only a periodicity constraint. Its lift, not its drawing as a
finite Euclidean graph, is the object being certified.
"""
import argparse
from collections import Counter
from itertools import combinations
import json

from pysat.solvers import Solver
from phase_checks import DIRECTIONS


def search(width, height, opposite_only, conflicts, triangle_partners=False):
    n = width * height
    vertices = [(x, y) for y in range(height) for x in range(width)]
    index = {v: i for i, v in enumerate(vertices)}
    def shift(v, d):
        return ((v[0] + d[0]) % width, (v[1] + d[1]) % height)
    neighbors = {v: [shift(v, d) for d in DIRECTIONS] for v in vertices}
    assert all(len(set(ns)) == 6 for ns in neighbors.values())
    def x(v, c):
        return 6 * index[v] + c + 1
    clauses = []
    for v in vertices:
        clauses.append([x(v, c) for c in range(6)])
        clauses.extend([-x(v, a), -x(v, b)] for a, b in combinations(range(6), 2))
        for c in range(6):
            clauses.append([x(v, c)] + [x(u, c) for u in neighbors[v]])
            clauses.extend([-x(v, c), -x(u, c)] for u in neighbors[v])
        if opposite_only:
            for i in range(6):
                a, b = neighbors[v][i], neighbors[v][(i + 2) % 6]
                clauses.extend([-x(a, c), -x(b, c)] for c in range(6))
        if triangle_partners:
            for c in range(6):
                for other in range(6):
                    if (c < 3) != (other < 3):
                        clauses.extend([-x(v, c), -x(a, other), -x(b, other)]
                                       for a, b in combinations(neighbors[v], 2))
    root = (0, 0)
    clauses.append([x(root, 0)])
    # At least two neighbours of root have colour 1.
    ns = neighbors[root]
    for skip in range(6):
        clauses.append([x(u, 1) for j, u in enumerate(ns) if j != skip])
    # Some other colour-0 vertex must have a different repeated colour.
    witnesses = []
    for v in vertices[1:]:
        w = 6 * n + index[v] + 1
        witnesses.append(w)
        clauses.append([-w, x(v, 0)])
        clauses.extend([-w, -x(a, 1), -x(b, 1)] for a, b in combinations(neighbors[v], 2))
    clauses.append(witnesses)
    with Solver(name='g4', bootstrap_with=clauses) as solver:
        solver.conf_budget(conflicts)
        status = solver.solve_limited()
        result = dict(width=width, height=height, opposite_only=opposite_only,
                      triangle_partners=triangle_partners,
                      status='SAT' if status else ('UNSAT-search-only' if status is False else 'UNKNOWN'),
                      clauses=len(clauses), stats=solver.accum_stats())
        if status:
            model = {v for v in solver.get_model() if v > 0}
            colors = {v: next(c for c in range(6) if x(v, c) in model) for v in vertices}
            partners = {c: set() for c in range(6)}
            for v in vertices:
                counts = Counter(colors[u] for u in neighbors[v])
                assert set(counts) == set(range(6)) - {colors[v]}
                assert sorted(counts.values()) == [1, 1, 1, 1, 2]
                p = next(c for c, count in counts.items() if count == 2)
                partners[colors[v]].add(p)
                if triangle_partners:
                    assert (colors[v] < 3) == (p < 3)
                if opposite_only:
                    where = [i for i, u in enumerate(neighbors[v]) if colors[u] == p]
                    assert (where[0] - where[1]) % 6 == 3
            assert len(partners[0]) >= 2
            result['rows'] = [[colors[(x, y)] for x in range(width)] for y in range(height)]
            result['partners'] = {c: sorted(s) for c, s in partners.items()}
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type=int, default=6)
    parser.add_argument('--height', type=int, default=6)
    parser.add_argument('--opposite-only', action='store_true')
    parser.add_argument('--triangle-partners', action='store_true')
    parser.add_argument('--conflicts', type=int, default=100000)
    args = parser.parse_args()
    print(json.dumps(search(args.width, args.height, args.opposite_only, args.conflicts,
                            args.triangle_partners), indent=2))
