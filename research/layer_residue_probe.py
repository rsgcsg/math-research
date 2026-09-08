"""Bounded periodic finite-quotient probe, never an infinite negative proof."""
import json
from parts_core import clauses


def run():
    from pysat.solvers import Solver
    unit = [(x, y) for x in range(11) for y in range(11) if (x*x+y*y) % 11 == 1]
    results = []
    for period in (1, 2, 3, 4):
        index = lambda x, y, z: 121*(z % period)+11*(x % 11)+y % 11
        edges = set()
        for z in range(period):
            for x in range(11):
                for y in range(11):
                    v = index(x, y, z)
                    for dx, dy in unit:
                        edges.add(tuple(sorted((v, index(x+dx, y+dy, z)))))
                    for dx in (-2, 2):
                        edges.add(tuple(sorted((v, index(x+dx, y, z+1)))))
        with Solver(name='cadical195', bootstrap_with=clauses(121*period, sorted(edges), 5)) as solver:
            solver.conf_budget(10000)
            status = solver.solve_limited()
            record = dict(period=period, vertices=121*period, edges=len(edges), conflict_budget=10000,
                          status='UNKNOWN' if status is None else 'SAT' if status else 'UNSAT_UNCERTIFIED')
            if status:
                model = set(solver.get_model())
                colors = [next(c for c in range(5) if 5*v+c+1 in model) for v in range(121*period)]
                assert all(colors[a] != colors[b] for a, b in edges)
                record['search_coloring_requires_independent_check'] = colors
            results.append(record)
            print(json.dumps(record), flush=True)
    return results


if __name__ == '__main__':
    run()
