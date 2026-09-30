#!/usr/bin/env python3
"""Exact integer calibration in Z[t]/(t^3+t-1); not an infinite proof."""
import argparse
import hashlib
import json
from pathlib import Path

ZERO = (0, 0, 0)
ONE = (1, 0, 0)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def mul(a, b):
    out = [0] * 5
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    # t^3 = 1-t, so t^j = t^(j-3)-t^(j-2).
    for j in (4, 3):
        out[j - 3] += out[j]
        out[j - 2] -= out[j]
        out[j] = 0
    return tuple(out[:3])


def cmul(a, b):
    x, y = a
    z, w = b
    return add(mul(x, z), neg(mul(y, w))), add(mul(x, w), mul(y, z))


def norm(a):
    return add(mul(a[0], a[0]), mul(a[1], a[1]))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compute():
    theta = (0, 1, 0)
    require(add(mul(mul(theta, theta), theta), theta) == ONE, 'cubic relation')
    u = ((-1, 2, 0), (0, 0, 2))
    require(norm(u) == ONE, 'generator norm')
    require(cmul(u, (u[0], neg(u[1]))) == (ONE, ZERO), 'integral inverse')
    # p(z)=z^6+6z^5+31z^4-12z^3+31z^2+6z+1.
    coefficients = (1, 6, 31, -12, 31, 6, 1)
    value = (ZERO, ZERO)
    for c in coefficients:
        value = cmul(value, u)
        value = (add(value[0], (c, 0, 0)), value[1])
    require(value == (ZERO, ZERO), 'reciprocal polynomial identity')
    points = []
    current = (ONE, ZERO)
    for exponent in range(65):
        require(norm(current) == ONE, 'power has wrong norm')
        require(current not in points, 'duplicate power in finite calibration')
        require(all(type(c) is int for a in current for c in a), 'noninteger coefficient')
        points.append(current)
        current = cmul(current, u)
    altered = ((0, 2, 0), (0, 0, 2))
    require(norm(altered) != ONE, 'corrupted generator unexpectedly accepted')
    raw = json.dumps(points, separators=(',', ':')).encode()
    return dict(status='PASS', field_polynomial_descending=[1, 0, 1, -1],
                coefficient_order='constant,t,t^2', generator=u,
                unit_polynomial_descending=coefficients,
                exponents_checked=[0, 64], distinct_integral_points=len(points),
                point_sequence_sha256=hashlib.sha256(raw).hexdigest(),
                first_eight_points=points[:8], mutation_rejected='changed-generator-constant',
                scope='Finite exact calibration only. Infinitude and density use the written non-torsion proof; no HN bound.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    report = compute()
    path = Path(__file__).resolve().parents[1] / 'certificates/cubic_unit_directions.json'
    raw = json.dumps(report, indent=2) + '\n'
    if args.write_certificate:
        path.write_text(raw)
    else:
        require(json.loads(path.read_text()) == json.loads(raw), 'saved certificate differs')
    print(raw, end='')


if __name__ == '__main__':
    main()
