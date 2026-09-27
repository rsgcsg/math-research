"""Independent complete nonzero H=<eta,u> identification checker.

Only standard-library and existing independent field/geometry checks are used.
The producer is never imported.  Instead of making each combined eta^h u^n
operator and joining its returns, this checker follows elementary rotations
on one fixed integer grid, then reconstructs connected components by BFS.
The finite exponent bound is replayed, not inferred from absent returns.

No unit-edge table, coloring, or Hadwiger--Nelson bound is certified here.
"""

from collections import Counter, deque
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import math
import time

from verify_quintic_core_probe import conjugate_twice, digest, product_twice
from verify_quintic_tau_union import verify as source_geometry
from verify_rotation_offset_bound import verify as offset_bound


SOURCE_SHA = '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1'
POINT_SHA = '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
ROWS_SHA = '1b2d008b0799760e15f6f87651cb0c0ca073f9866e7c602c2f3b2341e5204d51'
CONVENTION = ('target = eta^h u^n source; '
              'point_i = eta^h u^n point_representative')
SCOPE = ('Complete nonzero H=<eta,u> orbit identification from the T125 return '
         'bound. Origin is one fixed vertex. No unit-edge table, coloring, '
         'joint law, lower bound, or plane coloring is certified here.')


def _elementary_operator(coefficients, divisor, table):
    """Columns from direct elementary multiplication, not combined powers."""
    rows = [[] for _ in range(32)]
    for column in range(32):
        unit = [int(i == column) for i in range(32)]
        image = product_twice(coefficients, unit, table)
        for row, value in enumerate(image):
            if value:
                rows[row].append((column, value))

    def apply(point):
        result = []
        for row in rows:
            numerator = sum(point[j] * value for j, value in row)
            quotient, remainder = divmod(numerator, divisor)
            assert remainder == 0, 'Elementary transform left the proved integer grid'
            result.append(quotient)
        return tuple(result)

    return apply


