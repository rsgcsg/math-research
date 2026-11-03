"""Exact rational calibration of the 2026-11-03 Bessel two-point moment ceiling.

NOT an infinite Bochner/Riesz formalization and NOT a 6/7 chromatic proof.
The analytic argument is in docs/proofs/plane_coupled_moment_bridge_20261103.md.
"""
from fractions import Fraction as Q
from math import factorial
import json


def s0(x: Q, n: int) -> Q:
    return sum((-1)**j * (x*x/4)**j / factorial(j)**2 for j in range(n+1))


def s1(x: Q, n: int) -> Q:
    return sum((-1)**j * (x/2)**(2*j+1) /
               (factorial(j)*factorial(j+1)) for j in range(n+1))


def verify() -> dict:
    if not __debug__:
        raise RuntimeError("Run without -O: assertions must be active")
    # Alternating J0(4) tail is decreasing after index 2.
    j0_four_upper = s0(Q(4), 6)
    assert j0_four_upper == Q(-803, 2025)
    assert j0_four_upper < Q(-1, 3)

    x = Q(5, 2)
    lo0, hi0 = s0(x, 5), s0(x, 4)
    lo1, hi1 = s1(x, 5), s1(x, 4)
    assert lo0 < hi0 < 0 < lo1 < hi1
    energy_upper = lo0**2 + hi1**2
    assert energy_upper < Q(1, 4)
    assert lo0 > Q(-1, 2)

    # True mismatch at 2h minus two mismatches at h is strictly positive;
    # the numerator is bounded below by this purely rational expression.
    gap = 2*s0(Q(1, 10), 3) - s0(Q(1, 5), 2) - 1
    assert gap == Q(5734799, 1152000000)
    assert gap > 0

    tables = []
    for k in (4, 5, 6, 7, 12):
        f_unit = -Q(1, k-1)
        same = Q(1, k*k) + Q(k-1, k*k)*f_unit
        distinct = (1-f_unit)/(k*k)
        assert same == 0
        assert distinct == Q(1, k*(k-1))
        assert same+(k-1)*distinct == Q(1, k)
        # Check algebraic decomposition of color projections.
        for shift in range(k):
            vec = [Q(((2*j+shift)%7)-3, 5) for j in range(k)]
            mean = sum(vec)/k
            parallel = sum(vec)**2/k
            perpendicular = sum((v-mean)**2 for v in vec)
            assert parallel >= 0 and perpendicular >= 0
            assert parallel+perpendicular == sum(v*v for v in vec)
        tables.append({"k": k, "unit_same": str(same),
                       "unit_different_ordered_pair": str(distinct)})

    return {
        "status": "PASS_EXACT_RATIONAL_CALIBRATION",
        "j0_four_upper": str(j0_four_upper),
        "j0_5_over_2_interval": [str(lo0), str(hi0)],
        "j1_5_over_2_interval": [str(lo1), str(hi1)],
        "energy_5_over_2_upper": str(energy_upper),
        "energy_below_one_quarter": True,
        "global_min_strict_range": "(-1/2,-1/3)",
        "three_point_gap_numerator_lower": str(gap),
        "three_point_gap_strict": True,
        "sample_tables": tables,
        "new_analytic_theorem_formalized": False,
        "hn_exact_six_or_seven_decided": False,
        "scope": "Fractional rational tails, algebraic marginals, projection calibrations only; all infinite claims use the written proof."
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
