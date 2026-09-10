"""Center-aware five-color search: first Lambda states plus m-n modulo 3.

A positive target coloring extends to all of X. Target failure says nothing
about the chromatic number of X; ignoring the JLambda labels is an ansatz.
"""
from itertools import product
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def search(pair, budget, solver_name, output):
    from parts_core import clauses
    from pysat.solvers import Solver
    source = (ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()
    core_raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    data = json.loads(gzip.decompress(source))
    states = list(product(range(3), repeat=2)) if pair else [(q, 0) for q in range(3)]
    index = {v: i for i, v in enumerate(states)}
    def target(q, a, b):
        x, y = states[q]
        return index[((x+a) % 3, (y+b) % 3)] if pair else (q+a-b) % 3
    rows = list(data['contacts'])
    for a, b in product(range(-1, 2), repeat=2):
        if a*a+a*b+b*b == 1:
            rows.extend((i, i, a, b, 0, 0) for i in range(509))
    edges = sorted({tuple(sorted((509*q+i, 509*target(q, a, b)+j)))
                    for i, j, a, b, _, _ in rows for q in range(len(states))})
    n = 509*len(states)
    # Same core, first-Lambda triangle: (0,0), (1,0), (0,1).
    triangle = [0, target(0, 1, 0), target(0, 0, 1)]
    anchors = [[5*509*q+c+1] for c, q in enumerate(triangle)]
    print(dict(pair=pair, vertices=n, edges=len(edges)), flush=True)
    with Solver(name=solver_name, bootstrap_with=clauses(n, edges, 5)+anchors) as solver:
        core = json.loads(core_raw)['five_coloring']
        solver.set_phases([5*(509*q+i)+(core[i]+q) % 5+1 for q in range(len(states)) for i in range(509)])
        solver.conf_budget(budget)
        status = solver.solve_limited()
        print(dict(status=status, statistics=solver.accum_stats()), flush=True)
        if status is True:
            model = set(solver.get_model())
            word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(n))
            result = dict(schema=1, source_sha256=hashlib.sha256(source).hexdigest(),
                          core_sha256=hashlib.sha256(core_raw).hexdigest(),
                          parameter=dict(beta=[40, 169], first=7, second=3, denominator=13),
                          states=states, pair=pair, word=word, target_vertices=n,
                          target_edges=len(edges),
                          edge_sha256=hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest(),
                          coloring_formula=('(word[509*(3*(a%3)+b%3)+i]+(m-n)%3)%5' if pair else
                                            '(word[509*((a-b)%3)+i]+(m-n)%3)%5'),
                          solver=solver_name, conflict_budget=budget,
                          solver_statistics=solver.accum_stats(),
                          scope='Entire P+(7/13)Lambda+(3/13)JLambda+(2sqrt(10)/13)Lambda exactly five; not K^2+alphaLambda or the plane')
            if output:
                Path(output).write_text(json.dumps(result, separators=(',', ':'))+'\n')
            return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair', action='store_true')
    parser.add_argument('--budget', type=int, default=100000)
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--output')
    args = parser.parse_args()
    search(args.pair, args.budget, args.solver, args.output)
