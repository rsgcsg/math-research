"""Compile every nonzero Y return under H = <eta, u> exactly.

T125 section 9, independently replayed by verify_rotation_offset_bound.py,
proves that any equality p = eta**h * u**n * q between nonzero Y points has
0 <= h < 5 and -6 <= n <= 6.  Here every one of these 65 actions is scanned.
This is a geometry producer, not an independent certificate checker or a
coloring claim. The fixed origin is separate from all free H orbits.
"""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import math

from verify_quintic_core_probe import conjugate_twice, digest, product_twice
from verify_quintic_tau_union import verify as source_geometry


SOURCE_SHA = '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1'
POINT_SHA = '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
BOUND_ROWS_SHA = '1b2d008b0799760e15f6f87651cb0c0ca073f9866e7c602c2f3b2341e5204d51'


def rotations(table, limit=6):
    """Return all exact eta**h u**n, with integer-action ready coordinates."""
    one = (Q(1),) + (Q(0),) * 31
    eta = (Q(0),) * 16 + one[:16]
    u = tuple({0: Q(1, 8), 4: -Q(3, 8), 9: -Q(1, 8),
               13: -Q(1, 8)}.get(i, Q(0)) for i in range(32))
    mul = lambda a, b: tuple(Q(x) / 2 for x in product_twice(a, b, table))
    ubar = tuple(Q(x) / 2 for x in conjugate_twice(u))
    assert mul(u, ubar) == one
    eta_powers = [one]
    for _ in range(5):
        eta_powers.append(mul(eta, eta_powers[-1]))
    assert eta_powers[5] == one and len(set(eta_powers[:5])) == 5
    u_powers = {0: one}
    for n in range(1, limit + 1):
        u_powers[n] = mul(u, u_powers[n-1])
        u_powers[-n] = mul(ubar, u_powers[1-n])
    assert len(set(u_powers.values())) == 2*limit + 1
    return [(h, n, mul(eta_powers[h], u_powers[n]))
            for h in range(5) for n in range(-limit, limit + 1)]


def integer_action(rotation, table):
    """Sparse rows A and denominator d: multiplication is exactly A*p/d.

    The representation is in the same 32-dimensional basis as the independent
    geometry. Fractions occur only here, never inside the point scan.
    """
    den = math.lcm(*(x.denominator for x in rotation))
    coeff = [(i, int(x*den)) for i, x in enumerate(rotation) if x]
    rows = [[] for _ in range(32)]
    for j in range(32):
        column = Counter()
        for i, x in coeff:
            for k, factor in table[i, j]:
                column[k] += x*factor
        for k, x in column.items():
            if x:
                rows[k].append((j, x))
    common = math.gcd(2*den, *(x for row in rows for _, x in row))
    return [[(j, x//common) for j, x in row] for row in rows], 2*den//common


def apply_integer_action(point, rows, denominator):
    """Return a point on the original coordinate grid, or None if not on it."""
    result = []
    for row in rows:
        x = sum(point[j]*coefficient for j, coefficient in row)
        if x % denominator:
            return None
        result.append(x//denominator)
    return tuple(result)


def build(root, context=None, progress=False):
    if not __debug__:
        raise RuntimeError('Assertions are required; do not use -O.')
    root = Path(root)
    assert hashlib.sha256((root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest() == SOURCE_SHA
    if context is None:
        _, context = source_geometry(root, geometry_context=True)
    table = context['ring']['table']
    den = math.lcm(*(x.denominator for p in context['points'] for x in p))
    points = [tuple(int(x*den) for x in p) for p in context['points']]
    assert len(points) == len(set(points)) == 10077
    assert digest(points) == POINT_SHA
    zero_indices = [i for i, p in enumerate(points) if not any(p)]
    assert zero_indices == [4641]
    nonzero = [i for i, p in enumerate(points) if any(p)]
    lookup = {points[i]: i for i in nonzero}
    parents = list(range(len(points)))

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    def join(i, j):
        i, j = find(i), find(j)
        if i != j:
            parents[max(i, j)] = min(i, j)

    records = []
    # Convention throughout: target = eta**h * u**n * source.
    for h, n, rotation in rotations(table):
        rows, action_den = integer_action(rotation, table)
        mapping = []
        for i in nonzero:
            target = apply_integer_action(points[i], rows, action_den)
            j = lookup.get(target)
            if j is not None:
                mapping.append([i, j])
                join(i, j)
        records.append(dict(h=h, n=n, domain=len(mapping), mapping=mapping))
        if progress:
            print(json.dumps(dict(progress='rotation_equalities', h=h, n=n,
                                  domain=len(mapping))), flush=True)
    representatives = sorted({find(i) for i in nonzero})
    representative_set = set(representatives)
    coordinates = [None] * len(points)
    # Every orbit member must be directly related to its canonical member
    # within the complete return range, not merely transitively connected.
    for record in records:
        for i, j in record['mapping']:
            if i in representative_set:
                value = [i, record['h'], record['n']]
                assert coordinates[j] is None or coordinates[j] == value
                coordinates[j] = value
    assert all(coordinates[i] is not None and coordinates[i][0] == find(i)
               for i in nonzero)
    assert coordinates[zero_indices[0]] is None
    assert all(coordinates[i] == [i, 0, 0] for i in representatives)
    # The H action is free away from zero: v0(u)=-1 forces n=0 in
    # eta**h*u**n=1, then primitive order five forces h=0 mod 5.
    for record in records:
        for i, j in record['mapping']:
            ri, hi, ni = coordinates[i]
            rj, hj, nj = coordinates[j]
            assert ri == rj
            assert hj == (hi + record['h']) % 5
            assert nj == ni + record['n']
    orbit_sizes = Counter(find(i) for i in nonzero)
    hist = sorted(Counter(orbit_sizes.values()).items())
    total_returns = sum(r['domain'] for r in records)
    # Freeness makes every ordered pair in an orbit correspond to exactly
    # one (h,n); this guards against either missed or duplicated returns.
    assert total_returns == sum(size*size for size in orbit_sizes.values())
    result = dict(
        schema=1, kind='complete_nonzero_rotation_orbit_equalities',
        source_sha256=SOURCE_SHA, source_point_sha256=POINT_SHA,
        source_denominator=den, source_vertices=len(points),
        zero_indices=zero_indices, nonzero_vertices=len(nonzero),
        completeness=dict(theorem='T125 section 9', eta_order=5,
                          equality_offset_absolute_bound=6,
                          valuation_rows_sha256=BOUND_ROWS_SHA,
                          replay='research/verify_rotation_offset_bound.py'),
        convention='target = eta^h u^n source; point_i = eta^h u^n point_representative',
        orbit_count=len(representatives), representatives=representatives,
        orbit_size_histogram=hist, coordinates=coordinates,
        all_actions=records, total_nonzero_returns=total_returns,
        return_map_sha256=digest(records), coordinates_sha256=digest(coordinates),
        scope='Complete nonzero H=<eta,u> orbit identification from the T125 return '
              'bound. Origin is one fixed vertex. No unit-edge table, coloring, '
              'joint law, lower bound, or plane coloring is certified here.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    print('ROTATION_EQUALITIES_JSON=' + json.dumps(
        build(Path(__file__).resolve().parents[1], progress=not args.quiet),
        separators=(',', ':')), flush=True)
