"""Independent checker for E096 cyclic and full rational rotation orbits.

This imports only the previously independent E091 multiplication/checker, not
the E096 producer.  All rational angles are obtained by solving the full field
coefficient equations.  Gaussian valuation then extracts the only possible
power of (3+4i)/5, which is checked by exact exponentiation.
The complete angle list also certifies that the full rational-rotation
saturation splits into disjoint copies of the finite antipodal block.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
from itertools import product as cartesian_product
import json
from math import isqrt, lcm
from pathlib import Path

from verify_cm_escape_nine import check_data as check_source, product


ZERO = (Q(0),) * 8
ONE = (Q(1),) + (Q(0),) * 7
ROTATION = (Q(3, 5), Q(4, 5))


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def subtract(x, y):
    return tuple(a - b for a, b in zip(x, y))


def scale(a, x):
    return tuple(a * v for v in x)


def complex_product(z, w):
    a, b = z
    c, d = w
    return a * c - b * d, a * d + b * c


def rotation_power(n):
    base = ROTATION if n >= 0 else (ROTATION[0], -ROTATION[1])
    value = (Q(1), Q(0))
    n = abs(n)
    while n:
        if n & 1:
            value = complex_product(value, base)
        base = complex_product(base, base)
        n //= 2
    return value


def gaussian_power_index(z):
    """Return n iff z=((2+i)/(2-i))**n, with no exponent enumeration."""
    x, y = z
    assert x * x + y * y == 1
    denominator = lcm(x.denominator, y.denominator)
    a, b = int(x * denominator), int(y * denominator)
    numerator_order = 0
    assert a or b
    while (2 * a + b) % 5 == 0 and (2 * b - a) % 5 == 0:
        a, b = (2 * a + b) // 5, (2 * b - a) // 5
        numerator_order += 1
    denominator_order = 0
    while denominator % 5 == 0:
        denominator //= 5
        denominator_order += 1
    candidate = numerator_order - denominator_order
    return candidate if rotation_power(candidate) == z else None


def rational_sqrt(x):
    if x < 0:
        return None
    a, b = isqrt(x.numerator), isqrt(x.denominator)
    return Q(a, b) if a * a == x.numerator and b * b == x.denominator else None


def unit_circle_solutions(equations):
    """Exact rational solutions of A*c+B*s=C and c*c+s*s=1.

    The two-variable row reduction is intentionally independent of producer
    elimination.  Returned rank classifications document exhaustiveness.
    """
    rows = [tuple(map(Q, row)) for row in equations]
    if any(a == b == 0 and c != 0 for a, b, c in rows):
        return [], 'inconsistent'
    active = [row for row in rows if row[0] or row[1]]
    assert active, 'Nonzero source points must not give unconstrained angles'
    a, b, c = active[0]
    independent = next((row for row in active[1:] if a * row[1] != b * row[0]), None)
    if independent is not None:
        d, e, f = independent
        determinant = a * e - b * d
        x, y = (c * e - b * f) / determinant, (a * f - c * d) / determinant
        if any(A * x + B * y != C for A, B, C in rows):
            return [], 'inconsistent'
        return ([(x, y)] if x * x + y * y == 1 else []), 'rank2'
    if any(a * C != A * c or b * C != B * c for A, B, C in active):
        return [], 'inconsistent'
    norm = a * a + b * b
    radical = rational_sqrt(norm - c * c)
    if radical is None:
        return [], 'rank1_no_rational_intersection'
    candidates = {
        ((a * c + sign * b * radical) / norm,
         (b * c - sign * a * radical) / norm)
        for sign in (-1, 1)
    }
    assert all(x * x + y * y == 1 for x, y in candidates)
    assert all(A * x + B * y == C for x, y in candidates for A, B, C in rows)
    return sorted(candidates), 'rank1_rational_intersection'


def rotate_point(q, angle):
    c, s = angle
    x, y = q
    return subtract(scale(c, x), scale(s, y)), add(scale(s, x), scale(c, y))


def distance_square(p, q):
    dx, dy = subtract(p[0], q[0]), subtract(p[1], q[1])
    return add(product(dx, dx), product(dy, dy))


def derive(source):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    check_source(source)
    points = [tuple(tuple(Q(c) for c in axis) for axis in p) for p in source['coordinates']]
    assert all(p != (ZERO, ZERO) for p in points)
    norms = [add(product(x, x), product(y, y)) for x, y in points]
    edges, identifications, contacts = [], [], []
    edge_cases, equality_cases = Counter(), Counter()
    rational_edge_angles = rational_equality_angles = 0
    for i, j in cartesian_product(range(len(points)), repeat=2):
        px, py = points[i]
        qx, qy = points[j]
        A = scale(2, add(product(px, qx), product(py, qy)))
        B = scale(2, subtract(product(py, qx), product(px, qy)))
        C = subtract(add(norms[i], norms[j]), ONE)
        solutions, case = unit_circle_solutions(zip(A, B, C))
        edge_cases[case] += 1
        rational_edge_angles += len(solutions)
        unit_angles = []
        for angle in solutions:
            assert distance_square(points[i], rotate_point(points[j], angle)) == ONE
            n = gaussian_power_index(angle)
            unit_angles.append(dict(c=str(angle[0]), s=str(angle[1]), exponent=n))
            if n is not None:
                edges.append([i, j, n])
        equations = list(zip(qx, scale(-1, qy), px)) + list(zip(qy, qx, py))
        solutions, case = unit_circle_solutions(equations)
        equality_cases[case] += 1
        rational_equality_angles += len(solutions)
        equality_angles = []
        for angle in solutions:
            assert points[i] == rotate_point(points[j], angle)
            n = gaussian_power_index(angle)
            equality_angles.append(dict(c=str(angle[0]), s=str(angle[1]), exponent=n))
            if n is not None:
                identifications.append([i, j, n])
        contacts.append(dict(pair=[i, j], unit_angles=unit_angles,
                             equality_angles=equality_angles))
    edges.sort()
    identifications.sort()
    assert all([j, i, -n] in edges for i, j, n in edges)
    assert all([j, i, -n] in identifications for i, j, n in identifications)
    return dict(edges=edges, identifications=identifications, contacts=contacts,
                distance_pair_cases=dict(sorted(edge_cases.items())),
                equality_pair_cases=dict(sorted(equality_cases.items())),
                rational_edge_angles=rational_edge_angles,
                rational_equality_angles=rational_equality_angles)


def check_saturation(data, source, contacts):
    """Check all rational rotations, not just the selected cyclic subgroup.

    Every inter-copy contact or overlap has a rational relative angle, already
    exhausted in contacts.  If only +/-1 occur, cosets modulo +/-1 do not
    intersect or share an edge.  A directly checked S union -S coloring can
    therefore be used separately on each such finite block.
    """
    unit_angles = {(Q(angle['c']), Q(angle['s']))
                   for row in contacts for angle in row['unit_angles']}
    equality_angles = {(Q(angle['c']), Q(angle['s']))
                       for row in contacts for angle in row['equality_angles']}
    antipodal_angles = {(Q(1), Q(0)), (Q(-1), Q(0))}
    assert unit_angles <= antipodal_angles
    assert equality_angles <= antipodal_angles
    points = [tuple(tuple(Q(c) for c in axis) for axis in p) for p in source['coordinates']]
    block = sorted({tuple(scale(sign, axis) for axis in p)
                    for sign in (-1, 1) for p in points})
    assert len(block) == 16
    assert data['block'] == 'S union -S'
    assert data['vertices'] == len(block)
    assert data['all_pairs'] == len(block) * (len(block) - 1) // 2 == 120
    edges = [[i, j] for i in range(len(block)) for j in range(i + 1, len(block))
             if distance_square(block[i], block[j]) == ONE]
    assert len(edges) == 29 and data['edges'] == edges
    assert data['colors'] == 4
    word = data['word']
    assert len(word) == len(block)
    assert all(type(c) is int and 0 <= c < 4 for c in word)
    assert all(word[i] != word[j] for i, j in edges)
    return dict(all_rational_unit_angles_antipodal=True,
                all_rational_equality_angles_antipodal=True,
                antipodal_block_vertices=16, antipodal_block_all_pairs=120,
                antipodal_block_actual_edges=29,
                full_rational_rotation_saturation_four_coloring=True)


def check_data(data, source_raw):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E096'
    assert data['source_sha256'] == hashlib.sha256(source_raw).hexdigest()
    assert data['rotation'] == dict(real='3/5', imaginary='4/5',
                                    gaussian_prime=[2, 1], valuation_of_rotation=1)
    assert data['seed_count'] == 9 and data['all_ordered_pairs'] == 81
    source = json.loads(source_raw)
    derived = derive(source)
    assert data['unit_offsets'] == derived['edges']
    assert data['equality_offsets'] == derived['identifications']
    contacts = derived.pop('contacts')
    assert data['contacts'] == contacts
    saturation_report = check_saturation(data['rational_rotation_saturation'], source, contacts)
    periodic = data['periodic_certificate']
    period = periodic['period']
    assert type(period) is int and period == 1
    assert periodic['colors'] == 4
    words = [periodic['word']]
    assert all(len(word) == 9 and all(type(c) is int and 0 <= c < 4 for c in word)
               for word in words)
    edge_obligations = equality_obligations = 0
    for k in range(period):
        for i, j, n in derived['edges']:
            assert words[k][i] != words[(k + n) % period][j]
            edge_obligations += 1
        for i, j, n in derived['identifications']:
            assert words[k][i] == words[(k + n) % period][j]
            equality_obligations += 1
    return dict(status='PASS', experiment='E096', source_vertices=9,
                all_ordered_pairs=81, distance_coefficient_equations=648,
                equality_coefficient_equations=1296, exponent_scan_used=False,
                **derived, period=period, colors=4,
                edge_obligations=edge_obligations, equality_obligations=equality_obligations,
                complete_infinite_orbit_four_coloring=True,
                **saturation_report,
                scope='Full rational-rotation saturation and cyclic orbit; '
                      'not all algebraic rotations or the whole coordinate field; no HN bound change.')


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    source_raw = (root / 'certificates/cm_escape_nine.json').read_bytes()
    raw = (root / 'certificates/rational_rotation_orbit.json').read_bytes()
    report = check_data(json.loads(raw), source_raw)
    report['certificate_sha256'] = hashlib.sha256(raw).hexdigest()
    return report


def mutation_test(root):
    source_raw = (root / 'certificates/cm_escape_nine.json').read_bytes()
    data = json.loads((root / 'certificates/rational_rotation_orbit.json').read_bytes())
    check_data(data, source_raw)
    mutations = []
    bad = deepcopy(data)
    bad['source_sha256'] = '0' * 64
    mutations.append(bad)
    bad = deepcopy(data)
    bad['unit_offsets'].pop()
    mutations.append(bad)
    bad = deepcopy(data)
    bad['equality_offsets'].append([0, 1, 0])
    mutations.append(bad)
    bad = deepcopy(data)
    bad['unit_offsets'][0][2] = 1
    mutations.append(bad)
    bad = deepcopy(data)
    i, j, n = bad['unit_offsets'][0]
    bad['periodic_certificate']['word'][j] = bad['periodic_certificate']['word'][i]
    mutations.append(bad)
    bad = deepcopy(data)
    bad['contacts'][0]['unit_angles'].pop()
    mutations.append(bad)
    bad = deepcopy(data)
    bad['rational_rotation_saturation']['edges'].pop()
    mutations.append(bad)
    bad = deepcopy(data)
    saturation = bad['rational_rotation_saturation']
    i, j = saturation['edges'][0]
    saturation['word'][j] = saturation['word'][i]
    mutations.append(bad)
    for bad in mutations:
        try:
            check_data(bad, source_raw)
        except (AssertionError, RuntimeError, ValueError):
            continue
        raise AssertionError('Mutated certificate was accepted')
    return len(mutations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--analyze', action='store_true')
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.analyze:
        result = derive(json.loads((root / 'certificates/cm_escape_nine.json').read_bytes()))
    else:
        result = verify(root)
        if args.mutations:
            result['rejected_mutations'] = mutation_test(root)
    print(json.dumps(result, indent=2))
