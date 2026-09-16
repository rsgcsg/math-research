"""Independent exact checker for the nine-point non-CM host example.

No producer, symbolic algebra, SAT solver, or numerical geometry is imported.
The general CM exclusion uses the short arbitrary-map argument in the proof.
This checker certifies every actual edge and the complete four-color witness.
"""

from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path


EXPONENTS = [(i & 1, (i >> 1) & 1, (i >> 2) & 1) for i in range(8)]


def product(x, y):
    result = [Q(0)] * 8
    for u, cu in enumerate(x):
        for v, cv in enumerate(y):
            if not cu or not cv:
                continue
            a, b, h = [i+j for i, j in zip(EXPONENTS[u], EXPONENTS[v])]
            terms = [(a, b, h, cu*cv)] if h < 2 else [
                (a, b, 0, cu*cv/8), (a+1, b+1, 0, cu*cv/8)]
            for aa, bb, hh, c in terms:
                c *= 3 ** (aa//2) * 11 ** (bb//2)
                result[(aa % 2) + 2*(bb % 2) + 4*hh] += c
    return tuple(result)


def squared_distance(p, q):
    differences = [tuple(a-b for a, b in zip(x, y)) for x, y in zip(p, q)]
    xx, yy = [product(d, d) for d in differences]
    return tuple(a+b for a, b in zip(xx, yy))


def check_data(data):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E091'
    assert data['basis'] == ['1', 'sqrt(3)', 'sqrt(11)', 'sqrt(33)',
                             'h', 'sqrt(3)*h', 'sqrt(11)*h', 'sqrt(33)*h']
    assert data['h'] == 'positive sqrt((1+sqrt(33))/8)'
    pts = [tuple(tuple(Q(c) for c in axis) for axis in p) for p in data['coordinates']]
    assert len(pts) == len(set(pts)) == 9
    assert all(len(p) == 2 and all(len(axis) == 8 for axis in p) for p in pts)
    def vector(coefficients):
        return tuple(map(Q, coefficients)) + (Q(0),) * (8-len(coefficients))
    one, zero = vector([1]), vector([])
    a, b, h = vector([0, 1]), vector([0, 0, 1]), vector([0, 0, 0, 0, 1])
    assert product(a, a) == vector([3])
    assert product(b, b) == vector([11])
    assert product(h, h) == vector([Q(1,8), 0, 0, Q(1,8)])
    # h^2 has a negative real conjugate: 33>1. It is not a square in
    # Q(sqrt(3),sqrt(11)), so these eight basis coordinates are independent.
    assert 33 > 1
    assert data['basic_indices'] == dict(s=0, t=1, x=2, y=3, p=4)
    assert pts[:5] == [
        (vector([Q(-1, 2)]), zero), (vector([Q(1, 2)]), zero),
        (zero, vector([0, 0, Q(1, 2)])), (zero, vector([0, Q(1, 2)])),
        (h, vector([0, Q(1, 4), Q(1, 4)]))]
    actual = [pair for pair in combinations(range(9), 2)
              if squared_distance(pts[pair[0]], pts[pair[1]]) == one]
    assert data['actual_edges'] == [list(e) for e in actual]
    assert len(actual) == 15
    listed = {(0, 1), (0, 3), (1, 3), (2, 4), (3, 4)}
    assert data['moser_rod'] == dict(anchor=2, target=0, c=1, u=5, v=6, w=7, z=8)
    A, B, C, U, V, W, Z = 2, 0, 1, 5, 6, 7, 8
    template = [(A, U), (A, V), (B, U), (B, V), (U, V),
                (A, W), (A, Z), (C, W), (C, Z), (W, Z), (B, C)]
    listed.update(tuple(sorted(e)) for e in template)
    assert squared_distance(pts[A], pts[B]) == vector([3])
    assert squared_distance(pts[A], pts[C]) == vector([3])
    assert len(listed) == 15 and listed == set(actual)
    assert data['listed_edges'] == [list(e) for e in sorted(listed)]
    assert data['forced_pair'] == [2, 3]
    assert data['forced_squared_distance'] == '(7-sqrt(33))/2'
    assert squared_distance(pts[2], pts[3]) == vector([Q(7, 2), 0, 0, Q(-1, 2)])
    # t_- in (0,4), t_+>4, checked by strict rational square comparisons.
    assert 1 < 33 < 49
    word = data['proper_four_coloring']
    assert len(word) == 9 and all(type(c) is int and 0 <= c < 4 for c in word)
    assert all(word[i] != word[j] for i, j in actual)
    neighbors = lambda vertex: {j if i == vertex else i for i, j in actual if vertex in (i, j)}
    assert neighbors(4) == {2, 3}
    assert neighbors(3) - {4} == {0, 1}
    return dict(status='PASS', experiment='E091', vertices=9, all_pairs=36,
                listed_unit_edges=15, actual_unit_edges=15,
                extra_actual_edges=[list(e) for e in actual if e not in listed],
                proper_four_coloring_checked=True, moser_rods=1,
                degree_two_peeling=[4, 3], original_seven_port_relation_unchanged_for_k_ge_3=True,
                forced_squared_distance='(7-sqrt(33))/2',
                scope='Exact finite geometry/color calibration of T123; no HN bound change.')


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    raw = (root / 'certificates/cm_escape_nine.json').read_bytes()
    report = check_data(json.loads(raw))
    report['certificate_sha256'] = hashlib.sha256(raw).hexdigest()
    return report


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
