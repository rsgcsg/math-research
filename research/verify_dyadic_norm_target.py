"""Exact small calibrations for the dyadic norm-congruence target ceiling.

This does not enumerate the enormous GR(2**h, 4) graph or certify a source
unit-distance lower bound. The all-h argument is the accompanying proof.
"""
from collections import Counter
import json


def verify():
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')

    def multiply(a, b):
        result = 0
        while b:
            if b & 1:
                result ^= a
            a <<= 1
            b >>= 1
            if a & 16:
                a ^= 19
        return result

    def power(a, n):
        result = 1
        for _ in range(n):
            result = multiply(result, a)
        return result

    def trace(a):
        value = a ^ power(a, 2) ^ power(a, 4) ^ power(a, 8)
        assert value in (0, 1)
        return value

    inverses = {x: next(y for y in range(1, 16) if multiply(x, y) == 1)
                for x in range(1, 16)}
    kloosterman = {
        (a, b): sum(1-2*trace(multiply(a, x) ^ multiply(b, inverses[x]))
                    for x in range(1, 16))
        for a in range(16) for b in range(16)
    }
    assert kloosterman[0, 0] == 15
    assert all(kloosterman[0, b] == kloosterman[b, 0] == -1
               for b in range(1, 16))
    unit_distribution = Counter(kloosterman[a, b]
                                for a in range(1, 16) for b in range(1, 16))
    assert min(unit_distribution) == -5
    minimum_pair = next((a, b) for (a, b), value in kloosterman.items() if value == -5)

    # Independent q=2 calibrations: directly enumerate every direction and
    # every additive character of Z/(2**h), using exact cyclotomic reduction.
    # No floating-point FFT, stationary-phase formula, or production graph.
    small_rings = []
    for c, h in ((0, 1), (2, 3), (2, 4), (4, 5), (4, 6)):
        modulus = 1 << h
        half = modulus >> 1
        directions = [(x, y) for x in range(modulus) for y in range(modulus)
                      if x*y % modulus == (1 << c)]
        degree = len(directions)
        assert degree == (c+1)*(1 << (h-1))
        spectrum = Counter()
        for a in range(modulus):
            for b in range(modulus):
                coefficients = [0]*half
                for x, y in directions:
                    exponent = (a*x+b*y) % modulus
                    coefficients[exponent % half] += 1 if exponent < half else -1
                # Phi_(2**h)(X) = X**half + 1, so this is exact evaluation
                # in Q(zeta_(2**h)), not a rounded numerical spectrum.
                assert all(value == 0 for value in coefficients[1:])
                spectrum[coefficients[0]] += 1
        expected_min = -1 if c == 0 else -2*(1 << (h-1))
        assert min(spectrum) == expected_min
        assert sum(spectrum.values()) == modulus**2
        assert sum(value*count for value, count in spectrum.items()) == 0
        assert sum(value*value*count for value, count in spectrum.items()) == modulus**2*degree
        small_rings.append(dict(q=2, norm_exponent=c, modulus_exponent=h,
                                vertices=modulus**2, degree=degree,
                                least_eigenvalue=min(spectrum),
                                exact_spectrum=dict(sorted(spectrum.items()))))

    return dict(status='PASS', field_modulus_bits=19,
                finite_field_character_pairs=256,
                unit_kloosterman_distribution=dict(sorted(unit_distribution.items())),
                unit_kloosterman_minimum=-5, minimum_pair=minimum_pair,
                independent_small_rings=small_rings,
                proved_target_bounds=[dict(norm_exponent=c, minimum_precision=c+1,
                                           chromatic_lower_bound=3*c+4)
                                      for c in (0, 2, 4)],
                scope='Calibrates the written all-precision congruence-target proof; '
                      'no lower bound on the real unit-distance source is inferred.')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
