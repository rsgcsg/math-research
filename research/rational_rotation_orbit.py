"""Exact all-integer offsets for a rational rotation of the E091 nine points.

No exponent cutoff: rational circle intersections followed by Gaussian-prime
valuation decide membership in <(3+4i)/5>. A periodic positive coloring is
then checked on the complete offset set. Independent checker is separate.
"""

from fractions import Fraction as Q
from itertools import product as cartesian
from math import isqrt, lcm
from pathlib import Path
import hashlib
import json

from cm_escape_nine_probe import add, sub, mul, ZERO, ONE, color


def scale(a, v):
    return tuple(a*x for x in v)


def rational_sqrt(a):
    if a < 0:
        return None
    m, n = isqrt(a.numerator), isqrt(a.denominator)
    return Q(m, n) if m*m == a.numerator and n*n == a.denominator else None


def circle_solutions(rows):
    """All rational (c,s) on c^2+s^2=1 satisfying rational linear rows."""
    rows = list(rows)
    if any(not a and not b and d for a, b, d in rows):
        return []
    pivot = next(((a, b, d) for a, b, d in rows if a or b), None)
    if pivot is None:
        raise ValueError('Whole circle requires a separate zero-point treatment')
    a, b, d = pivot
    candidates = None
    for e, f, g in rows:
        det = a*f - b*e
        if det:
            candidates = [(Q(d*f-b*g, det), Q(a*g-d*e, det))]
            break
    if candidates is None:
        norm = a*a+b*b
        root = rational_sqrt(norm-d*d)
        if root is None:
            return []
        candidates = [(Q(a*d-b*sign*root, norm), Q(b*d+a*sign*root, norm))
                      for sign in (-1, 1)]
    return sorted({(c, s) for c, s in candidates
                   if c*c+s*s == 1 and all(a*c+b*s == d for a, b, d in rows)})


def cmul(a, b):
    x, y = a
    u, v = b
    return x*u-y*v, x*v+y*u


def rotation_power(n):
    base = (Q(3, 5), Q(4 if n >= 0 else -4, 5))
    result = (Q(1), Q(0))
    n = abs(n)
    while n:
        if n & 1:
            result = cmul(result, base)
        base = cmul(base, base)
        n //= 2
    return result


def power_index(pair):
    c, s = pair
    assert c*c+s*s == 1
    den = lcm(c.denominator, s.denominator)
    a, b = int(den*c), int(den*s)
    count = 0
    while (2*a+b) % 5 == 0 and (2*b-a) % 5 == 0:
        a, b = (2*a+b)//5, (2*b-a)//5
        count += 1
    while den % 5 == 0:
        den //= 5
        count -= 1
    return count if rotation_power(count) == pair else None


def norm(p):
    return add(mul(p[0], p[0]), mul(p[1], p[1]))


def edge_angles(p, q):
    dot = add(mul(p[0], q[0]), mul(p[1], q[1]))
    cross = sub(mul(p[1], q[0]), mul(p[0], q[1]))
    target = sub(add(norm(p), norm(q)), ONE)
    return circle_solutions(zip(scale(2, dot), scale(2, cross), target))


def equality_angles(p, q):
    # p = R(c,s) q, coefficientwise in an independent real basis.
    return circle_solutions(list(zip(q[0], scale(-1, q[1]), p[0]))
                            + list(zip(q[1], q[0], p[1])))


def run(root):
    raw = (root/'certificates/cm_escape_nine.json').read_bytes()
    source = json.loads(raw)
    pts = [tuple(tuple(map(Q, axis)) for axis in p) for p in source['coordinates']]
    assert len(pts) == 9 and all(p != (ZERO, ZERO) for p in pts)
    records, edges, equalities = [], [], []
    for i, j in cartesian(range(9), repeat=2):
        angles = edge_angles(pts[i], pts[j])
        overlaps = equality_angles(pts[i], pts[j])
        decoded = [(a, power_index(a)) for a in angles]
        ids = [(a, power_index(a)) for a in overlaps]
        edges.extend([i, j, n] for _, n in decoded if n is not None)
        equalities.extend([i, j, n] for _, n in ids if n is not None)
        records.append(dict(pair=[i, j],
                            unit_angles=[dict(c=str(a[0]), s=str(a[1]), exponent=n)
                                         for a, n in decoded],
                            equality_angles=[dict(c=str(a[0]), s=str(a[1]), exponent=n)
                                             for a, n in ids]))
    # A single period is enough if it works; do not interpret its failure as
    # an infinite-graph lower bound. This particular source supplies a hint.
    word = source['proper_four_coloring']
    proper = all(word[i] != word[j] for i, j, n in edges)
    consistent = all(word[i] == word[j] for i, j, n in equalities)
    # The complete angle calculation also covers EVERY rational rotation,
    # not only powers of the selected one.  If only +/-1 connects seed
    # copies, each rational-rotation coset modulo +/-1 is a finite block.
    all_unit_angles = {(Q(a['c']), Q(a['s'])) for row in records for a in row['unit_angles']}
    all_equal_angles = {(Q(a['c']), Q(a['s'])) for row in records for a in row['equality_angles']}
    assert all_unit_angles | all_equal_angles <= {(Q(1), Q(0)), (Q(-1), Q(0))}
    antipodal_points = sorted(set(pts + [tuple(scale(-1, axis) for axis in p) for p in pts]))
    antipodal_edges = []
    for i in range(len(antipodal_points)):
        for j in range(i+1, len(antipodal_points)):
            dx = sub(antipodal_points[i][0], antipodal_points[j][0])
            dy = sub(antipodal_points[i][1], antipodal_points[j][1])
            if add(mul(dx, dx), mul(dy, dy)) == ONE:
                antipodal_edges.append([i, j])
    antipodal_word = color(len(antipodal_points), antipodal_edges, 4)
    assert antipodal_word is not None
    return dict(schema=1, experiment='E096', source_sha256=hashlib.sha256(raw).hexdigest(),
                rotation=dict(real='3/5', imaginary='4/5', gaussian_prime=[2, 1],
                              valuation_of_rotation=1),
                seed_count=9, all_ordered_pairs=81,
                contacts=records, unit_offsets=edges, equality_offsets=equalities,
                periodic_certificate=(dict(period=1, colors=4, word=word)
                                      if proper and consistent else None),
                rational_rotation_saturation=dict(
                    block='S union -S', vertices=len(antipodal_points),
                    all_pairs=len(antipodal_points)*(len(antipodal_points)-1)//2,
                    edges=antipodal_edges, colors=4, word=antipodal_word),
                scope='All integer powers, not a finite exponent scan. Exact chi=4 '
                      'also for all rational norm-one rotations, only if the independent '
                      'complete-angle and antipodal-block checks pass; '
                      'no coloring of the whole coordinate field or HN bound.')


if __name__ == '__main__':
    print(json.dumps(run(Path(__file__).resolve().parents[1]), separators=(',', ':')))
