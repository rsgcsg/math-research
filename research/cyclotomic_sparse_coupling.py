"""Exact witnesses for T079 and C015; no SAT needed.

Coefficients lie in Q(i,sqrt(3)), basis 1,sqrt(3),i,i*sqrt(3).
Each physical point has four coefficients at 1,z,z^2,z^3, z=zeta_7.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import math


def mul(a, b):
    c = [Q(0)]*4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i ^ j] += x*y*(3 if i & j & 1 else 1)*(-1 if i & j & 2 else 1)
    return tuple(c)


def element(x=0, tau=0, imaginary=0):
    return (Q(x), Q(0), Q(imaginary), Q(tau))


def build():
    vectors = []
    for j in range(4):
        vectors.append(dict(label=f'axis_{j}', coefficients=[element(int(i == j)) for i in range(4)]))
    for support in ((0, 1, 3), (0, 2, 3)):
        vectors.append(dict(label='triple_'+''.join(map(str, support)),
                            coefficients=[element(Q(1, 2), imaginary=Q(1, 2)) if i in support
                                          else element() for i in range(4)]))
    cases = ((3, 2, 3, 12, 10, 11), (2, 3, 3, 18, 10, 11),
             (-10, 9, 139, 810, 1858, 767), (-9, 10, 139, 900, 1858, 767))
    for n, d, g, h, a, b in cases:
        lam = Q(n, d)
        x = (lam*lam+lam-1)/(2*lam)
        scalar = element(Q(h*a, a*a+3*b*b), Q(-h*b, a*a+3*b*b))
        for sign in (-1, 1):
            y = Q(sign*g, 2*n*d)
            raw = [element(1), element(x, y), element(lam*(1-x), lam*y), element(lam)]
            vectors.append(dict(label=f'mixed_{n}_{d}_{sign}', coefficients=[mul(scalar, v) for v in raw]))
    for record in vectors:
        record['coefficients'] = [[[x.numerator, x.denominator] for x in a] for a in record['coefficients']]
    return dict(schema=1, theorem='T079', counterexample='C015',
                coefficient_basis=['1', 'sqrt(3)', 'i', 'i*sqrt(3)'],
                powers=[0, 1, 2, 3], unit_vectors=vectors)


def search(bound):
    """Bounded rational slice only; not a completeness theorem for the quartics."""
    classes = (1, 3, 5, 11, 15, 33, 55, 165)
    real, complex_points = [], []
    for d in range(1, bound+1):
        for n in range(-bound, bound+1):
            if n == 0 or math.gcd(n, d) != 1:
                continue
            delta = n**4+2*n**3*d-5*n*n*d*d+2*n*d**3+d**4
            g = 3*n**4-2*n**3*d-3*n*n*d*d-2*n*d**3+3*d**4
            for value, output in ((delta, real), (g, complex_points)):
                if value <= 0:
                    continue
                for s in classes:
                    if value % s == 0 and math.isqrt(value//s)**2 == value//s:
                        output.append([n, d, s, math.isqrt(value//s)])
    return dict(status='BOUNDED_SEARCH', bound=bound, square_classes=list(classes),
                real_branch=real, nonreal_branch=complex_points,
                zero_discriminants='not listed; tested separately in proof')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search-bound', type=int)
    args = parser.parse_args()
    if args.search_bound is not None:
        assert args.search_bound > 0
        print(json.dumps(search(args.search_bound), indent=2))
        raise SystemExit(0)
    path = Path(__file__).resolve().parents[1]/'certificates/cyclotomic_sparse_coupling.json'
    data = build()
    path.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(output=str(path), unit_vectors=len(data['unit_vectors']))))
