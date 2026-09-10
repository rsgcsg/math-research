"""Independent standard-library checks for C016.

No search code, certificate producer, symbolic algebra, or solver is imported.
The infinite field and minimum-witness claims require the accompanying proof.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb
from pathlib import Path
import json


ZERO = (Q(0),) * 4
ONE = (Q(1), Q(0), Q(0), Q(0))
ETA = (Q(0), Q(1), Q(0), Q(0))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, c):
    return tuple(c * x for x in a)


def multiply(a, b):
    """Q[X]/(1+X+X^2+X^3+X^4), by polynomial division."""
    terms = [Q(0)] * 7
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            terms[i + j] += x * y
    for k in range(6, 3, -1):
        lead = terms[k]
        for j in range(5):
            terms[k - 4 + j] -= lead
    assert terms[4:] == [0, 0, 0]
    return tuple(terms[:4])


def power(a, n):
    result = ONE
    for _ in range(n):
        result = multiply(result, a)
    return result


def substitute(a, image):
    result = ZERO
    for j, c in enumerate(a):
        result = add(result, scale(power(image, j), c))
    return result


def conjugate(a):
    return substitute(a, power(ETA, 4))


def norm(a):
    return multiply(a, conjugate(a))


def conic_calibrations():
    """Separate exact parameter checks, not part of C016's obstruction."""
    results = []
    for r in (Q(-1), Q(0), Q(1), Q(3, 2), Q(8, 5), Q(5, 3), Q(2)):
        denominator = 4 - 3 * r * r
        x = (-4 + 6 * r - 3 * r * r) / denominator
        y = (4 - 8 * r + 3 * r * r) / denominator
        beta = (1 - x * x) / 3
        assert 4 * x * x - 3 * y * y == 1
        assert x * x == 1 - 3 * beta
        assert y * y == 1 - 4 * beta
        results.append(dict(r=str(r), t3=str(x), t4=str(y), beta=str(beta)))
    assert results[4] == dict(r='8/5', t3='13/23', t4='7/23', beta='120/529')
    assert results[5] == dict(r='5/3', t3='7/13', t4='3/13', beta='40/169')
    return results


def verify(root=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')

    # Phi_5(X+1) is 5-Eisenstein: this is an irreducibility proof, not
    # a failure to find rational roots of a degree-four polynomial.
    shifted = [sum(comb(j, k) for j in range(k, 5)) for k in range(5)]
    assert shifted == [5, 10, 10, 5, 1]
    assert shifted[-1] == 1 and all(x % 5 == 0 for x in shifted[:-1])
    assert shifted[0] % 25 != 0
    assert power(ETA, 5) == ONE
    assert all(power(ETA, j) != ONE for j in range(1, 5))
    assert len({power(ETA, j) for j in range(5)}) == 5

    # Exact C4 automorphism, contrasting with the exponent-two group of F.
    orbit = []
    point = ETA
    for _ in range(4):
        orbit.append(point)
        point = substitute(point, power(ETA, 2))
    assert len(set(orbit)) == 4 and point == ETA
    assert {a * a % 5 for a in (1, 2, 3, 4)} == {1, 4}
    assert all((a ^ a) == 0 for a in range(16))

    t = add(ETA, conjugate(ETA))
    sqrt5 = add(scale(t, 2), ONE)
    assert conjugate(t) == t and multiply(sqrt5, sqrt5) == scale(ONE, 5)
    assert add(add(multiply(t, t), t), scale(ONE, -1)) == ZERO
    assert substitute(sqrt5, power(ETA, 2)) == scale(sqrt5, -1)
    assert power(ETA, 2) == add(multiply(t, ETA), scale(ONE, -1))

    # Three F-linear norm obligations, and the forced real/imaginary squares.
    units = [ONE, ETA, power(ETA, 2)]
    assert all(norm(u) == ONE for u in units)
    real_part = scale(t, Q(1, 2))
    imaginary_square = add(ONE, scale(multiply(real_part, real_part), -1))
    assert imaginary_square == scale(add(scale(ONE, 5), sqrt5), Q(1, 8))
    assert add(add(scale(multiply(imaginary_square, imaginary_square), 16),
                   scale(imaginary_square, -20)), scale(ONE, 5)) == ZERO

    # Each two-obligation subset is satisfiable by explicit weights in Q(t).
    # The general minimum-cardinality assertion is proved using a vector basis.
    pair_weights = [
        ((0, 1), (ONE, ONE)),
        ((0, 2), (ONE, scale(add(t, ONE), 2))),
        ((1, 2), (add(t, scale(ONE, -1)), ONE)),
    ]
    for required, (z0, z1) in pair_weights:
        images = [z0, z1, add(multiply(t, z1), scale(z0, -1))]
        assert all(conjugate(z) == z for z in (z0, z1))
        assert all(norm(images[j]) == ONE for j in required)

    # Both sqrt(5) residue choices exclude the new real radical at 11.
    squares = {a * a % 11 for a in range(11)}
    assert squares == {0, 1, 3, 4, 5, 9}
    roots = [a for a in range(11) if a * a % 11 == 5]
    assert roots == [4, 7]
    residues = [(5 + a) * pow(8, -1, 11) % 11 for a in roots]
    assert residues == [8, 7] and all(a not in squares for a in residues)

    # The witness graph itself is a bipartite star, using all actual pairs.
    small_points = [ZERO] + units
    small_edges = [(i, j) for i, j in combinations(range(4), 2)
                   if norm(add(small_points[i], scale(small_points[j], -1))) == ONE]
    assert small_edges == [(0, 1), (0, 2), (0, 3)]

    # Q-independence follows from the first three coordinates of this basis;
    # test a complete physical box as a separate positive induced-graph check.
    labels = list(product(range(-2, 3), repeat=3))
    points = [tuple(map(Q, label)) + (Q(0),) for label in labels]
    assert len(set(points)) == 125
    physical_edges = listed_edges = 0
    directions = set(units + [scale(u, -1) for u in units])
    for i, j in combinations(range(len(points)), 2):
        difference = add(points[i], scale(points[j], -1))
        listed = difference in directions
        actual = norm(difference) == ONE
        assert actual == listed
        physical_edges += actual
        listed_edges += listed
        if actual:
            assert sum(labels[i]) % 2 != sum(labels[j]) % 2
    assert physical_edges == listed_edges == 300

    return dict(status='PASS', check='quintic_projection', counterexample='C016',
                unit_directions=3, minimum_norm_obligations=3,
                witness_points=4, witness_exact_pairs=6, witness_induced_edges=3,
                finite_box_points=125, finite_box_exact_pairs=7750,
                finite_box_induced_edges=physical_edges,
                residue11_radical_squares=residues,
                shell_parameter_calibrations=conic_calibrations(),
                scope='No five-color obstruction; infinite claims use the written proof.')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('verification requires assertions')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
