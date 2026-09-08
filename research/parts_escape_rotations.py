"""Leave the F11-good coordinate field via exact spindle-style rotations.

For R=c I + sqrt(d)*s J, where d is independent of K and s in K is nonzero,
old p and rotated q are a unit pair iff p cross q=0 and
|p|^2+|q|^2-2c(p dot q)=1. The radical coefficient vanishes separately.
All common vertices are just the origin. Negative SAT answers are provisional.
"""
import json
from pathlib import Path
from parts_core import RADICANDS, clauses

ROTATIONS = ((7, 13, 22), (13, 5, 8), (17, 7, 10), (41, 19, 22))


def mul(a, b):
    out = [0]*8
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i ^ j] += x*y*RADICANDS[i & j]
    return out


def contacts(core):
    pts = core['points']; den = core['coordinate_denominator']
    norms = [[a+b for a, b in zip(mul(x, x), mul(y, y))] for x, y in pts]
    cases = {d: [] for d, _, _ in ROTATIONS}
    for i, (px, py) in enumerate(pts):
        for j, (qx, qy) in enumerate(pts):
            if i == 0 or j == 0:
                continue  # Existing edges to the identified origin suffice.
            if mul(px, qy) != mul(py, qx):
                continue
            dot = [a+b for a, b in zip(mul(px, qx), mul(py, qy))]
            normsum = [a+b for a, b in zip(norms[i], norms[j])]
            normsum[0] -= den*den
            for d, num, denom in ROTATIONS:
                if all(denom*a == 2*num*b for a, b in zip(normsum, dot)):
                    cases[d].append((i, j))
    return cases


def run(root):
    from pysat.solvers import Solver
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    assert not any(x for axis in core['points'][0] for x in axis)
    cases = contacts(core)
    result = []
    for d, num, denom in ROTATIONS:
        other = lambda v: v+508 if v else 0
        edges = set(map(tuple, core['induced_edges']))
        edges.update(tuple(sorted((other(a), other(b)))) for a, b in core['induced_edges'])
        edges.update((a, other(b)) for a, b in cases[d])
        n = 1017
        with Solver(name='cadical195', bootstrap_with=clauses(n, sorted(edges), 5)) as solver:
            solver.conf_budget(500000)
            status = solver.solve_limited()
            record = dict(radicand=d, cosine=[num, denom], vertices=n,
                          induced_edges=len(edges), cross_edges=cases[d],
                          status='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN')
            if status:
                model = set(solver.get_model())
                colors = [next(c for c in range(5) if 5*v+c+1 in model) for v in range(n)]
                assert all(colors[a] != colors[b] for a, b in edges)
                record['five_coloring'] = colors
            result.append(record)
            print(json.dumps({k: v for k, v in record.items() if k not in ('cross_edges', 'five_coloring')}), flush=True)
    return dict(cases=result, scope='Exactly two Parts509 copies per case, origin identified; not the full extended field',
                negative_results_certified=False)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    result = run(root)
    (root/'certificates/parts509_escape_rotations.json').write_text(json.dumps(result, indent=2)+'\n')
