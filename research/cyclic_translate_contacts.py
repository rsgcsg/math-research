"""Exact two-exponent Laurent zeros for a common base visible at a finite place.

The caller supplies exact field elements and an exact additive valuation.
No window, SAT solver, numerical root finder, or S-unit oracle is used.
The returned lines are *whole* affine integer lines, not bounded samples.
General completeness is proved in docs/proofs/cyclic_translate_effective.md.
"""
from itertools import combinations
from math import gcd


def integer(x, label):
    if type(x) is not int:
        raise ValueError(label + ' must be an integer (not bool)')
    return x


def bezout(a, b):
    """Return x,y with ax+by=gcd(a,b), for signed integers."""
    aa, bb = abs(a), abs(b)
    x0, x1, y0, y1 = 1, 0, 0, 1
    while bb:
        q, r = divmod(aa, bb)
        aa, bb = bb, r
        x0, x1 = x1, x0-q*x1
        y0, y1 = y1, y0-q*y1
    return x0 if a >= 0 else -x0, y0 if b >= 0 else -y0


def affine_line(a, b, c):
    """Canonical primitive equation A*n+B*m=C, or None if no integer point."""
    if a == b == 0:
        raise ValueError('a nontrivial line is required')
    g = gcd(a, b)
    if c % g:
        return None
    a, b, c = a//g, b//g, c//g
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


def parametrization(line):
    a, b, c = line
    x, y = bezout(a, b)
    n, m = c*x, c*y
    r, s = b, -a
    # Reduce the size of the origin on the line, using exact integer arithmetic.
    shift = -(n*r+m*s)//(r*r+s*s)
    n, m = n+r*shift, m+s*shift
    if a*n+b*m != c or gcd(r, s) != 1:
        raise AssertionError('invalid line parametrization')
    return (n, m), (r, s)


def evaluate(poly, u, n, m):
    return sum((c*u**(a*n+b*m) for (a, b), c in poly.items()), u-u)


def solve_laurent(poly, u, valuation):
    """Return an exact zero-set description and finite search accounting.

    `poly` maps exponent pairs to exact coefficients. `u` must be nonzero,
    with nonzero integer valuation. Zero-test, +, *, and integer powers must
    be exact. The validity of the valuation is a caller/proof hypothesis,
    not inferred from passing a few tests.
    """
    zero = u-u
    if u == zero:
        raise ValueError('zero base')
    d = integer(valuation(u), 'valuation of base')
    if not d:
        raise ValueError('base invisible at the supplied finite place')
    clean = {}
    for exp, c in poly.items():
        if (type(exp) is not tuple or len(exp) != 2 or
                any(type(i) is not int for i in exp)):
            raise ValueError('noninteger exponent pair')
        if c != zero:
            clean[exp] = c
    if not clean:
        return dict(all_integer_pairs=True, lines=[], points=[],
                    tested_lines=0, tested_parameters=0, root_degree_budget=0)
    entries = sorted(clean)
    values = {a: integer(valuation(clean[a]), 'coefficient valuation') for a in entries}
    cover = set()
    for a, b in combinations(entries, 2):
        line = affine_line(d*(a[0]-b[0]), d*(a[1]-b[1]), values[b]-values[a])
        if line is not None:
            cover.add(line)
    lines, points = set(), set()
    tested_parameters = degree_budget = 0
    for line in sorted(cover):
        (n, m), (r, s) = parametrization(line)
        restricted = {}
        for (a, b), c in clean.items():
            exponent = a*r+b*s
            restricted[exponent] = restricted.get(exponent, zero)+c*u**(a*n+b*m)
        restricted = {i: c for i, c in restricted.items() if c != zero}
        if not restricted:
            lines.add(line)
            continue
        degrees = sorted(restricted)
        degree_budget += max(degrees)-min(degrees)
        orders = {i: integer(valuation(restricted[i]), 'restricted valuation') for i in degrees}
        candidates = set()
        for a, b in combinations(degrees, 2):
            numerator, denominator = orders[b]-orders[a], d*(a-b)
            if numerator % denominator == 0:
                candidates.add(numerator//denominator)
        tested_parameters += len(candidates)
        for j in sorted(candidates):
            if sum((c*u**(i*j) for i, c in restricted.items()), zero) == zero:
                point = (n+r*j, m+s*j)
                if evaluate(clean, u, *point) != zero:
                    raise AssertionError('restriction inconsistency')
                points.add(point)
    points = {p for p in points if not any(a*p[0]+b*p[1] == c for a, b, c in lines)}
    return dict(all_integer_pairs=False, lines=[list(x) for x in sorted(lines)],
                points=[list(x) for x in sorted(points)], tested_lines=len(cover),
                tested_parameters=tested_parameters, root_degree_budget=degree_budget)


def contact_polynomial(a, b, t, bar):
    """Squared distance |a*x-(t+b*y)|^2 - 1, with x*bar(x)=y*bar(y)=1."""
    one = a**0
    return {(0, 0): a*bar(a)+b*bar(b)+t*bar(t)-one,
            (1, 0): -a*bar(t), (-1, 0): -bar(a)*t,
            (0, 1): b*bar(t), (0, -1): bar(b)*t,
            (1, -1): -a*bar(b), (-1, 1): -bar(a)*b}


def contacts(a, b, t, u, bar, valuation):
    """Complete contacts between a*u^Z and t+b*u^Z; a,b,t must be nonzero."""
    zero, one = u-u, u**0
    if any(z == zero for z in (a, b, t)):
        raise ValueError('zero radius or zero translation is a separate case')
    if u*bar(u) != one:
        raise ValueError('base must be a unit complex rotation')
    out = solve_laurent(contact_polynomial(a, b, t, bar), u, valuation)
    if out['all_integer_pairs']:
        raise AssertionError('nonzero contact polynomial vanished')
    for row in out['lines']:
        A, B, C = row
        if (A, B) == (1, 0):
            valid = a*u**C == t and b*bar(b) == one
        elif (A, B) == (0, 1):
            valid = b*u**C == -t and a*bar(a) == one
        elif (A, B) == (1, -1):
            valid = a*u**C == b and t*bar(t) == one
        else:
            valid = False
        if not valid:
            raise AssertionError('unexpected infinite family')
    if len(out['points']) > 54 or out['root_degree_budget'] > 54:
        raise AssertionError('hexagon degree bound violated')
    return out