def _rebuild(context, bound_report):
    assert bound_report['status'] == 'PASS'
    assert bound_report['valuation_rows_sha256'] == ROWS_SHA
    assert bound_report['nonzero_equality_offset_absolute_bound'] == 6
    assert bound_report['u_valuations_v0_v3'] == [-1, 1]
    assert bound_report['unresolved_residues'] == 0
    table = context['ring']['table']
    source_denominator = math.lcm(
        *(x.denominator for point in context['points'] for x in point))
    points = [tuple(int(x * source_denominator) for x in point)
              for point in context['points']]
    assert source_denominator == 480
    assert len(points) == len(set(points)) == 10077
    assert digest(points) == POINT_SHA
    zero_indices = [i for i, point in enumerate(points) if not any(point)]
    assert zero_indices == [4641]
    nonzero = [i for i, point in enumerate(points) if any(point)]

    eta = [int(i == 16) for i in range(32)]
    u8 = [{0: 1, 4: -3, 9: -1, 13: -1}.get(i, 0) for i in range(32)]
    ubar8 = [{0: 1, 4: -3, 9: 1, 13: 1}.get(i, 0) for i in range(32)]
    assert conjugate_twice(u8) == [2 * x for x in ubar8]
    assert product_twice(u8, ubar8, table) == [128] + [0] * 31
    assert product_twice(eta, conjugate_twice(eta), table) == [4] + [0] * 31
    field_mul = context['ring']['mul']
    eta_power = (Q(1),) + (Q(0),) * 31
    powers = [eta_power]
    for _ in range(5):
        eta_power = field_mul(eta_power, tuple(map(Q, eta)))
        powers.append(eta_power)
    assert powers[5] == powers[0] and len(set(powers[:5])) == 5

    # At most six u or u^-1 applications introduce divisors 16, and four
    # eta applications introduce divisors 2.  This over-large integer grid
    # contains every scan point without rounding. Moving from u^-6 to u^6
    # by u remains on that same grid by cancellation and is checked exactly.
    scale = 16**6 * 2**4
    scaled = [tuple(scale * x for x in points[i]) for i in nonzero]
    lookup = {point: i for point, i in zip(scaled, nonzero)}
    eta_action = _elementary_operator(eta, 2, table)
    forward = _elementary_operator(u8, 16, table)
    backward = _elementary_operator(ubar8, 16, table)
    layer = scaled
    for _ in range(6):
        layer = [backward(point) for point in layer]
    records_by_action = {}
    for n in range(-6, 7):
        torsion_layer = layer
        for h in range(5):
            mapping = []
            for i, point in zip(nonzero, torsion_layer):
                j = lookup.get(point)
                if j is not None:
                    mapping.append([i, j])
            records_by_action[h, n] = dict(h=h, n=n, domain=len(mapping),
                                           mapping=mapping)
            if h < 4:
                torsion_layer = [eta_action(point) for point in torsion_layer]
        if n < 6:
            layer = [forward(point) for point in layer]
    records = [records_by_action[h, n]
               for h in range(5) for n in range(-6, 7)]
    assert records_by_action[0, 0]['mapping'] == [[i, i] for i in nonzero]
    assert len(records) == 65

    # Independently rebuild components.  A path may suggest an orbit, but
    # the later direct representative return check is mandatory: arbitrary
    # transitive closure alone would not certify its claimed coordinates.
    adjacency = {i: set() for i in nonzero}
    inverse_maps = {}
    for record in records:
        pairs = record['mapping']
        assert pairs == sorted(pairs)
        assert len({i for i, _ in pairs}) == len({j for _, j in pairs}) == len(pairs)
        inverse_maps[record['h'], record['n']] = set(map(tuple, pairs))
        for i, j in pairs:
            adjacency[i].add(j)
            adjacency[j].add(i)
    for (h, n), pairs in inverse_maps.items():
        assert {(j, i) for i, j in pairs} == inverse_maps[(-h) % 5, -n]
    component = {}
    sizes = []
    representatives = []
    for initial in nonzero:
        if initial in component:
            continue
        representatives.append(initial)
        queue = deque([initial])
        component[initial] = initial
        size = 0
        while queue:
            point = queue.popleft()
            size += 1
            for neighbor in adjacency[point]:
                if neighbor not in component:
                    assert neighbor >= initial
                    component[neighbor] = initial
                    queue.append(neighbor)
        sizes.append(size)
    coordinates = [None] * len(points)
    representative_set = set(representatives)
    for record in records:
        for i, j in record['mapping']:
            if i in representative_set:
                assert coordinates[j] is None
                coordinates[j] = [i, record['h'], record['n']]
    for i in nonzero:
        assert coordinates[i] is not None
        assert coordinates[i][0] == component[i]
    for i in representatives:
        assert coordinates[i] == [i, 0, 0]
    for record in records:
        for i, j in record['mapping']:
            a, h, n = coordinates[i]
            b, k, m = coordinates[j]
            assert a == b
            assert (h + record['h']) % 5 == k
            assert n + record['n'] == m
    total_returns = sum(record['domain'] for record in records)
    assert total_returns == sum(size**2 for size in sizes)
    assert len(representatives) == 4176 and total_returns == 39580
    expected = dict(
        schema=1, kind='complete_nonzero_rotation_orbit_equalities',
        source_sha256=SOURCE_SHA, source_point_sha256=POINT_SHA,
        source_denominator=source_denominator, source_vertices=len(points),
        zero_indices=zero_indices, nonzero_vertices=len(nonzero),
        completeness=dict(theorem='T125 section 9', eta_order=5,
                          equality_offset_absolute_bound=6,
                          valuation_rows_sha256=ROWS_SHA,
                          replay='research/verify_rotation_offset_bound.py'),
        convention=CONVENTION, orbit_count=len(representatives),
        representatives=representatives,
        orbit_size_histogram=[list(pair) for pair in sorted(Counter(sizes).items())],
        coordinates=coordinates, all_actions=records,
        total_nonzero_returns=total_returns,
        return_map_sha256=digest(records), coordinates_sha256=digest(coordinates),
        scope=SCOPE)
    return expected


