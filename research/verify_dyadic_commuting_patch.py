"""Independent E095 finite physical commuting-patch checker.

No producer, search, or SAT imports.  Four copies are built by successively
applying sparse eta and u operators, not by the producer's combined rotation.
When an induced stage is present, EVERY unordered point pair is visited and
filtered by a checked ring map before exact norm checking.  This deliberately
does not reuse the producer's displacement/bucket enumeration.

UNKNOWN and uncertified UNSAT are observations only.  For a listed-only run,
neither this checker nor its PASS status asserts that all unit pairs were
enumerated, or that any coloring/negative coloring theorem was obtained.
"""

from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math

from verify_quintic_tau_union import verify as source_geometry
from verify_quintic_core_probe import (
    conjugate_twice, digest, filter_map, product_twice,
)


def _rebuild(context):
    table = context['ring']['table']
    source_den = math.lcm(*(x.denominator for p in context['points'] for x in p))
    # eta multiplication can introduce a factor 2; u a factor 8.  Retain
    # their product as the common denominator, independently of any saved
    # geometry metadata or any precomputed eta*u coordinates.
    denominator = 16 * source_den
    assert all((x * denominator).denominator == 1 for p in context['points'] for x in p)
    base = [tuple(int(x * denominator) for x in p) for p in context['points']]
    eta = [int(i == 16) for i in range(32)]
    u8 = [{0: 1, 4: -3, 9: -1, 13: -1}.get(i, 0) for i in range(32)]
    assert product_twice(eta, conjugate_twice(eta), table) == [4] + [0] * 31
    assert product_twice(u8, conjugate_twice(u8), table) == [256] + [0] * 31

    def apply(point, coefficient, divisor):
        numerator = product_twice(coefficient, point, table)
        assert all(x % divisor == 0 for x in numerator)
        return tuple(x // divisor for x in numerator)

    eta_copy = [apply(p, eta, 2) for p in base]
    u_copy = [apply(p, u8, 16) for p in base]
    both = [apply(p, eta, 2) for p in u_copy]
    assert both == [apply(p, u8, 16) for p in eta_copy]
    raw = [base, eta_copy, u_copy, both]
    assert all(len(set(copy)) == len(base) for copy in raw)
    # A single lookup for exact coordinate tuples imposes ALL physical
    # identifications, including intersections not connected by a chosen path.
    points = sorted(set().union(*(set(copy) for copy in raw)))
    index = {point: i for i, point in enumerate(points)}
    copies = [[index[p] for p in copy] for copy in raw]
    listed_set = set()
    for a, b in context['edges']:
        for copy in copies:
            x, y = sorted((copy[a], copy[b]))
            assert x < y
            listed_set.add((x, y))
    listed = sorted(listed_set)
    metadata = dict(
        vertices=len(points), denominator=denominator,
        actual_pairs=len(points) * (len(points) - 1) // 2,
        point_sha256=digest(points), copies_sha256=digest(copies),
        copy_labels=['Y', 'eta_Y', 'u_Y', 'eta_u_Y'],
        listed_edges=len(listed), listed_edge_sha256=digest(listed),
        pairwise_copy_intersections=[
            [a, b, len(set(copies[a]) & set(copies[b]))]
            for a, b in combinations(range(4), 2)],
    )
    return points, copies, listed, table, metadata


def _all_actual_edges(points, denominator, table):
    prime, images, bars = filter_map(table)
    assert denominator % prime != 0
    residues = [(sum(x * y for x, y in zip(point, images)) % prime,
                 sum(x * y for x, y in zip(point, bars)) % prime)
                for point in points]
    target_mod = denominator * denominator % prime
    target = [4 * denominator * denominator] + [0] * 31
    edges, norms = [], {}
    survivors = 0
    # Exhaustive PAIR loop, not a lookup by any displacement vocabulary.
    for i in range(len(points)):
        x, xbar = residues[i]
        for j in range(i + 1, len(points)):
            y, ybar = residues[j]
            if (x - y) * (xbar - ybar) % prime != target_mod:
                continue
            survivors += 1
            delta = tuple(a - b for a, b in zip(points[i], points[j]))
            if delta not in norms:
                norms[delta] = product_twice(
                    delta, conjugate_twice(delta), table) == target
            if norms[delta]:
                edges.append((i, j))
    assert edges == sorted(set(edges))
    return edges, dict(filter_prime=prime, modular_candidate_pairs=survivors,
                       distinct_exact_differences=len(norms))


def _word(word, vertices, edges):
    assert isinstance(word, str) and len(word) == vertices
    assert set(word) <= set('01234')
    assert all(word[a] != word[b] for a, b in edges)


def _check(data, parent, rebuilt, source_sha, induced=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    points, copies, listed, table, metadata = rebuilt
    assert data['schema'] == 1 and data['experiment'] == 'E095'
    assert data['source_sha256'] == source_sha
    assert data['source_geometry'] == parent['geometry']
    stages = data['stages']
    assert isinstance(stages, list) and len(stages) in (1, 2)
    first = stages[0]
    assert first['name'] == 'transported_edges_with_all_physical_identifications'
    assert first['status'] in ('SAT', 'UNKNOWN', 'UNSAT_SEARCH_ONLY_UNCERTIFIED')
    has_induced = first['status'] == 'SAT'
    assert len(stages) == 1 + int(has_induced)
    summary = dict(metadata)
    if has_induced:
        assert induced is not None
        all_edges, enumeration = induced
        assert set(listed) <= set(all_edges)
        summary.update(induced_edges=len(all_edges), edge_sha256=digest(all_edges),
                       additional_cross_edges=len(all_edges) - len(listed))
        assert data['enumeration'] == enumeration
    else:
        assert induced is None and data['enumeration'] is None
        assert 'violations_on_induced_graph' not in first
        all_edges = None
    assert data['geometry'] == summary
    reports = []
    for index, stage in enumerate(stages):
        status = stage['status']
        assert type(stage['conflict_budget']) is int
        direct = status == 'SAT_DIRECT_REUSE'
        if direct:
            assert index == 1 and stage['conflict_budget'] == 0 and stage['stats'] is None
        else:
            assert 1 <= stage['conflict_budget'] <= 20000
            assert isinstance(stage['stats'], dict)
            assert all(type(value) is int and value >= 0 for value in stage['stats'].values())
        if index == 1:
            assert stage['name'] == 'all_actual_unit_pairs'
            assert status in ('SAT', 'SAT_DIRECT_REUSE', 'UNKNOWN',
                              'UNSAT_SEARCH_ONLY_UNCERTIFIED')
        chosen_edges = listed if index == 0 else all_edges
        if status in ('SAT', 'SAT_DIRECT_REUSE'):
            _word(stage['word'], len(points), chosen_edges)
            checked_status = ('CHECKED_LISTED_EDGE_COLORING_ONLY' if index == 0
                              else 'CHECKED_INDUCED_FINITE_FIVE_COLORING')
            reports.append(dict(stage=stage['name'], status=checked_status,
                                checked_word_edges=len(chosen_edges)))
        else:
            assert stage['word'] is None
            reports.append(dict(stage=stage['name'], recorded_search_status=status,
                                status='GEOMETRY_ONLY_NO_COLORING_CONCLUSION',
                                negative_mathematical_claim=False))
    if has_induced:
        violations = sum(first['word'][a] == first['word'][b] for a, b in all_edges)
        assert first['violations_on_induced_graph'] == violations
        if violations == 0:
            assert stages[1]['status'] == 'SAT_DIRECT_REUSE'
            assert stages[1]['word'] == first['word']
        else:
            assert stages[1]['status'] != 'SAT_DIRECT_REUSE'
    return dict(
        status='PASS', experiment='E095', geometry=summary,
        exact_physical_copies=len(copies),
        transported_edge_occurrences=4 * parent['geometry']['induced_edges'],
        all_actual_pairs_enumerated=has_induced, stages=reports,
        solver_stats_independently_audited=False,
        scope=('Exact four-layer physical point identifications and transported '
               'unit edges. Only an induced-stage positive word certifies a '
               'coloring on ALL unit pairs. UNKNOWN and uncertified UNSAT give '
               'no negative theorem. No full joint, whole-host, or HN conclusion.'))


def _self_tests(table):
    """Exercise the conditional induced/SAT path even for an UNKNOWN artifact."""
    zero = (Q(0),) * 32
    one = (Q(1),) + zero[1:]
    tiny = dict(ring=dict(table=table), points=[zero, one], edges=[(0, 1)])
    rebuilt = _rebuild(tiny)
    points, copies, listed, _, metadata = rebuilt
    assert len(points) == 5
    induced = _all_actual_edges(points, metadata['denominator'], table)
    edges, enumeration = induced
    assert set(listed) <= set(edges)
    geometry = dict(metadata, induced_edges=len(edges), edge_sha256=digest(edges),
                    additional_cross_edges=len(edges) - len(listed))
    word = ''.join(str(i) for i in range(len(points)))
    parent = dict(geometry=dict(vertices=2, induced_edges=1))
    data = dict(schema=1, experiment='E095', source_sha256='1' * 64,
                source_geometry=parent['geometry'], geometry=geometry,
                enumeration=enumeration, stages=[
                    dict(name='transported_edges_with_all_physical_identifications',
                         status='SAT', word=word, conflict_budget=1, stats={},
                         violations_on_induced_graph=0),
                    dict(name='all_actual_unit_pairs', status='SAT_DIRECT_REUSE',
                         word=word, conflict_budget=0, stats=None)])
    report = _check(data, parent, rebuilt, '1' * 64, induced)
    assert report['all_actual_pairs_enumerated'] is True
    rejected = []
    for mutation in ('monochromatic_word', 'missing_actual_edge_digest'):
        bad = deepcopy(data)
        if mutation == 'monochromatic_word':
            bad['stages'][1]['word'] = '0' * len(points)
        else:
            bad['geometry']['edge_sha256'] = digest(edges[1:])
        try:
            _check(bad, parent, rebuilt, '1' * 64, induced)
        except AssertionError:
            rejected.append(mutation)
        else:
            raise AssertionError('Synthetic mutation accepted: ' + mutation)
    # A square checks four true unit pairs AND both nonunit diagonals without
    # relying on a single rotation-derived edge list as the expected answer.
    square = []
    for x, y in ((0, 0), (1, 0), (1, 1), (0, 1)):
        point = [0] * 32
        point[0], point[8] = x, y
        square.append(tuple(point))
    square_edges, _ = _all_actual_edges(square, 1, table)
    assert square_edges == [(0, 1), (0, 3), (1, 2), (2, 3)]
    return dict(induced_positive_path='PASS', square_all_six_pairs='PASS',
                rejected_synthetic_mutations=rejected)


def verify(root, mutation_checks=False, certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    root = Path(root)
    path = Path(certificate) if certificate else root / 'certificates/dyadic_commuting_patch.json'
    data = json.loads(path.read_text())
    parent, context = source_geometry(root, geometry_context=True)
    rebuilt = _rebuild(context)
    source_sha = hashlib.sha256((root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest()
    induced = None
    if len(data['stages']) == 2:
        induced = _all_actual_edges(rebuilt[0], rebuilt[4]['denominator'], rebuilt[3])
    report = _check(data, parent, rebuilt, source_sha, induced)
    report['small_induced_path_self_tests'] = _self_tests(rebuilt[3])
    if mutation_checks:
        mutations = []
        for field in ('point_sha256', 'copies_sha256', 'listed_edge_sha256'):
            bad = deepcopy(data)
            bad['geometry'][field] = '0' * 64
            mutations.append(('altered_' + field, bad))
        bad = deepcopy(data)
        bad['source_sha256'] = '0' * 64
        mutations.append(('altered_source_sha256', bad))
        bad = deepcopy(data)
        bad['geometry']['pairwise_copy_intersections'][0][2] += 1
        mutations.append(('altered_physical_intersection', bad))
        bad = deepcopy(data)
        bad['geometry']['vertices'] += 1
        mutations.append(('altered_vertex_count', bad))
        bad = deepcopy(data)
        bad['stages'][0]['name'] = 'all_actual_unit_pairs'
        mutations.append(('listed_mislabelled_induced', bad))
        bad = deepcopy(data)
        bad['stages'][0]['status'] = 'UNSAT'
        mutations.append(('uncertified_negative_upgrade', bad))
        for index, stage in enumerate(data['stages']):
            bad = deepcopy(data)
            if stage['word'] is None:
                bad['stages'][index]['word'] = '0' * len(rebuilt[0])
                name = 'word_in_unknown_stage'
            else:
                word = list(stage['word'])
                a, b = rebuilt[2][0]
                word[b] = word[a]
                bad['stages'][index]['word'] = ''.join(word)
                name = 'monochromatic_listed_edge'
            mutations.append((f'{name}_{index}', bad))
        rejected = []
        for name, bad in mutations:
            try:
                _check(bad, parent, rebuilt, source_sha, induced)
            except AssertionError:
                rejected.append(name)
            else:
                raise AssertionError('Mutation accepted: ' + name)
        report['rejected_mutations'] = rejected
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutations', action='store_true')
    parser.add_argument('--certificate')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.mutations,
                            args.certificate), indent=2))
