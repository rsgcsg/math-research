"""Independent exact q=2 calibration of the genuinely liftable local target.

The all-q16/all-h theorem and global direction lifting are written proofs.
This checker does not import the ordinary congruence-target checker.
"""
import json


def verify():
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    reports = []
    for c, h in ((2, 3), (2, 4), (4, 5), (4, 6)):
        modulus = 1 << h

        def valuation(x):
            return (x & -x).bit_length()-1 if x else h

        directions = {}
        for x in range(modulus):
            for y in range(modulus):
                r, t = valuation(x), valuation(y)
                if r+t != c:
                    continue
                m = min(r, t)
                if (x*y-(1 << c)) % (1 << (h+m)) == 0:
                    directions[x, y] = 1 << m

        parametrized = {}
        for r in range(c+1):
            m = min(r, c-r)
            for u in range(1, 1 << (h-m), 2):
                pair = ((1 << r)*u % modulus,
                        (1 << (c-r))*pow(u, -1, modulus) % modulus)
                assert pair not in parametrized
                parametrized[pair] = 1 << m
        assert directions == parametrized
        assert (0, 0) not in directions
        assert all(directions.get((-x % modulus, -y % modulus)) == weight
                   for (x, y), weight in directions.items())
        degree = sum(directions.values())
        assert degree == (c+1)*(1 << (h-1))

        # Integer reduction modulo Phi_(2**h)(X)=X**(2**(h-1))+1.
        # Some genuine-target characters are nonintegral (already at c4,h6).
        # The triangle bound below certifies their lower bound without
        # rounding roots of unity or pretending that their spectra are integers.
        floor = -2*(1 << (h-1))
        certified_minimum = None
        attained_integer_minimum = None
        nonintegral_characters = 0
        for a in range(modulus):
            for b in range(modulus):
                half = modulus >> 1
                coefficients = [0]*half
                for (x, y), weight in directions.items():
                    exponent = (a*x+b*y) % modulus
                    coefficients[exponent % half] += weight if exponent < half else -weight
                lower = coefficients[0]-sum(abs(value) for value in coefficients[1:])
                assert lower >= floor
                certified_minimum = lower if certified_minimum is None else min(certified_minimum, lower)
                if any(coefficients[1:]):
                    nonintegral_characters += 1
                else:
                    value = coefficients[0]
                    attained_integer_minimum = value if attained_integer_minimum is None else min(attained_integer_minimum, value)
        assert certified_minimum == attained_integer_minimum == floor
        reports.append(dict(q=2, norm_exponent=c, modulus_exponent=h,
                            vertices=modulus**2, directions=len(directions),
                            weighted_degree=degree, exact_least_eigenvalue=floor,
                            nonintegral_characters=nonintegral_characters,
                            condition_equals_parameterization=True))
    return dict(status='PASS', local_liftable_calibrations=reports,
                scope='Exact small q=2 weighted target checks only; '
                      'the q=16 finite-precision ceiling and global direction lifting '
                      'are the accompanying written proofs, not ordinary source chromatic lower bounds.')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