def _check(data, expected):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    assert type(data) is dict and set(data) == set(expected)
    # Serialized comparison also rejects Python's bool==int and 1.0==1
    # equivalences, while allowing object key order to be irrelevant.
    assert json.dumps(data, sort_keys=True, separators=(',', ':')) == \
        json.dumps(expected, sort_keys=True, separators=(',', ':'))


def _mutation_tests(data, expected):
    checks = []

    def reject(name, mutate):
        damaged = deepcopy(data)
        mutate(damaged)
        try:
            _check(damaged, expected)
        except (AssertionError, KeyError, TypeError, ValueError):
            checks.append(name)
        else:
            raise AssertionError('Mutation accepted: ' + name)

    def omit_return(d):
        record = next(r for r in d['all_actions'] if r['domain'] > 0)
        record['mapping'].pop()
        record['domain'] -= 1
        d['total_nonzero_returns'] -= 1
        d['return_map_sha256'] = digest(d['all_actions'])

    def false_return(d):
        record = next(r for r in d['all_actions'] if r['domain'] > 0)
        record['mapping'][0][1] = d['zero_indices'][0]
        d['return_map_sha256'] = digest(d['all_actions'])

    def false_coordinate(d):
        coordinate = next(row for row in d['coordinates'] if row is not None)
        coordinate[2] += 1
        d['coordinates_sha256'] = digest(d['coordinates'])

    reject('omitted_return_with_recomputed_hash', omit_return)
    reject('false_origin_return_with_recomputed_hash', false_return)
    reject('wrong_coordinate_with_recomputed_hash', false_coordinate)
    reject('wrong_canonical_representative',
           lambda d: d['representatives'].__setitem__(0, d['representatives'][0] + 1))
    reject('origin_turned_into_free_orbit',
           lambda d: d['coordinates'].__setitem__(4641, [4641, 0, 0]))
    reject('false_completeness_bound',
           lambda d: d['completeness'].__setitem__('equality_offset_absolute_bound', 5))
    reject('changed_source_hash', lambda d: d.__setitem__('source_sha256', '0' * 64))
    reject('missing_action', lambda d: d['all_actions'].pop())
    reject('swapped_torsion_label', lambda d: d['all_actions'][0].__setitem__('h', 1))
    reject('boolean_metadata', lambda d: d.__setitem__('schema', True))
    return checks


def verify(root, mutation_tests=False, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    started = time.monotonic()
    root = Path(root)
    source_sha = hashlib.sha256(
        (root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest()
    assert source_sha == SOURCE_SHA
    certificate = root / 'certificates/rotation_orbit_equalities.json'
    data = json.loads(certificate.read_text())
    bound_report = offset_bound(root)
    _, context = source_geometry(root, geometry_context=True)
    expected = _rebuild(context, bound_report)
    _check(data, expected)
    mutations = _mutation_tests(data, expected) if mutation_tests else []
    report = dict(
        status='PASS', kind=data['kind'], certificate_sha256=hashlib.sha256(
            certificate.read_bytes()).hexdigest(),
        source_sha256=source_sha, source_point_sha256=POINT_SHA,
        source_vertices=data['source_vertices'], zero_indices=data['zero_indices'],
        nonzero_vertices=data['nonzero_vertices'], orbit_count=data['orbit_count'],
        orbit_size_histogram=data['orbit_size_histogram'],
        actions_checked=len(data['all_actions']),
        point_action_checks=65 * data['nonzero_vertices'],
        total_nonzero_returns=data['total_nonzero_returns'],
        return_map_sha256=data['return_map_sha256'],
        coordinates_sha256=data['coordinates_sha256'],
        completeness_bound_replayed=True, mutation_rejections=mutations,
        elapsed_seconds=round(time.monotonic() - started, 3), scope=SCOPE)
    if geometry_context:
        denominator = expected['source_denominator']
        points = [tuple(int(x * denominator) for x in point)
                  for point in context['points']]
        representatives = expected['representatives']
        return report, dict(
            points=points, denominator=denominator,
            representative_points=[points[i] for i in representatives],
            representatives=representatives, table=context['ring']['table'],
            equalities=expected, bounds=bound_report, source_context=context)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutation-tests', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.mutation_tests),
                     indent=2))
