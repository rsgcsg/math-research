"""Exact finite-algebra calibration for the order-three five-color pseudolaw.

This does not verify uncountably many geometric configurations or the external
no-five-color theorem. Read the accompanying full mathematical proof.
"""
from fractions import Fraction as Q
from itertools import product
import json

BITS = tuple(product((0, 1), repeat=3))


def check_binary_law(weights):
    den = sum(weights)
    if den == 0:
        return None
    means = [Q(sum(w*bits[i] for w, bits in zip(weights, BITS)), den)
             for i in range(3)]
    if not (means[0] == means[1] == means[2]):
        return None
    delta = means[0]
    if not (Q(1, 5) < delta < 1):
        return None
    pairs = ((0, 1), (0, 2), (1, 2))
    q = [sum(Q(w, den)*bits[i]*bits[j]
             for w, bits in zip(weights, BITS))/delta
         for i, j in pairs]
    assert all(0 <= t <= 1 for t in q)
    d = [1-t for t in q]
    assert all(d[i] <= d[(i+1) % 3] + d[(i+2) % 3] for i in range(3))
    a = max(Q(0), (sum(q)-1)/2)
    b = [t-a for t in q]
    c = 1-sum(q)+2*a
    assert all(t >= 0 for t in [a, *b, c])
    assert a + sum(b) + c == 1
    assert all(a+b[i] == q[i] for i in range(3))
    for i in range(3):
        if q[i] == 0:
            assert a == b[i] == 0
    for k in (5, 6, 7):
        assert (k*delta-1)/(k-1) > 0
        assert Q(k)/((k-1)*delta) > 0
    return tuple(q)


def run():
    if not __debug__:
        raise RuntimeError("Non-optimized Python required")
    # pi>3, sqrt(3)<7/4: the actual disk density >3/14>1/5.
    assert Q(3, 14) > Q(1, 5)
    for m in range(-4, 5):
        for n in range(-4, 5):
            if (m, n) != (0, 0):
                assert m*m + m*n + n*n >= 1
                assert (2*m+n)**2 + 3*n*n >= 4
    total, asymmetric, patterns = 0, 0, set()
    for weights in product(range(3), repeat=8):
        q = check_binary_law(weights)
        if q is None:
            continue
        total += 1
        patterns.add(q)
        if len(set(q)) > 1:
            asymmetric += 1
    assert total == 399 and asymmetric == 324 and len(patterns) == 95
    return {
      "status": "PASS_FINITE_EXACT_ALGEBRA_ONLY",
      "lattice_vectors_checked": 80,
      "equal_marginal_binary_cases": total,
      "asymmetric_three_pair_cases": asymmetric,
      "distinct_pair_triples": len(patterns),
      "rational_density_lower": "3/14>1/5",
      "full_hadwiger_nelson_decided": False,
      "scope": "Rational three-point partition calibration only; continuum construction and PSD in the written proof, not Lean-formalized."
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
