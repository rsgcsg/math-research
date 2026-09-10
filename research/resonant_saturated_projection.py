"""Probe X + Lambda: saturate 7/13 Lambda to 1/13 Lambda.

This is a center-separable quotient search, not a lower-bound search.
Coincident core/state labels are merged before solving. Negative returns are
not certificates and cannot be transferred to the actual infinite host.
"""
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import math

from verify_contact_translation_closure import multiplication, squared_distance

ROOT = Path(__file__).resolve().parents[1]
RAD = (1, 3, 11, 33, 5, 15, 55, 165)
DEN = 1248


@lru_cache(None)
def sphere(total, rx, rw):
    if total < 0:
        return ()
    bound = math.isqrt(total)
    left = {}
    for x in range(-bound, bound+1):
        if (x-rx) % 48:
            continue
        for y in range(-bound//144, bound//144+1):
            value = x*x+3*(144*y)**2
            if value <= total:
                left.setdefault(value, []).append((x, 144*y))
    found = []
    for z in range(-bound//144, bound//144+1):
        for w in range(-bound, bound+1):
            if (w-rw) % 48:
                continue
            for x, y in left.get(total-(144*z)**2-3*w*w, ()):
                if (x-rx-w+rw) % 96 == 0 and (144*z+y) % 288 == 0:
                    found.append((x, y, 144*z, w))
    return tuple(found)


def compile_target(core):
    table = multiplication(RAD)
    zero = ([0]*8, [0]*8)
    parent = list(range(1527))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(i, j):
        parent[find(j)] = find(i)
    edges, coincidences, rows = set(), set(), []
    for i, p in enumerate(core['points']):
        for j, q in enumerate(core['points']):
            delta = tuple(tuple(13*(b-a) for a, b in zip(ax, bx)) for ax, bx in zip(p, q))
            assert delta[0][1] == delta[1][0] == 0
            fixed = sum(r*v*v for ax in delta for r, v in zip(RAD[2:], ax[2:]))
            # Zero displacements in the enlarged lattice need label merging.
            if fixed == 0 and delta[1][1] % 48 == 0 and (delta[0][0]-delta[1][1]) % 96 == 0:
                b = -delta[1][1]//48
                a = (-delta[0][0]+delta[1][1])//96
                for state in range(3):
                    u, v = 509*state+i, 509*((state+a-b) % 3)+j
                    coincidences.add(tuple(sorted((u, v))))
                    union(u, v)
            for x, y, z, w in sphere(DEN*DEN-fixed, delta[0][0] % 96, delta[1][1] % 96):
                a, b = (x-delta[0][0]-w+delta[1][1])//96, (w-delta[1][1])//48
                c, d = (z+y)//288, -y//144
                point = ([x, y]+list(delta[0][2:]), [z, w]+list(delta[1][2:]))
                if squared_distance(point, zero, table) == [DEN*DEN]+[0]*7:
                    rows.append((i, j, a, b, c, d))
                    for state in range(3):
                        edges.add(tuple(sorted((509*state+i, 509*((state+a-b) % 3)+j))))
    # N=3 changes the first-lattice label by seven unit steps.
    for i in range(509):
        for q in range(3):
            edges.add(tuple(sorted((509*q+i, 509*((q+1) % 3)+i))))
    roots = sorted({find(i) for i in range(1527)})
    index = {v: i for i, v in enumerate(roots)}
    labels = [index[find(i)] for i in range(1527)]
    merged = sorted({tuple(sorted((labels[i], labels[j]))) for i, j in edges})
    return labels, merged, dict(contact_rows=len(rows), unmerged_edges=len(edges),
                               coincidence_pairs=len(coincidences), sphere_cache=sphere.cache_info().currsize)


def search(budget, output):
    from parts_core import clauses
    from pysat.solvers import Solver
    raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    labels, edges, stats = compile_target(json.loads(raw))
    n = max(labels)+1
    result = dict(vertices=n, edges=len(edges), loops=sum(u == v for u, v in edges), **stats)
    print(result, flush=True)
    anchors = [[5*labels[509*q]+q+1] for q in range(3)]
    with Solver(name='cadical195', bootstrap_with=clauses(n, edges, 5)+anchors) as solver:
        solver.conf_budget(budget)
        status = solver.solve_limited()
        result.update(status=status, solver_statistics=solver.accum_stats(), conflict_budget=budget,
                      scope='Center-separable quotient for X+Lambda only; no source lower bound')
        print(result, flush=True)
        if status is True:
            model = set(solver.get_model())
            word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(n))
            result.update(word=word, labels=labels)
        if output:
            result.update(core_sha256=hashlib.sha256(raw).hexdigest(), schema=1,
                          target_edges=edges, label_map=labels)
            Path(output).write_text(json.dumps(result, separators=(',', ':'))+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget', type=int, default=50000)
    parser.add_argument('--output')
    args = parser.parse_args()
    search(args.budget, args.output)
