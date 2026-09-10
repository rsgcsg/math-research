"""Independent rational checks for T079/C015. No producer or solver import.

The 96-dimensional field arithmetic is the earlier independent T076 checker.
All physical pairs are tested, not only the 14 prescribed origin edges.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json

from verify_cyclotomic_integer_stack import multiplication, norm


def quadratic(a, b):
    return (a[0]*b[0]+3*a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def pair(a, b):
    """a times conjugate(b), in basis 1,sqrt(3),i,i*sqrt(3)."""
    rr, ii = quadratic(a[:2], b[:2]), quadratic(a[2:], b[2:])
    ir, ri = quadratic(a[2:], b[:2]), quadratic(a[:2], b[2:])
    return (rr[0]+ii[0], rr[1]+ii[1], ir[0]-ri[0], ir[1]-ri[1])


def rref(rows):
    a = [list(map(Q, row)) for row in rows]
    pivot = 0
    for j in range(len(a[0])):
        k = next((k for k in range(pivot, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[pivot], a[k] = a[k], a[pivot]
        scale = a[pivot][j]
        a[pivot] = [x/scale for x in a[pivot]]
        for k in range(len(a)):
            if k != pivot and a[k][j]:
                scale = a[k][j]
                a[k] = [x-scale*y for x, y in zip(a[k], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return a[:pivot]


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    path = certificate or root/'certificates/cyclotomic_sparse_coupling.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    assert data['schema'] == 1 and data['theorem'] == 'T079' and data['counterexample'] == 'C015'
    assert data['coefficient_basis'] == ['1', 'sqrt(3)', 'i', 'i*sqrt(3)']
    assert data['powers'] == [0, 1, 2, 3]
    records = data['unit_vectors']
    assert len(records) == 14 and len({v['label'] for v in records}) == 14
    coeffs, points, rows = [], [], []
    table = multiplication()
    unit = [1]+[0]*95
    for record in records:
        encoded = record['coefficients']
        assert len(encoded) == 4 and all(len(a) == 4 for a in encoded)
        for a in encoded:
            for x in a:
                assert len(x) == 2 and all(type(v) is int for v in x) and x[1] > 0
                assert [Q(*x).numerator, Q(*x).denominator] == x
        a = [tuple(Q(*x) for x in c) for c in encoded]
        coeffs.append(a)
        point = [Q(0)]*96
        for j, c in enumerate(a):
            for b, x in zip((0, 1, 8, 9), c):
                point[16*j+b] = x
        assert norm(point, table) == unit
        points.append(tuple(point))
        row = []
        for c in a:
            squared = pair(c, c)
            assert squared[1:] == (0, 0, 0)
            row.append(squared[0])
        for i, j in combinations(range(4), 2):
            product = pair(a[i], a[j])
            assert product[1] == product[2] == 0
            row.extend((2*product[0], -2*product[3]))
        rows.append(row+[Q(1)])
    assert len(set(points)) == 14
    assert [sum(any(c) for c in a) for a in coeffs] == [1]*4+[3]*2+[4]*8
    # The displayed four-support example is a specific certificate vector.
    numerator = ((24, 0, 0, 0), (22, 0, 0, 6), (3, 0, 0, 9), (36, 0, 0, 0))
    denominator = (20, 0, 0, 22)
    explicit = [tuple(x/Q(1852) for x in pair(a, denominator)) for a in numerator]
    assert explicit == coeffs[[r['label'] for r in records].index('mixed_3_2_1')]
    assert len(set(explicit)) == 4 and all(any(a) for a in explicit)
    assert any(explicit[1][1:])  # Not in F+Q(zeta) in the unique six-power basis.

    # Rational-root theorem: neither quartic in the written slice has a rational zero.
    for q in (Q(-1), Q(1)):
        assert q**4+2*q**3-5*q*q+2*q+1 != 0
    for q in (Q(-3), Q(-1), Q(-1, 3), Q(1, 3), Q(1), Q(3)):
        assert 3*q**4-2*q**3-3*q*q-2*q+3 != 0

    # The target equations are independent of witness production and field norms.
    target = []
    def equation(terms, rhs=0):
        row = [Q(0)]*17
        for j, value in terms:
            row[j] = Q(value)
        row[-1] = Q(rhs)
        target.append(row)
    for j in range(4):
        equation([(j, 1)], 1)
    # Pairs: 01,02,03,12,13,23; real, sqrt(3)*imaginary.
    for a, b in ((4, 10), (4, 14), (5, 11), (5, 15), (6, 12), (7, 13)):
        equation([(a, 1), (b, -1)])
    equation([(4, 1), (6, 1), (8, 1)], Q(-1, 2))
    assert len(rref([row[:-1] for row in rows])) == 11
    assert len(rref(target)) == 11 and rref(rows) == rref(target)

    # Complete 35-support combinatorics, not a random support sample.
    ap = difference = 0
    for support in combinations(range(7), 3):
        counts = [sum((a-b) % 7 == k for a in support for b in support) for k in range(7)]
        is_ap = any({a, (a+d) % 7, (a+2*d) % 7} == set(support)
                    for a in range(7) for d in range(1, 7))
        if is_ap:
            ap += 1
            assert sorted(counts[1:]) == [0, 0, 1, 1, 2, 2]
        else:
            difference += 1
            assert counts[1:] == [1]*6
    assert (ap, difference) == (21, 14)
    one = (Q(1), Q(0), Q(0), Q(0))
    u = (Q(-1, 2), Q(0), Q(0), Q(1, 2))
    v = (Q(0), Q(-1, 2), Q(1, 2), Q(0))
    assert pair(u, u) == pair(v, v) == one
    assert pair(tuple(x+y+z for x, y, z in zip(one, u, v)),
                tuple(x+y+z for x, y, z in zip(one, u, v))) == (2, 0, 0, 0)

    # Preserve the distinction: the Gram obstruction itself is a small low-color graph.
    points = [(Q(0),)*96]+points
    edges = [(i, j) for i, j in combinations(range(15), 2)
             if norm([x-y for x, y in zip(points[i], points[j])], table) == unit]
    assert all((0, j) in edges for j in range(1, 15))
    neighbors = [[] for _ in points]
    for i, j in edges:
        if i:
            neighbors[i].append(j)
            neighbors[j].append(i)
    colors = [2]+[-1]*14
    for start in range(1, 15):
        if colors[start] >= 0:
            continue
        colors[start] = 0
        queue = [start]
        for i in queue:
            for j in neighbors[i]:
                if colors[j] < 0:
                    colors[j] = 1-colors[i]
                    queue.append(j)
                assert colors[j] != colors[i]
    assert all(colors[i] != colors[j] for i, j in edges)
    return dict(status='PASS', check='cyclotomic_sparse_coupling', theorem='T079', counterexample='C015',
                certificate_sha256=hashlib.sha256(raw).hexdigest(), unit_directions=14,
                gram_rows=14, gram_rank=11, ap_supports=ap, difference_supports=difference,
                physical_points=15, exact_pairs=105, induced_edges=len(edges), colors=colors)


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('verification requires assertions')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
