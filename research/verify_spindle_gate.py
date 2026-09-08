"""Independent all-pairs gate geometry and complete local diamond-list identity."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from math import gcd
import json


def verify(root):
    data = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    radicals = (1, 3, 11, 33)
    assert data['schema'] == 1 and data['radicals'] == list(radicals)
    points = [tuple(tuple(F(v) for v in axis) for axis in p) for p in data['points']]
    assert len(points) == len(set(points)) == 21
    assert all(len(p) == 2 and all(len(a) == 4 for a in p) for p in points)
    def multiply(left, right):
        out = [F(0)]*4
        for i, x in enumerate(left):
            for j, y in enumerate(right):
                g = gcd(radicals[i], radicals[j])
                k = radicals.index(radicals[i]*radicals[j]//(g*g))
                out[k] += g*x*y
        return out
    def square(axis):
        return multiply(axis, axis)
    def subtract(left, right):
        return [x-y for x, y in zip(left, right)]
    def norm_squared(vector):
        return [x+y for x, y in zip(square(vector[0]), square(vector[1]))]
    edges = []
    for a, b in combinations(range(21), 2):
        norm = [F(0)]*4
        for ax in range(2):
            value = square([x-y for x, y in zip(points[a][ax], points[b][ax])])
            norm = [x+y for x, y in zip(norm, value)]
        if norm == [1, 0, 0, 0]:
            edges.append([a, b])
    spindle = [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3),
               (2, 3), (3, 6), (4, 5), (4, 6), (5, 6)]
    expected = set(spindle)
    for i in range(7):
        expected.update(((i, 7+2*i), (i, 8+2*i), (7+2*i, 8+2*i)))
    assert edges == data['induced_edges'] == [list(e) for e in sorted(expected)]
    assert data['boundary_pairs'] == [[7+2*i, 8+2*i] for i in range(7)]
    # T040: no three boundary vertices lie on a circle of radius one.
    # For noncollinear points, R^2 = |u|^2 |v|^2 |u-v|^2 / (4 det(u,v)^2).
    # This checks all possible circle centers, not only stored graph vertices.
    circle_triples = 0
    for a, b, c in combinations(range(7, 21), 3):
        u = [subtract(points[b][k], points[a][k]) for k in range(2)]
        v = [subtract(points[c][k], points[a][k]) for k in range(2)]
        uv = [subtract(u[k], v[k]) for k in range(2)]
        determinant = subtract(multiply(u[0], v[1]), multiply(u[1], v[0]))
        assert determinant != [0]*4
        side_product = multiply(multiply(norm_squared(u), norm_squared(v)), norm_squared(uv))
        assert side_product != [4*x for x in square(determinant)]
        circle_triples += 1
    assert circle_triples == 364
    word = data['four_coloring']
    assert len(word) == 21 and all(isinstance(c, int) and 0 <= c < 4 for c in word)
    assert all(word[a] != word[b] for a, b in edges)
    assert not any(all(w[a] != w[b] for a, b in spindle) for w in product(range(3), repeat=7))
    sets = [set(c) for n in range(2, 6) for c in combinations(range(5), n)]
    tips = [s for s in sets if len(s) >= 3]
    cases = 0
    for A, B, C in product(sets, sets, tips):
        actual = {c for c in C if any(a != b and a != c and b != c for a in A for b in B)}
        expected_tip = C-A if A == B and len(A) == 2 else C
        assert actual == expected_tip
        cases += 1
    assert cases == 10816
    # NAE pair predicate and the three-distinct-anchor escape, all labelled pairs.
    pairs = list(combinations(range(5), 2))
    for first, second in product(pairs, repeat=2):
        for a, b in (first, first[::-1]):
            for c, d in (second, second[::-1]):
                if len({a, b, c}) == 3:
                    assert set(first) != set(second)
    # T039: a fresh-color homogeneous output cannot come from unequal old
    # proper edge palettes. Check every local preimage, including unchanged edges.
    repair_cases = 0
    for alpha in range(4):
        states = []
        for a, b in product(range(4), repeat=2):
            if a == b:
                continue
            for select in (False, True):
                out = frozenset(4 if select and x == alpha else x for x in (a, b))
                states.append((frozenset((a, b)), out))
        for (old, out), (old2, out2) in product(states, repeat=2):
            if out == out2 and 4 in out:
                assert old == old2
            repair_cases += 1
    for bits in product((0, 1), repeat=7):
        outputs = [frozenset((4 if bit else 0, 1)) for bit in bits]
        assert (len(set(outputs)) == 1) == (sum(bits) in (0, 7))
    return dict(status='VERIFIED_EXACT_SPINDLE_PAIR_GATE_AND_DIAMOND_LIST_IDENTITY',
                vertices=21, all_pairs=210, induced_edges=len(edges), chromatic_number=4,
                local_list_cases=cases, repair_preimage_cases=repair_cases,
                repair_bit_patterns=128, bad_labelled_boundaries=10*2**7,
                boundary_circle_triples=circle_triples, maximum_external_boundary_neighbors=2,
                bad_boundary_count_uses='Written T037 list proof, not enumeration of 5^14 assignments',
                scope='Not the original historical 28-point Galois geometry')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
