"""Independent T078/C014 checker: exact directions, residue formula, actual edges.

No producer or SAT imports. Infinite completeness comes from the written
ramified-prime proof. All-pair geometry at width 3 independently calibrates
the complete-direction compilation used for larger finite boxes.
"""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
from verify_cyclotomic_127 import multiply, conjugate, power


ONE = (1, 0, 0, 0, 0, 0)


def norm(a):
    return multiply(a, conjugate(a))


def f2_remainder(a, b):
    while a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length()-b.bit_length())
    return a


def calibrate():
    cases = ((2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3),
             (5, 1), (5, 2), (7, 1), (7, 2), (11, 1), (13, 1))
    for p, r in cases:
        assert all(p % j for j in range(2, math.isqrt(p)+1))
        step, degree = p**(r-1), (p-1)*p**(r-1)
        shifted = [sum((-1)**j*math.comb(t*step, j) for t in range(p) if t*step >= j)
                   for j in range(degree+1)]
        assert shifted[0] == p and shifted[0] % (p*p)
        assert abs(shifted[-1]) == 1 and all(x % p == 0 for x in shifted[:-1])
        word = [0, 1] if p == 2 else [j % 2 for j in range(p-1)]+[2]
        assert all(word[j] != word[(j+1) % p] for j in range(p))
    alpha = (1, 1, 1, 0, 1, 0)
    assert norm(alpha) == (2, 0, 0, 0, 0, 0)
    # Phi_7 mod 2 has two irreducible cubics. Alpha vanishes in exactly one.
    a, b = 0b1011, 0b1101
    value = 0
    for j in range(4):
        if b >> j & 1:
            value ^= a << j
    assert value == 0b1111111
    assert all(f & 1 and bin(f).count('1') % 2 for f in (a, b))
    assert f2_remainder(0b10111, a) == 1 and f2_remainder(0b10111, b) == 0
    bar_mask = sum((x % 2) << j for j, x in enumerate(conjugate(alpha)))
    assert f2_remainder(bar_mask, a) == 0 and f2_remainder(bar_mask, b) == 1
    v2 = (-1, 1, 1, 0, 1, 0)
    assert multiply(alpha, alpha) == v2
    # No conjugation-stable prime over 7 can extend to F containing sqrt(-3).
    assert {x for x in range(7) if (x*x+3) % 7 == 0} == {2, 5}
    return len(cases)


def directions():
    # For n/2 to have norm 1, its trace energy is 24. With a_6=0,
    # each |a_i| <= sqrt(24) < 5. This is a proved exhaustive integer box.
    found = set()
    trace_candidates = 0
    for a in product(range(-4, 5), repeat=6):
        if 7*sum(x*x for x in a)-sum(a)**2 != 24:
            continue
        trace_candidates += 1
        if norm(a) == (4, 0, 0, 0, 0, 0):
            found.add(a)
    assert len(found) == 42
    return found, trace_candidates


def decompose(a):
    a = Fraction(a)
    ppart, other = 1, a.denominator
    while other % 7 == 0:
        ppart *= 7
        other //= 7
    representative = Fraction((a.numerator*pow(other, -1, ppart)) % ppart, ppart)
    integral = a-representative
    assert integral.denominator % 7
    return representative, integral.numerator*pow(integral.denominator, -1, 7) % 7


def field_color(point, word):
    return word[sum(decompose(a)[1] for a in point) % 7]


