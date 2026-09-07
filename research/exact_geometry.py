"""Exact Q(sqrt(3),sqrt(11)) arithmetic for small geometry calibration."""
from fractions import Fraction as F
from itertools import combinations, product


def field(*coefficients):
    return tuple(F(x) for x in coefficients) + (F(0),) * (4-len(coefficients))


ZERO, ONE = field(0), field(1)


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def mul(a, b):
    out = [F(0)] * 4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            common = i & j
            out[i ^ j] += x*y*(3 if common & 1 else 1)*(11 if common & 2 else 1)
    return tuple(out)


def sub(a, b):
    return add(a, neg(b))


def cmul(a, b):
    return sub(mul(a[0], b[0]), mul(a[1], b[1])), add(mul(a[0], b[1]), mul(a[1], b[0]))


def distance_squared(a, b):
    dx, dy = sub(a[0], b[0]), sub(a[1], b[1])
    return add(mul(dx, dx), mul(dy, dy))


def induced_edges(points):
    assert len(points) == len(set(points)), 'Coincident vertices'
    return [(i, j) for i, j in combinations(range(len(points)), 2)
            if distance_squared(points[i], points[j]) == ONE]


def check_geometry():
    a, b, tip = (field(0, F(1, 2)), field(F(1, 2))), \
                (field(0, F(1, 2)), field(F(-1, 2))), (field(0, 1), ZERO)
    rotation = field(F(5, 6)), field(0, 0, F(1, 6))
    assert add(mul(rotation[0], rotation[0]), mul(rotation[1], rotation[1])) == ONE
    points = [(ZERO, ZERO), a, b, tip] + [cmul(rotation, p) for p in (a, b, tip)]
    edges = induced_edges(points)
    expected = [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3),
                (2, 3), (3, 6), (4, 5), (4, 6), (5, 6)]
    assert edges == expected
    # Ducz's modular identity: polynomial equality modulo 4 suffices; 4^4 cases.
    for A, B, C, D in product(range(4), repeat=4):
        N = 6*(A*A+A*B+B*B+C*C+C*D+D*D)+10*A*C+5*A*D+5*B*C+10*B*D
        M = B*C-A*D
        p, q = (A+B+D) % 2, (A+C+D) % 2
        assert (N+M) % 4 == 2*(p+q+p*q) % 4
    return dict(moser_vertices=7, all_pairs_checked=21, induced_edges=edges,
                field='Q(sqrt(3),sqrt(11))', moser_rotation_squared_norm='1',
                ducz_polynomial_residue_cases=256)


if __name__ == '__main__':
    print(check_geometry())
