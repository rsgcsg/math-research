"""Independent exact calibrations for T075's written rigidity proof.

No SAT and no search-producer imports. The all-precision and nowhere-continuity
claims are proved in the accompanying text; sampled powers only calibrate its
explicit sequence, and are not an inference from finite tests.
"""
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import json


def add(x, y):
    return tuple(a+b for a, b in zip(x, y))


def mul(x, y):
    a, b = x
    c, d = y
    return (a*c+3*b*d, a*d+b*c)


def scale(x, a):
    return tuple(a*b for b in x)


def dot(x, y):
    return add(mul(x[0], y[0]), mul(x[1], y[1]))


def verify(root=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in the proof checker')
    identity = tuple(range(5))
    palettes = 0
    color_pairs = 0
    for sigma, tau in product(permutations(range(5)), repeat=2):
        frame = (identity, sigma, tau)
        if any(len({row[a] for row in frame}) != 3 for a in range(5)):
            continue
        palettes += 1
        compatible = set()
        for a, b in product(range(5), repeat=2):
            # The two signs and all starting center states give ALL r != s.
            allowed = all(frame[r][a] != frame[s][b]
                          for r, s in product(range(3), repeat=2) if r != s)
            if allowed:
                compatible.add((a, b))
            color_pairs += 1
        assert compatible == {(a, a) for a in range(5)}
    assert palettes == 552 and color_pairs == 13800

    directions = [(u, v) for u, v in product(range(-1, 2), repeat=2)
                  if u*u+u*v+v*v == 1]
    geometric_edges = 0
    for u, v in directions:
        e = ((F(2*u+v, 2), F(0)), (F(0), F(v, 2)))
        Je = (scale(e[1], -1), e[0])
        shift = tuple(scale(axis, F(3, 13)) for axis in Je)
        assert dot(shift, shift) == (F(9, 169), 0)
        relation = set()
        for sign in (-1, 1):
            delta = tuple(scale(axis, 2*sign) for axis in e)
            assert dot(shift, delta) == (0, 0)
            assert add(dot(shift, shift), scale(dot(delta, delta), F(40, 169))) == (1, 0)
            for r in range(3):
                relation.add((r, (r+2*sign*(u-v)) % 3))
            geometric_edges += 1
        assert relation == {(r, s) for r, s in product(range(3), repeat=2) if r != s}
    assert geometric_edges == 12

    # Independently prove the chosen next host actually leaves X. Solve all
    # possible core/lattice representations, rather than trusting SAT labels.
    root = root or Path(__file__).resolve().parents[1]
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    assert core['coordinate_denominator'] == 96 and len(core['points']) == 509
    members = {1: [], 3: []}
    for i, (x, y) in enumerate(core['points']):
        assert x[1] == y[0] == 0
        if any(v for axis in (x, y) for v in axis[2:]):
            continue
        a0, b0 = F(x[0]-y[1], 96), F(y[1], 48)
        for numerator in members:
            a, b = (numerator-13*a0)/7, -13*b0/7
            if a.denominator == b.denominator == 1:
                members[numerator].append((i, int(a), int(b)))
    assert members[3] == []
    assert (166, 2, 0) in members[1]  # 1/13 is NOT an outside-X witness.
    assert 6*7-3*13 == 3

    sequence = []
    for k in range(1, 33):
        modulus = 11**k
        t = (13*pow(3, -1, modulus)) % modulus
        displacement = 1-F(3*t, 13)
        assert displacement != 0
        assert displacement.numerator % modulus == 0
        assert displacement.denominator == 13
        sequence.append(dict(k=k, t=t))

    # Omitting the rainbow hypothesis would be false: three identity frames
    # allow exactly the off-diagonal pairs, not the equality relation.
    assert {(a, b) for a, b in product(range(5), repeat=2)
            if all(a != b for r, s in product(range(3), repeat=2) if r != s)} == {
                (a, b) for a, b in product(range(5), repeat=2) if a != b}
    # Nor does the five-color capacity argument extend to six colors.
    assert all(r != (3+s) % 6 for r, s in product(range(3), repeat=2))

    # A real infinite TWO-colorable strip exhibits the same local obstruction.
    # Height positivity gives |dm| <= 2 and |dk| <= 13, so these are all edges.
    strip_steps = [(m, k) for m in range(-2, 3) for k in range(-13, 14)
                   if 40*m*m+k*k == 169]
    assert set(strip_steps) == {(0, -13), (0, 13), (-2, -3), (-2, 3), (2, -3), (2, 3)}
    strip_checks = 0
    for dm, dk in strip_steps:
        for m, k in product(range(3), range(6)):
            assert k % 2 != (k+dk) % 2
            assert (k % 3+m % 3) % 5 != ((k+dk) % 3+(m+dm) % 3) % 5
            strip_checks += 1
    assert strip_checks == 108
    return dict(status='VERIFIED_CENTER_PALETTE_RIGIDITY_CALIBRATION',
                normalized_rainbow_palettes=palettes, palette_color_pairs=color_pairs,
                exact_N4_edges=geometric_edges, calibrated_precision_powers=len(sequence),
                saturated_host_outside_point='(3/13,0)', outside_core_candidates=509,
                first_period_multipliers=sequence[:4],
                infinite_strip_chromatic_number=2, strip_color_checks=strip_checks,
                scope='Written T075: rainbow palette rules force periods and are nowhere 11-adically continuous on K^2; no host lower bound')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
