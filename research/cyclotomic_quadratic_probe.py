"""E040 bounded five-color probes, not lower-bound certificates.

B=F+Z*(48*sqrt(-7)/127). The exact new unit differences are
±1/127 ± 48*sqrt(-7)/127. At the old F11 reduction, ±1/127 maps to ±2.
Center periods constrain the coloring, not the original graph.
"""
from itertools import product
from pathlib import Path
import json


def target(period):
    def index(x, y, z):
        return ((z % period)*11+x % 11)*11+y % 11
    unit = [(a, b) for a, b in product(range(11), repeat=2) if (a*a+b*b) % 11 == 1]
    edges = set()
    for z, x, y in product(range(period), range(11), range(11)):
        i = index(x, y, z)
        for a, b in unit:
            edges.add(tuple(sorted((i, index(x+a, y+b, z)))))
        for a in (-2, 2):
            edges.add(tuple(sorted((i, index(x+a, y, z+1)))))
    return 121*period, sorted(edges)


def run():
    from pysat.solvers import Solver
    results = []
    for period, budget in ((2, 10000), (3, 100000), (11, 100000)):
        size, edges = target(period)
        clauses = [[5*i+c+1 for c in range(5)] for i in range(size)]
        clauses.extend([-5*i-c-1, -5*j-c-1] for i, j in edges for c in range(5))
        # An actual horizontal unit edge can have labels 0,1 without loss.
        clauses.extend([[1], [5*11+2]])
        with Solver(name='cadical195', bootstrap_with=clauses) as solver:
            solver.conf_budget(budget)
            answer = solver.solve_limited()
            record = dict(period=period, vertices=size, edges=len(edges), conflict_budget=budget,
                          status=('SAT_UNCHECKED' if answer else 'UNSAT_UNCERTIFIED')
                          if answer is not None else 'UNKNOWN', stats=solver.accum_stats())
            if answer:
                positive = {x for x in solver.get_model() if x > 0}
                record['word'] = [next(c for c in range(5) if 5*i+c+1 in positive) for i in range(size)]
            results.append(record)
            print(json.dumps(record), flush=True)
    return dict(experiment='E040', solver='cadical195', colors=5,
                scope='F11 core reduction with prescribed center period; not the source graph',
                cases=results)


if __name__ == '__main__':
    data = run()
    path = Path(__file__).resolve().parents[1]/'certificates/cyclotomic_quadratic_probe.json'
    path.write_text(json.dumps(data, indent=2)+'\n')
