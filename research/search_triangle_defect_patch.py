"""Search a finite obstruction to defects staying inside two fixed triples."""
import argparse
from itertools import combinations
from pathlib import Path
import json

from pysat.solvers import Solver
from phase_checks import DIRECTIONS


def radius(v):
    x, y = v
    return max(abs(x), abs(y), abs(x + y))


def make_cnf(r):
    points = sorted((a, b) for a in range(-r-1, r+2) for b in range(-r-1, r+2)
                    if radius((a, b)) <= r + 1)
    index = {v: i for i, v in enumerate(points)}
    def x(v, c):
        return index[v] * 6 + c + 1
    clauses = []
    for v in points:
        ns = [(v[0] + a, v[1] + b) for a, b in DIRECTIONS
              if (v[0] + a, v[1] + b) in index]
        clauses.append([x(v, c) for c in range(6)])
        clauses.extend([-x(v, a), -x(v, b)] for a, b in combinations(range(6), 2))
        for u in ns:
            if index[u] > index[v]:
                clauses.extend([-x(v, c), -x(u, c)] for c in range(6))
        if radius(v) <= r:
            assert len(ns) == 6
            for c in range(6):
                clauses.append([x(v, c)] + [x(u, c) for u in ns])
                for d in range(6):
                    if (c < 3) != (d < 3):
                        clauses.extend([-x(v, c), -x(a, d), -x(b, d)]
                                       for a, b in combinations(ns, 2))
    # Valid by permuting the two triples and then permuting within a triple.
    clauses.append([x((0, 0), 0)])
    return points, clauses


def run(r, output=None):
    points, clauses = make_cnf(r)
    with Solver(name='g4', bootstrap_with=clauses, with_proof=True) as solver:
        solver.conf_budget(200000)
        solved = solver.solve_limited()
        result = dict(radius=r, vertices=len(points), clauses=len(clauses),
                      status='SAT' if solved else ('UNSAT' if solved is False else 'UNKNOWN'),
                      stats=solver.accum_stats())
        if solved is False:
            proof = solver.get_proof()
            result['proof_lines'] = len(proof)
            if output:
                output.mkdir(parents=True, exist_ok=True)
                (output / 'triangle_defect.cnf').write_text(
                    f'p cnf {6 * len(points)} {len(clauses)}\n' +
                    ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in clauses))
                (output / 'triangle_defect.drat').write_text('\n'.join(proof) + '\n')
                (output / 'triangle_defect_input.json').write_text(json.dumps(
                    dict(radius=r, points=points, result=result), indent=2) + '\n')
        elif solved:
            model = {x for x in solver.get_model() if x > 0}
            result['coloring'] = [[*p, next(c for c in range(6) if 6*i+c+1 in model)]
                                  for i, p in enumerate(points)]
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--radius', type=int, default=2)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    print(json.dumps(run(a.radius, a.output), indent=2))
