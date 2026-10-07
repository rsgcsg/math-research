"""Finite exact checks for R158-C and R158-F; NOT their analytic proofs.

No floating point, solver, network, or upstream executable is used.
"""
from fractions import Fraction as Q
from itertools import product
import json


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def support_rounding():
    tests = 0
    zeros = 0
    for k in range(1, 4):
        for relation in range(1 << (k*k)):
            for a in range(1, 1 << k):
                aa = [i for i in range(k) if (a >> i) & 1]
                for b in range(1, 1 << k):
                    bb = [j for j in range(k) if (b >> j) & 1]
                    # Strictly positive uniform masses on each selected support.
                    forbidden_numerator = sum(
                        1 - ((relation >> (i*k+j)) & 1) for i in aa for j in bb
                    )
                    all_allowed = all((relation >> (i*k+j)) & 1
                                      for i in aa for j in bb)
                    require((forbidden_numerator == 0) == all_allowed,
                            'zero forbidden product/support mismatch')
                    if not forbidden_numerator:
                        zeros += 1
                        require((relation >> (aa[0]*k+bb[0])) & 1,
                                'least-positive rounding failed')
                    tests += 1
    return dict(relation_support_pairs=tests, zero_product_cases=zeros,
                label_sizes=[1, 2, 3])


def reflection_polarization():
    # Real functions on Z/5 with f(x)=f(-x); all independent values in {-1,0,1}.
    evens = [(a, b, c, c, b) for a, b, c in product((-1, 0, 1), repeat=3)]
    def corr(f, g, z):
        return sum(f[x]*g[(x+z) % 5] for x in range(5))
    tests = 0
    for f, g in product(evens, repeat=2):
        h = tuple(x+y for x, y in zip(f, g))
        for z in range(5):
            cross = corr(f, g, z)
            require(cross == corr(g, f, z) == corr(f, g, -z),
                    'reflection cross symmetry')
            require(2*cross == corr(h, h, z)-corr(f, f, z)-corr(g, g, z),
                    'real polarization identity')
            tests += 1
    # Without reflection invariance, self-polarization alone is insufficient.
    f, g = (1, 0, 0, 0, 0), (0, 1, 0, 0, 0)
    require(corr(f, g, 1) != corr(g, f, 1), 'missing reflection counterexample')
    return dict(exact_identities=tests, nonreflection_counterexample_checked=True)


def rotate(z, inverse=False):
    # z = a + b*i + (c+d*i)*sqrt(2); multiplication by (3+4i)/5.
    a, b, c, d = map(Q, z)
    v = -Q(4, 5) if inverse else Q(4, 5)
    u = Q(3, 5)
    return (u*a-v*b, v*a+u*b, u*c-v*d, v*c+u*d)


def subfield_kernel():
    points = [tuple(map(Q, p)) for p in
              [(0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,0),(1,2,1,0),
               (0,0,0,1),(-2,1,0,1),(1,1,2,-1),(-1,0,2,-1)]]
    tags = sorted({p[2:] for p in points})
    incidence = [[int(p[2:] == t) for t in tags] for p in points]
    gram = [[int(a[2:] == b[2:]) for b in points] for a in points]
    require(gram == [[sum(x*y for x, y in zip(a, b)) for b in incidence]
                     for a in incidence], 'exact Gram factorization')
    # Factorization implies PSD for EVERY real or complex coefficient vector.
    comparisons = 0
    for steps in range(-5, 6):
        moved = points
        for _ in range(abs(steps)):
            moved = [rotate(p, inverse=steps < 0) for p in moved]
        for i, a in enumerate(moved):
            for j, b in enumerate(moved):
                require(int(a[2:] == b[2:]) == gram[i][j], 'subfield invariance')
                comparisons += 1
    for p in points:
        require(rotate(rotate(p), inverse=True) == p, 'inverse rotation')
    require(Q(3, 5)**2 + Q(4, 5)**2 == 1, 'unit rotation')
    require(Q(6, 5).denominator != 1, 'nonintegral cyclotomic trace')
    require(gram[0][1] == 1 and gram[0][3] == 0, 'non-Haar coefficients')
    return dict(sample_points=len(points), additive_cosets=len(tags),
                gram_rank=len(tags), rotation_pair_comparisons=comparisons,
                exact_unit_norm=True)


def main():
    if not __debug__:
        raise RuntimeError('Finite mechanism checks require non-optimized Python')
    report = dict(status='PASS_FINITE_MECHANISMS_ONLY',
                  support_rounding=support_rounding(),
                  reflection_polarization=reflection_polarization(),
                  subfield_kernel=subfield_kernel(),
                  general_transfer_formalized=False,
                  full15_decided=False,
                  scope='Finite support rounding, real polarization and exact subgroup-kernel examples. Infinite claims use the accompanying written proofs.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
