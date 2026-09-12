"""Bounded producer for a conjugation-stable residue candidate; not a checker."""
from itertools import combinations
from pathlib import Path
import hashlib
import json


def graph():
    p = 29
    points = [(a, b) for a in range(p) for b in range(p)]
    ids = {v: i for i, v in enumerate(points)}
    directions = [(a, b) for a, b in points if (a*a+3*b*b) % p == 1]
    edges = sorted({tuple(sorted((i, ids[((a+x) % p, (b+y) % p)])))
                    for i, (a, b) in enumerate(points) for x, y in directions})
    return points, directions, edges


def run(k, budget=100000):
    from pysat.solvers import Solver
    points, directions, edges = graph()
    def var(v, c):
        return k*v+c+1
    cnf = [[var(v, c) for c in range(k)] for v in range(len(points))]
    cnf += [[-var(v, c), -var(v, d)] for v in range(len(points))
            for c, d in combinations(range(k), 2)]
    cnf += [[-var(v, c), -var(w, c)] for v, w in edges for c in range(k)]
    triangle = [0, 29, 15*29+15]
    assert all(tuple(sorted(pair)) in set(edges) for pair in combinations(triangle, 2))
    cnf += [[var(v, c)] for c, v in enumerate(triangle)]
    with Solver(name='cadical195', bootstrap_with=cnf) as solver:
        solver.conf_budget(budget)
        result = solver.solve_limited()
        record = dict(k=k, conflict_budget=budget,
                      status='SAT' if result else 'UNSAT_SEARCH_ONLY' if result is False else 'UNKNOWN',
                      statistics=solver.accum_stats())
        if result:
            model = set(solver.get_model())
            record['coloring'] = [next(c for c in range(k) if var(v, c) in model)
                                  for v in range(len(points))]
            assert all(record['coloring'][v] != record['coloring'][w] for v, w in edges)
    report = dict(field_order=29, norm_form=[1, 3], vertices=len(points),
                  directions=directions, edges=len(edges),
                  edge_sha256=hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest(),
                  result=record,
                  scope='Finite residue target only; negative search is not a source-field lower bound.')
    output = Path(__file__).resolve().parents[1]/'certificates'/f'cofinal_residue29_k{k}_probe.json'
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({**report, 'directions_count': len(directions)}, indent=2), flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--colors', type=int, default=6)
    parser.add_argument('--budget', type=int, default=100000)
    args = parser.parse_args()
    run(args.colors, args.budget)
