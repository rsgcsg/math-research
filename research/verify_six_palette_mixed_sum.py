#!/usr/bin/env python3
"""Independent finite exact checks for a six-label one-center mock palette.
Does not certify infinite weak-measurable arguments or ordinary plane chi=7.
"""
import json
from fractions import Fraction as Q
from itertools import combinations

LABELS = frozenset(range(6))
C = frozenset((2, 3, 4, 5))
N = 18


def check(flag, message):
    if not flag:
        raise ValueError(message)


def palette(i):
    i %= N
    return frozenset((0, 1)) if (i // 3) % 2 == 0 else C - {2 + (i % 3)}


def verify():
    sizes = [len(palette(i)) for i in range(N)]
    check(sizes == [2, 2, 2, 3, 3, 3] * 3, "palette sizes")
    for i in range(N):
        p, q = palette(i), palette(i + 3)
        check(not (p & q) and len(p | q) == 5, "R60 saturated disjointness")
        check(LABELS - (p | q) == {2 + i % 3}, "unique remaining color")
    for i in range(N):
        for j in range(N):
            check(len(palette(i) | palette(j)) <= 5, "two-angle abstract union")
    for i, j in combinations(range(N), 2):
        if i % 3 == j % 3:
            gap = min((j - i) % N, (i - j) % N)
            check(gap >= 3 and (gap-1)*20 >= 40, "same-color angular separation")
    # Outer-ring irrational chord angle alpha is between 20 and 40 degrees.
    # cos(pi/9) > sqrt(3)/2 > 5/6 > (1+sqrt(5))/4 > cos(2pi/9).
    check(Q(3, 4) > Q(25, 36), "sqrt(3)/2 > 5/6")
    check(Q(5) < Q(49, 9), "sqrt(5) < 7/3")
    a, b = Q(5, 3), Q(7, 4)
    same_max = b-a + 2*b*Q(22, 7)/18
    far_min = 2*a*(Q(1, 3) - Q(1, 3)**3/6)
    check(same_max == Q(25, 36) and same_max < 1, "local annulus short pairs")
    check(far_min == Q(265, 243) and far_min > 1, "local annulus long pairs")
    # Four-ray gadget: s=sin(delta)=(sqrt(3)-1)/2.
    # v1-v2=sqrt(3)*exp(i*pi/3), e1-e2=-2s*exp(i*pi/3).
    sin_delta = (Q(-1, 2), Q(1, 2))  # coefficients a+b*sqrt(3)
    coefficient = (Q(0)-2*sin_delta[0], Q(1)-2*sin_delta[1])
    check(coefficient == (Q(1), Q(0)), "mixed-sum exact unit chord")
    check(Q(3) < Q(4), "sqrt(3)<2 gives 0<delta<pi/6")
    # Directed endpoint chord directions span six 60-degree directions.
    endpoints = sorted({(120 + 60*n) % 360 for n in (0, 2, 4)} |
                       {(300 + 60*n) % 360 for n in (0, 2, 4)})
    check(endpoints == [0, 60, 120, 180, 240, 300], "six signed endpoint chords")
    return {
        "result": "PASS",
        "scope": "finite exact calibration only; abstract palette is NOT a true weak six-coloring",
        "angular_sectors": N,
        "palette_sizes": sizes,
        "all_R60_unions_have_five_distinct_colors": True,
        "every_independent_angle_union_has_at_most_five_colors": True,
        "forced_color_by_sector": [2 + i%3 for i in range(N)],
        "outer_circle_chord_rotation_bracket": "pi/9 < arccos(5/6) < 2pi/9",
        "independent_three_color_annulus_radii": [str(a), str(b)],
        "same_sector_distance_strictly_less_than": str(same_max),
        "separated_same_color_distance_strictly_greater_than": str(far_min),
        "mixed_sum_difference_exact_unit": True,
        "even_sector_signed_endpoint_chords_degrees": endpoints,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
