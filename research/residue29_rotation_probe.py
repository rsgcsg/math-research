"""Bounded, explicitly restricted rotational models for the residue graph H29.

This is a producer, not a negative proof checker.  A SAT word can be checked
against all 353220 pairs independently; UNSAT/UNKNOWN says nothing about free
six-colorability.  No output file is written automatically.
"""
from itertools import combinations
import argparse
import json


def multiply(x, y):
    return ((x[0]*y[0]-3*x[1]*y[1]) % 29,
            (x[0]*y[1]+x[1]*y[0]) % 29)


def power(x, n):
    result = (1, 0)
    for _ in range(n):
        result = multiply(result, x)
    return result


def run(order, permutation, budget):
    from pysat.solvers import Solver
    p = 29
    colors = len(permutation)
    points = [(a, b) for a in range(p) for b in range(p)]
    ids = {point: i for i, point in enumerate(points)}
    directions = [v for v in points if (v[0]**2+3*v[1]**2) % p == 1]
    assert power((4, 13), 30) == (1, 0)
    generator = power((4, 13), 30 // order)
    assert power(generator, order) == (1, 0)
    assert all(power(generator, i) != (1, 0) for i in range(1, order))
    perm_powers = [list(range(colors))]
    for _ in range(order):
        perm_powers.append([permutation[c] for c in perm_powers[-1]])
    assert perm_powers[-1] == perm_powers[0]
    loc = {}
    orbits = []
    for i, point in enumerate(points):
        if i in loc:
            continue
        orbit = []
        v = point
        while ids[v] not in loc:
            loc[ids[v]] = (len(orbits), len(orbit))
            orbit.append(ids[v])
            v = multiply(v, generator)
        assert ids[v] == i
        orbits.append(orbit)
    edges = sorted({tuple(sorted((i, ids[((a+x) % p, (b+y) % p)])))
                    for i, (a, b) in enumerate(points) for x, y in directions})
    assert len(edges) == 12615

    def var(orbit, color):
        return colors*orbit+color+1

    clauses = set()
    for oi, orbit in enumerate(orbits):
        clauses.add(tuple(var(oi, c) for c in range(colors)))
        for c, d in combinations(range(colors), 2):
            clauses.add((-var(oi, d), -var(oi, c)))
        for c in range(colors):
            if perm_powers[len(orbit)][c] != c:
                clauses.add((-var(oi, c),))
    for i, j in edges:
        oi, pi = loc[i]
        oj, pj = loc[j]
        for c in range(colors):
            for d in range(colors):
                if perm_powers[pi][c] == perm_powers[pj][d]:
                    clauses.add(tuple(sorted({-var(oi, c), -var(oj, d)})))
    # Only a color-label gauge: origin must be a fixed color, and all fixed
    # colors are conjugate under the centralizer of the selected permutation.
    fixed = [c for c in range(colors) if permutation[c] == c]
    assert fixed
    clauses.add((var(0, fixed[0]),))
    with Solver(name='cadical195', bootstrap_with=sorted(clauses)) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        result = dict(status='SAT' if answer else
                      'UNSAT_RESTRICTED_UNCERTIFIED' if answer is False else 'UNKNOWN',
                      statistics=solver.accum_stats())
        if answer:
            model = set(solver.get_model())
            representatives = [next(c for c in range(colors) if var(oi, c) in model)
                               for oi in range(len(orbits))]
            word = [perm_powers[loc[i][1]][representatives[loc[i][0]]]
                    for i in range(len(points))]
            assert all(word[i] != word[j] for i, j in edges)
            result['word'] = word
    return dict(p=p, norm=[1, 3], rotation_order=order,
                generator=generator, permutation=permutation,
                orbits=len(orbits), clauses=len(clauses),
                conflict_budget=budget, result=result,
                scope='Restricted rotational ansatz only; no free negative claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--order', type=int, choices=(5, 6), required=True)
    parser.add_argument('--budget', type=int, default=30000)
    args = parser.parse_args()
    permutation = [1, 2, 3, 4, 0, 5] if args.order == 5 else [1, 2, 0, 4, 3, 5]
    print(json.dumps(run(args.order, permutation, args.budget), indent=2), flush=True)