def solve_division(a, b):
    """Return a/b by rational Gaussian elimination, no symbolic dependencies."""
    cols = [multiply(b, power(j)) for j in range(6)]
    rows = [[Fraction(cols[j][i]) for j in range(6)]+[Fraction(a[i])] for i in range(6)]
    for j in range(6):
        pivot = next(i for i in range(j, 6) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        q = rows[j][j]
        rows[j] = [x/q for x in rows[j]]
        for i in range(6):
            if i != j:
                q = rows[i][j]
                rows[i] = [x-q*y for x, y in zip(rows[i], rows[j])]
    answer = tuple(row[-1] for row in rows)
    assert multiply(answer, b) == a
    return answer


def fractional_checks(word, ds):
    checks = 0
    for depth in range(1, 5):
        for residue in range(7):
            point = tuple(Fraction(j+1, 7**depth)+Fraction(residue if j == 0 else 0, 1)
                          for j in range(6))
            for a in ds:
                other = tuple(x+Fraction(y, 2) for x, y in zip(point, a))
                assert [decompose(x)[0] for x in point] == [decompose(x)[0] for x in other]
                assert field_color(point, word) != field_color(other, word)
                checks += 1
    pi = (1, -1, 0, 0, 0, 0)
    samples = 0
    for k in range(1, 25):
        a = tuple((k*(j+2)+j*j) % 11-5 for j in range(6))
        for _ in range(k % 7):
            a = multiply(a, pi)
        a = tuple(Fraction(x, 7**(k % 4)) for x in a)
        w = solve_division(a, conjugate(a))
        assert norm(w) == ONE
        assert all(x.denominator % 7 for x in w)
        assert sum(x.numerator*pow(x.denominator, -1, 7) for x in w) % 7 in (1, 6)
        samples += 1
    return checks, samples


def verify_data(data):
    assert __debug__, 'Do not disable assertions when verifying mathematical certificates.'
    assert data['schema'] == 1 and data['theorem'] == 'T078' and data['counterexample'] == 'C014'
    assert data['basis'] == '1,z,z^2,z^3,z^4,z^5; Phi_7(z)=0'
    assert data['denominator'] == 2
    word = data['cycle_word']
    assert word == [0, 1, 0, 1, 0, 1, 2]
    ds, candidates = directions()
    assert data['direction_numerators'] == [list(a) for a in sorted(ds)]
    for a in ds:
        assert 4*sum(a) % 7 in (1, 6)
    valid_additive = [w for w in product(range(3), repeat=6)
                      if all(sum(x*y for x, y in zip(w, a)) % 3 for a in ds)]
    assert valid_additive == []
    assert sum(all(x % 2 == 0 for x in a) for a in ds) == 14
    positive = [a for a in ds if a > (0,)*6]
    assert len(positive) == 21
    summaries = []
    assert [p['width'] for p in data['probes']] == [2, 3, 4, 5, 6]
    for probe in data['probes']:
        width = probe['width']
        strides = [width**j for j in range(5, -1, -1)]
        edges = []
        for a in positive:
            gain = sum(x*y for x, y in zip(a, strides))
            for p in product(*(range(max(0, -d), min(width, width-d)) for d in a)):
                i = sum(x*y for x, y in zip(p, strides))
                edges.append((i, i+gain))
        edges.sort()
        points = list(product(range(width), repeat=6))
        colors = [word[4*sum(p) % 7] for p in points]
        assert len(points) == probe['vertices'] and len(edges) == probe['edges']
        assert all(colors[i] != colors[j] for i, j in edges)
        assert hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest() == probe['edge_sha256']
        assert hashlib.sha256(bytes(colors)).hexdigest() == probe['word_sha256']
        if width == 3:
            norms, actual = {}, []
            for i, j in combinations(range(len(points)), 2):
                delta = tuple(x-y for x, y in zip(points[j], points[i]))
                if delta not in norms:
                    norms[delta] = norm(delta) == (4, 0, 0, 0, 0, 0)
                if norms[delta]:
                    actual.append((i, j))
            assert actual == edges
        summaries.append(dict(width=width, vertices=len(points), edges=len(edges)))
    shifts, samples = fractional_checks(word, ds)
    return dict(dyadic_unit_directions=42, trace_box_candidates=9**6,
                trace_energy_candidates=candidates, additive_three_color_weights_rejected=3**6,
                actual_pair_calibration=729*728//2, probes=summaries,
                nonintegral_coset_edge_checks=shifts, rational_norm_one_samples=samples)


def verify(root):
    if not __debug__:
        raise RuntimeError('Do not disable assertions when verifying mathematical certificates.')
    data = json.loads((root/'certificates/cyclotomic_field_coloring.json').read_text())
    return dict(cyclotomic_field=dict(prime_power_calibrations=calibrate(), **verify_data(data)),
                scope='Written T078: Q(zeta_(p^r)) as a subset of C has chromatic number 2 or 3; not F+L or the plane')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
