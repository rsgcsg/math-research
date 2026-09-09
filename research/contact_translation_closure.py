"""Search-side contact-translation closure and a denominator-13 finite probe.

Infinite conclusions are proved in docs/proofs/contact_translation_closure.md.
This producer is not imported by the independent certificate checker.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

from parts_core import clauses, mul

ROOT = Path(__file__).resolve().parents[1]
RAD = (1, 3, 11, 33, 5, 15, 55, 165)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def lattice_units():
    return [(a, b) for a, b in product(range(-1, 2), repeat=2) if a*a+a*b+b*b == 1]


def shifts():
    unit = lattice_units()
    return ([(0, 0, 0, 0)] + [(a, b, 0, 0) for a, b in unit]
            + [(0, 0, a, b) for a, b in unit]
            + [(2, 0, 0, 0), (3, 0, 0, 0), (3, 1, 0, 0)])


def base_points(core, q, first, second):
    points = []
    for a, b, c, d in shifts():
        for p in core['points']:
            x, y = ([q*z for z in ax] for ax in p)
            x[0] += 48*first*(2*a+b)
            x[1] -= 48*second*d
            y[0] += 48*second*(2*c+d)
            y[1] += 48*first*b
            points.append((tuple(x), tuple(y)))
    assert len(points) == len(set(points))
    return points


def complete_base_edges(points, den):
    prime = 1031
    roots = {a*a % prime: a for a in range(prime)}
    images = []
    for r in RAD:
        v = 1
        for d in (3, 5, 11):
            if r % d == 0:
                v = v*roots[d] % prime
        images.append(v)
    residues = [tuple(sum(a*b for a, b in zip(ax, images)) % prime for ax in p) for p in points]
    edges = []
    for i, j in combinations(range(len(points)), 2):
        (x, y), (u, v) = residues[i], residues[j]
        if ((x-u)**2+(y-v)**2-den*den) % prime:
            continue
        dx, dy = (tuple(a-b for a, b in zip(ax, bx)) for ax, bx in zip(points[i], points[j]))
        if tuple(a+b for a, b in zip(mul(dx, dx), mul(dy, dy))) == (den*den,)+(0,)*7:
            edges.append((i, j))
    return edges


def cross_edges(points, centers, first, second):
    lookup = {p: i for i, p in enumerate(points)}
    edges = []
    counts = Counter()
    size = len(points)
    for i, (a, b) in enumerate(centers):
        for j, (c, d) in enumerate(centers):
            if j <= i:
                continue
            m, n = c-a, d-b
            norm = m*m+m*n+n*n
            if norm not in (3, 4):
                continue
            for sign in (-1, 1):
                x, y = [0]*8, [0]*8
                if norm == 3:
                    x[0], y[1] = -sign*48*first*n, sign*16*first*(2*m+n)
                else:
                    x[1], y[0] = -sign*24*second*n, sign*24*second*(2*m+n)
                for k, point in enumerate(points):
                    other = tuple(tuple(a+b for a, b in zip(ax, bx)) for ax, bx in zip(point, (x, y)))
                    if other in lookup:
                        edges.append((i*size+k, j*size+lookup[other]))
                        counts[norm] += 1
    return sorted(edges), counts


def build():
    from pysat.solvers import Solver
    raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    core = json.loads(raw)
    q, first, second = 13, 7, 3
    den = 96*q
    points = base_points(core, q, first, second)
    base = complete_base_edges(points, den)
    print('base', len(points), len(base), 'mixed', sum(i//509 != j//509 for i, j in base), flush=True)
    centers = [(m, n) for m, n in product(range(-1, 2), repeat=2) if m*m+m*n+n*n <= 1]
    cross, counts = cross_edges(points, centers, first, second)
    edges = sorted([(z*len(points)+i, z*len(points)+j) for z in range(len(centers)) for i, j in base]+cross)
    npoints = len(points)*len(centers)
    target = sorted(set(base)|{tuple(sorted((i % len(points), j % len(points)))) for i, j in cross})
    old = core['five_coloring']
    frame_edges = sorted({tuple(sorted((5*(i//509)+old[i % 509], 5*(j//509)+old[j % 509]))) for i, j in target})
    # A sufficient positive ansatz: each copy may independently permute its
    # five old classes. Failure here would NOT be a source-graph refutation.
    with Solver(name='cadical195', bootstrap_with=clauses(80, frame_edges, 5)+[[1]]) as solver:
        solver.conf_budget(20000)
        answer = solver.solve_limited()
        assert answer is True, 'Frame model unresolved; do not assert a finite five-color witness'
        model = set(solver.get_model())
        frame_word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(80))
    one_layer = ''.join(frame_word[5*(i//509)+old[i % 509]] for i in range(len(points)))
    assert all(one_layer[i] != one_layer[j] for i, j in target)
    word = one_layer*len(centers)
    assert all(word[i] != word[j] for i, j in edges)
    print('probe', npoints, len(edges), dict(counts), 'frame SAT', len(frame_edges), flush=True)
    mixed = [(i, j) for i, j in base if i//509 != j//509]
    witness = mixed[0]
    # Exact ordered core pairs and shift labels are retained, not a fixed palette.
    return dict(schema=1, core_sha256=hashlib.sha256(raw).hexdigest(),
                old=dict(q=23, first=13, second=7,
                         trace_radius_squared=[4, 1], trace_diameter_squared=[16, 1],
                         roots3_mod23=[7, 16], shift_color='((a-b+c-d) mod3)',
                         coloring='(core_color + shift_color) mod5'),
                probe=dict(q=q, first=first, second=second, beta=[40, 169],
                           denominator=den, shifts=shifts(), centers=centers,
                           base_vertices=len(points), base_edges=len(base),
                           base_edge_sha256=digest(base), mixed_base_edges=len(mixed),
                           mixed_witness=list(witness), cross_edges_by_shell=dict(counts),
                           vertices=npoints, edges=len(edges), edge_sha256=digest(edges),
                           all_center_target_edges=len(target), target_edge_sha256=digest(target),
                           frame_edges=len(frame_edges), frame_word=frame_word,
                           solver='cadical195', conflict_budget=20000,
                           status='SAT_WITNESS',
                           five_word=word),
                scope='Old full contact closure and new specified 16-translation infinite array exactly five; full field stacks unresolved')


if __name__ == '__main__':
    data = build()
    (ROOT/'certificates/contact_translation_closure.json').write_text(json.dumps(data, indent=2)+'\n')
