"""Exact Gaussian-rational arithmetic and finite binary-effect calibrations.

This module does not claim to formalize the general graph theorem.
"""
from fractions import Fraction as F
from itertools import product
import random


def require(ok, message):
    if not ok:
        raise ValueError(message)


# Exact Gaussian rationals, represented by pairs (real, imaginary).
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def z(a=0, b=0):
    return (F(a), F(b))


def za(a, b):
    return (a[0] + b[0], a[1] + b[1])


def zm(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def zb(a):
    return (a[0], -a[1])


def ident(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def add(a, b):
    return tuple(tuple(za(x, y) for x, y in zip(ar, br)) for ar, br in zip(a, b))


def scale(c, a):
    return tuple(tuple((F(c)*x, F(c)*y) for x, y in row) for row in a)


def mm(a, b):
    n = len(a)
    require(n and len(b) == n and all(len(row) == n for row in a+b), 'matrix shape')
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            value = ZERO
            for k in range(n):
                value = za(value, zm(a[i][k], b[k][j]))
            row.append(value)
        out.append(tuple(row))
    return tuple(out)


def adj(a):
    return tuple(tuple(zb(a[j][i]) for j in range(len(a))) for i in range(len(a)))


def norm2(a):
    return sum(x*x + y*y for row in a for x, y in row)


def real_trace(a):
    value = ZERO
    for i in range(len(a)):
        value = za(value, a[i][i])
    require(value[1] == 0, 'trace not real')
    return value[0]


def formula_check(a, b):
    require(adj(a) == a and adj(b) == b, 'non-Hermitian input')
    n = len(a)
    half = scale(F(1, 2), ident(n))
    ea, eb = add(half, a), add(half, b)
    fa, fb = add(half, scale(-1, a)), add(half, scale(-1, b))
    left = norm2(mm(ea, eb)) + norm2(mm(fa, fb))
    right = F(n, 8) + (norm2(a)+norm2(b))/2 + 2*real_trace(mm(a, b)) + 2*norm2(mm(a, b))
    require(left == right, 'two-effect expansion mismatch')
    return mm(a, b) != mm(b, a)


def exact_identity_samples():
    rng = random.Random(15820261008)
    samples, noncommuting = 0, 0
    for n in range(1, 5):
        for _ in range(10):
            matrices = []
            for _ in range(2):
                a = [[ZERO for _ in range(n)] for _ in range(n)]
                for i in range(n):
                    for j in range(i, n):
                        a[i][j] = z(rng.randrange(-3, 4), 0 if i == j else rng.randrange(-3, 4))
                        a[j][i] = zb(a[i][j])
                # Rational row-sum bound <= 1/4 certifies ||B||op <= 1/4.
                bound = max(sum(abs(x)+abs(y) for x, y in row) for row in a)
                a = scale(F(1, 4*max(1, bound)), tuple(map(tuple, a)))
                matrices.append(a)
            noncommuting += int(formula_check(*matrices))
            samples += 1
    scalar = 0
    for a, b in product([F(j, 4) for j in range(5)], repeat=2):
        formula_check(((z(a-F(1, 2)),),), ((z(b-F(1, 2)),),))
        scalar += 1
    require(noncommuting > 0, 'missing noncommuting samples')
    return dict(gaussian_hermitian_pairs=samples, noncommuting_pairs=noncommuting,
                scalar_effect_pairs=scalar, row_bound='1/4', dimensions=[1, 2, 3, 4])


def tensor(a, b):
    return tuple(tuple(zm(x, y) for x in ar for y in br) for ar in a for br in b)


def clifford_samples():
    x = ((ZERO, ONE), (ONE, ZERO))
    y = ((ZERO, z(0, -1)), (z(0, 1), ZERO))
    zz = ((ONE, ZERO), (ZERO, z(-1)))
    checks = 0
    for s in range(1, 4):
        gs = []
        for j in range(s):
            for core in (x, y):
                g = ((ONE,),)
                for k in range(s):
                    g = tensor(g, zz if k < j else core if k == j else ident(2))
                require(adj(g) == g and real_trace(g) == 0, 'Clifford Hermitian/trace')
                gs.append(g)
        size = 2**s
        for i, a in enumerate(gs):
            for j, b in enumerate(gs):
                anticom = add(mm(a, b), mm(b, a))
                require(anticom == scale(2 if i == j else 0, ident(size)), 'Clifford anticommutation')
                checks += 1
    return dict(dimensions=[2, 4, 8], anticommutators_checked=checks)


