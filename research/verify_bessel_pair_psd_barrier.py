#!/usr/bin/env python3
"""Exact finite algebra check for the q>=4 Bessel two-point pseudo-coloring.

Infinite global Bessel minimum and positive-definiteness are in the written
proof, not established by sampling or by this finite executable.
"""
from fractions import Fraction as F
from math import factorial
import json


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def verify_taylor():
    a = [F(4**k, factorial(k)**2) for k in range(7)]
    partial = sum(((-1)**k*a[k] for k in range(7)), F(0))
    require(partial == F(-803, 2025), "J0(4) exact k<=6 partial sum")
    require(partial < F(-1, 3), "m<-1/3 from alternating upper bound")
    require(all(F(4, (k+1)**2) < 1 for k in range(2, 9)),
            "terms strictly decrease after k=2")
    return {"even_partial_sum_n6": str(partial),
            "strictly_below_minus_one_third": True,
            "first_omitted_sign": "negative",
            "logic": "alternating decreasing tail implies J0(4) < partial"}


def verify_q(q):
    # Test the rational identities at one possible m value inside the
    # admissible range, not at the actual transcendental minimum of J0.
    m = F(-2, 5)
    require(m < F(-1, q-1), "admissible m for q")
    b = F(q, q-1)/(1-m)
    a = 1-b
    require(0 < a < 1 and 0 < b < 1, "nonnegative spectral mixture")
    rho0 = a + b
    rho1 = a + b*m
    require(rho0 == 1 and rho1 == F(-1, q-1), "unit exclusion")

    def entry(i, j, rho):
        return F(1, q*q) + (F(int(i==j), q) - F(1, q*q))*rho

    at0 = [[entry(i,j,rho0) for j in range(q)] for i in range(q)]
    at1 = [[entry(i,j,rho1) for j in range(q)] for i in range(q)]
    for i in range(q):
        require(sum(at0[i]) == F(1,q) and sum(at1[i]) == F(1,q),
                "uniform row marginals")
        for j in range(q):
            require(at0[i][j] == (F(1,q) if i==j else 0),
                    "same-site exact color identity")
            require(at1[i][j] == (0 if i==j else F(1,q*(q-1))),
                    "all unit edges are perfectly heterochromatic")
            require(at0[i][j] >= 0 and at1[i][j] >= 0,
                    "nonnegative pair matrices")
    return {"q":q, "algebraic_test_m":"-2/5",
            "spectral_constant_weight":str(a),
            "spectral_circle_weight":str(b),
            "unit_rho":str(rho1),
            "unit_equal_color_prob":"0",
            "unit_unequal_pair_prob":str(F(1, q*(q-1))),
            "same_site_single_color_probability":str(F(1,q)),
            "scope":"rational identity check only; actual m is min J0"}


def verify_three_site_hamming_triangle_gap():
    # Rigorous exact alternating-series bounds at s=1/4 and 2s=1/2.
    j_small_lower = 1 - F(1,4)**2/F(4)
    j_double_upper = 1 - F(1,2)**2/F(4) + F(1,2)**4/F(64)
    require(j_small_lower == F(63,64), "J0(1/4) strict lower")
    require(j_double_upper == F(961,1024), "J0(1/2) strict upper")
    gap_numerator_lower = 2*j_small_lower-j_double_upper-1
    require(gap_numerator_lower == F(31,1024) and gap_numerator_lower>0,
            "strict Hamming triangle inequality violation")
    # In the actual kernel, h=1/(4*t_star), and the gap is
    # (2*J0(1/4)-J0(1/2)-1)/(1-m)>31/[1024*(1-m)].
    return {"sites":"0,h,2h collinear; |h|=1/(4*t_star)",
            "J0_one_quarter_gt":str(j_small_lower),
            "J0_one_half_lt":str(j_double_upper),
            "two_J0_quarter_minus_J0_half_minus_one_gt":str(gap_numerator_lower),
            "gap_for_any_q_ge_4_gt":"31/(1024*(1-m))",
            "result":"three point joint consistency impossible for this pairwise kernel"}


if __name__=="__main__":
    print(json.dumps({"result":"PASS",
                      "scope":"exact rational calibration only, no HN=7 proof or global Bessel minimum computation",
                      "bessel_bound":verify_taylor(),
                      "color_pair_kernels":[verify_q(q) for q in (4,5,6)],
                      "three_site_triangle_gap":verify_three_site_hamming_triangle_gap()},
                     sort_keys=True, indent=2))
