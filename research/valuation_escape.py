"""Exact calibration of unbounded-depth cross edges for cos(theta)=5/8.

The infinite statement is the Hensel-lifting proof, not the finite cutoff here.
Two copies of K^2 rotated relative to each other acquire cross edges whose two
pre-rotation endpoints both have arbitrarily negative 11-adic valuation.
"""
from fractions import Fraction as F
import json


def valuation11(value):
    value = F(value)
    if not value:
        raise ValueError('This calibration uses nonzero values only')
    n, d = abs(value.numerator), value.denominator
    v = 0
    while n % 11 == 0:
        v += 1
        n //= 11
    while d % 11 == 0:
        v -= 1
        d //= 11
    return v


def verify(depth=24):
    # F(T)=4T^2-5T+4 has simple roots 7,8 modulo 11.
    polynomial = lambda t: 4*t*t-5*t+4
    assert [t for t in range(11) if polynomial(t) % 11 == 0] == [7, 8]
    lifted = 7
    examples = []
    for m in range(1, depth+1):
        modulus = 11**m
        assert polynomial(lifted) % modulus == 0
        t = lifted
        if polynomial(t) % (11*modulus) == 0:
            t += modulus  # Force exact, not merely lower-bounded, valuation m.
        assert valuation11(polynomial(t)) == m
        a = F(4*(t*t-1), polynomial(t))
        b = F(t*(5*t-8), polynomial(t))
        assert valuation11(a) == valuation11(b) == -m
        assert a*a+b*b-F(5, 4)*a*b == 1
        # Actual cross displacement: (a-5b/8, -sqrt(39)b/8).
        assert (a-F(5, 8)*b)**2+39*(b/8)**2 == 1
        # Exact polynomial coefficient identity, tested independently at each t.
        aa=4*(t*t-1);bb=t*(5*t-8);ff=polynomial(t)
        assert 4*aa*aa+4*bb*bb-5*aa*bb == 4*ff*ff
        # Radial nonbacktracking transport (T031). Its invariant is exactly
        # the cross-edge equation; no assertion about full-graph colorability.
        pair = (a, b)
        seen = set()
        for _ in range(16):
            assert pair not in seen
            seen.add(pair)
            x, y = pair
            assert x*x+y*y-F(5, 4)*x*y == 1
            pair = (y, F(5, 4)*y-x)
        if m <= 3:
            examples.append(dict(depth=m, t=t, a=str(a), b=str(b)))
        correction = -(polynomial(lifted)//modulus)*pow(8*lifted-5, -1, 11) % 11
        lifted += correction*modulus
    assert examples[0]['a'] == '64/55' and examples[0]['b'] == '63/55'
    return dict(status='VERIFIED_FINITE_CALIBRATION_OF_INFINITE_VALUATION_ESCAPE_FAMILY',
                checked_depths=depth, radial_steps_per_depth=16, examples=examples,
                infinite_proof='docs/proofs/valuation_escape.md',
                no_chromatic_lower_bound_claim=True)


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(), indent=2))
