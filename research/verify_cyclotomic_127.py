"""Independent exact checks for T077: separated units and 127-local directions.

No search/constructor imports, no floating arithmetic. Completeness for the
infinite hosts is the written field and ideal proof, not this finite replay.
"""
from itertools import product
from pathlib import Path
import hashlib
import json


ONE = (1, 0, 0, 0, 0, 0)


def power(j):
    j %= 7
    return (-1,)*6 if j == 6 else tuple(int(i == j) for i in range(6))


def multiply(a, b):
    # Circular convolution modulo z^7-1, then quotient by Phi_7.
    c = [0]*7
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[(i+j) % 7] += x*y
    return tuple(x-c[6] for x in c[:6])


def conjugate(a):
    return tuple(sum(x*power(-j)[i] for j, x in enumerate(a)) for i in range(6))


def factors():
    return {j: tuple(2*x-y for x, y in zip(ONE, power(j))) for j in range(1, 7)}


def calibrate():
    # Each nontrivial real square class s has a local obstruction to s*r^2+7*b^2=1.
    obstructions = {3: (7, 3), 5: (5, 7), 11: (11, 7), 15: (5, 7),
                    33: (11, 7), 55: (11, 7), 165: (11, 7)}
    classes = {3**a*5**b*11**c for a, b, c in product(range(2), repeat=3)}
    assert set(obstructions) == classes-{1}
    for s, (p, nonsquare) in obstructions.items():
        assert nonsquare % p not in {x*x % p for x in range(p)}
        ramified, unramified = (7, s) if p == 7 else (s, 7)
        assert ramified % p == 0 and ramified % (p*p) != 0 and unramified % p
        assert unramified == nonsquare
    fs = factors()
    total = ONE
    for j in range(1, 7):
        total = multiply(total, fs[j])
    assert total == (127, 0, 0, 0, 0, 0)
    assert all(127 % d for d in range(2, 12))
    # Explicit six distinct residue maps; no class-number assumption.
    roots = [pow(2, pow(j, -1, 7), 127) for j in range(1, 7)]
    assert len(set(roots)) == 6
    for j, t in enumerate(roots, 1):
        assert sum(pow(t, k, 127) for k in range(7)) % 127 == 0
        assert [k for k in range(1, 7) if (2-pow(t, k, 127)) % 127 == 0] == [j]
    # In O/3O the six factors are invertible and bar(alpha_j)=z^-j alpha_j.
    for j in range(1, 7):
        assert tuple(x % 3 for x in conjugate(fs[j])) == tuple(
            x % 3 for x in multiply(power(-j), fs[j]))
    weights = (1, 1, 1, 1, 1, 2)
    assert all(sum(x*y for x, y in zip(weights, power(j))) % 3 for j in range(7))
    # Closed seven-edge walk has distinct first seven vertices and odd length.
    point = (0,)*6
    cycle = []
    for j in range(7):
        cycle.append(point)
        point = tuple(x+y for x, y in zip(point, power(j)))
    assert point == (0,)*6 and len(set(cycle)) == 7
    return dict(square_class_obstructions=len(obstructions), prime=127,
                prime_residue_roots=roots, localization_three_color_weights=list(weights),
                odd_cycle_vertices=7)


def verify_data(data):
    assert __debug__, 'Do not disable assertions when verifying mathematical certificates.'
    assert data['schema'] == 1 and data['theorem'] == 'T077' and data['denominator'] == 127
    assert data['basis'] == '1,z,z^2,z^3,z^4,z^5; Phi_7(z)=0'
    assert data['convention'] == 'r_j=(2-z^(-j))/(2-z^j), j=1,2,3'
    fs = factors()
    labels, directions = set(), set()
    for record in data['directions']:
        e = tuple(record['exponents'])
        k, sign = record['root_power'], record['sign']
        assert len(e) == 3 and all(type(x) is int and x in (-1, 0, 1) for x in e)
        assert type(k) is int and 0 <= k < 7 and type(sign) is int and sign in (-1, 1)
        label = e, k, sign
        assert label not in labels
        labels.add(label)
        a = tuple(record['numerator'])
        assert len(a) == 6 and all(type(x) is int for x in a)
        assert a not in directions
        directions.add(a)
        # Cross multiplication checks the label without rational inversion.
        left, right = a, tuple(sign*127*x for x in power(k))
        for j, exponent in enumerate(e, 1):
            if exponent:
                numerator, denominator = (7-j, j) if exponent == 1 else (j, 7-j)
                left = multiply(left, fs[denominator])
                right = multiply(right, fs[numerator])
        assert left == right
        assert multiply(a, conjugate(a)) == (127**2, 0, 0, 0, 0, 0)
        assert 7*sum(x*x for x in a)-sum(a)**2 == 6*127**2
        assert sum(x*y for x, y in zip((1, 1, 1, 1, 1, 2), a)) % 3
    expected = {(e, k, s) for e in product((-1, 0, 1), repeat=3)
                for k in range(7) for s in (-1, 1)}
    assert labels == expected and len(directions) == 378
    assert (-65, 93, 45, 21, 9, 3) in directions
    assert {tuple(-x for x in a) for a in directions} == directions
    assert {conjugate(a) for a in directions} == directions
    assert sum(all(x % 127 == 0 for x in a) for a in directions) == 14
    assert len({tuple(x % 3 for x in a) for a in directions}) == 14
    quadratic = {a for a in directions if a[1] == a[2] == a[4] and a[3] == a[5] == 0}
    assert quadratic == {(-127, 0, 0, 0, 0, 0), (127, 0, 0, 0, 0, 0),
                         (47, 96, 96, 0, 96, 0), (49, 96, 96, 0, 96, 0),
                         (-47, -96, -96, 0, -96, 0), (-49, -96, -96, 0, -96, 0)}
    assert 1+7*48**2 == 127**2 and 7*(2*48)**2 > 127**2
    raw = json.dumps(sorted(directions), separators=(',', ':')).encode()
    return dict(direction_count=378, old_root_directions=14, new_directions=364,
                mod3_directions=14, quadratic_directions=len(quadratic),
                sorted_numerators_sha256=hashlib.sha256(raw).hexdigest())


def verify(root):
    if not __debug__:
        raise RuntimeError('Do not disable assertions when verifying mathematical certificates.')
    path = root/'certificates/cyclotomic_127_directions.json'
    return dict(cyclotomic_127=dict(**calibrate(), **verify_data(json.loads(path.read_text()))))


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
