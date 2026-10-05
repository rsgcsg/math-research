#!/usr/bin/env python3
"""Exact replay of T162: the optimal nine-link lift of the fixed T161 count.

Search used a separate C++ optimizer. This verifier does not use its search
status or pruning bound: it reconstructs each quotient, checks a positive word,
and exhausts every canonical coloring whose nonnegative partial score could
beat that word. Only integer arithmetic is used for the negative checks.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Verification requires normal Python, not -O')

from verify_pr_matching_window_ceiling import read, digest
from check_transport_projection import (
    require, verify_geometry_and_components, square_distance, multiplication_twice,
)

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/q_defect_lift.json'
RECEIPT = ROOT / 'certificates/q_defect_lift_validation.json'
ENVELOPE = ROOT / 'certificates/q_defect_envelope.json'
BASE = 'c7dd21efe99cf18884a62b21f34a27de23eec550'


def literal_tree(x):
    if type(x) in (int, str):
        return True
    if type(x) is list:
        return all(literal_tree(y) for y in x)
    if type(x) is dict:
        return all(type(k) is str and literal_tree(v) for k, v in x.items())
    return False


def normalize(word):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in word)


def build_case(vertices, edges, score_pairs, links, mask):
    """Reconstruct Q equality classes by graph traversal, not producer DSU."""
    adj = {v: set() for v in vertices}
    for j, (a, b) in enumerate(links):
        if not (mask >> j) & 1:
            adj[a].add(b)
            adj[b].add(a)
    component = {}
    for v in vertices:
        if v in component:
            continue
        seen = {v}
        todo = [v]
        while todo:
            for w in adj[todo.pop()]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        for w in seen:
            component[w] = min(seen)
    blocks = sorted(set(component.values()))
    unequal = {tuple(sorted((component[a], component[b]))) for a, b in edges}
    unequal.update(tuple(sorted((component[a], component[b])))
                   for j, (a, b) in enumerate(links) if (mask >> j) & 1)
    require(all(a != b for a, b in unequal), 'consistent quotient inequality edges')
    graph = {v: set() for v in blocks}
    for a, b in unequal:
        graph[a].add(b)
        graph[b].add(a)
    costs = Counter(tuple(sorted((component[a], component[b]))) for a, b in score_pairs)
    constant = sum(w for (a, b), w in costs.items() if a == b)
    # Deterministic order independent of the certificate and the C++ optimizer.
    order = []
    placed = set()
    while len(order) < len(blocks):
        v = max((v for v in blocks if v not in placed),
                key=lambda z: (len(graph[z] & placed), len(graph[z]), -z))
        order.append(v)
        placed.add(v)
    index = {v: j for j, v in enumerate(order)}
    back_edges = [sorted(index[b] for b in graph[a] if index[b] < i)
                  for i, a in enumerate(order)]
    back_costs = [[(j, costs[tuple(sorted((a, b)))])
                   for j, b in enumerate(order[:i]) if tuple(sorted((a, b))) in costs]
                  for i, a in enumerate(order)]
    return back_edges, back_costs, constant


def exclude_lower_score(back_edges, back_costs, constant, claimed_minimum):
    """Exhaustive branch cover for score < claimed_minimum, with color symmetry.

    Score is a sum of nonnegative equality indicators. A branch reaching the
    claimed lower bound can never lead to a smaller complete score. At each
    node try every existing color and, if fewer than five, one new color.
    Relabeling any putative counterexample in first-occurrence order gives
    exactly one visited branch. No bound from a numerical optimizer is used.
    """
    n = len(back_edges)
    color = [-1] * n
    visited = 0

    def visit(i, top, partial):
        nonlocal visited
        visited += 1
        if partial >= claimed_minimum:
            return
        require(i < n, 'counterexample to a claimed case minimum')
        forbidden = 0
        for j in back_edges[i]:
            forbidden |= 1 << color[j]
        extra = [0] * 5
        for j, weight in back_costs[i]:
            extra[color[j]] += weight
        for value in range(min(top + 2, 5)):
            if (forbidden >> value) & 1:
                continue
            color[i] = value
            visit(i + 1, max(top, value), partial + extra[value])
        color[i] = -1

    visit(0, -1, constant)
    return visited


def prepare(parent, g, b, r):
    n, sets, sizes = verify_geometry_and_components(g, b, r)
    q = parent['quotient']
    vertices = q['vertices']
    links = [tuple(x) for x in q['Q_bridges']]
    require(len(vertices) == 21 and vertices == sorted(set(vertices)), '21 distinct ordered vertices')
    require(len(links) == 9 and len(set(links)) == 9, 'nine distinct Q links')
    require(all(a in vertices and z in vertices and (a, z) in sets['Q'] for a, z in links), 'actual Q links')
    score_records = [rec for rec in q['realizations'] if rec['type'] in ('P', 'R')]
    require(Counter(rec['type'] for rec in score_records) == {'P': 36, 'R': 12}, 'fixed count expression')
    score_pairs = [tuple(rec['actual_pair']) for rec in score_records]
    require(len(score_pairs) == len(set(score_pairs)) == 48, '48 distinct actual events')
    for rec in score_records:
        a, z = rec['actual_pair']
        require(a in vertices and z in vertices and (a, z) in sets[rec['type']], 'actual score event membership')
    table = multiplication_twice()
    edges = []
    for a, z in combinations(vertices, 2):
        distance = square_distance(g, a, z, table)
        unit = distance == (F(1),) + (F(0),) * 31
        require(unit == ((a, z) in sets['E']), 'complete local induced unit geometry')
        if unit:
            edges.append((a, z))
        for tag, value in [('P', F(1, 3)), ('Q', F(4)), ('R', F(4, 3))]:
            if (a, z) in sets[tag]:
                require(distance == (value,) + (F(0),) * 31, 'exact selected local distance')
    # For the fixed expression, adjoining any one actual Y vertex cannot
    # delete a W coloring: it has at most three neighbors in W, leaving at
    # least two of the five colors. This says nothing about joint extension
    # of several vertices or about new marginal-balance constraints.
    outside_degrees = Counter({v: 0 for v in range(n) if v not in set(vertices)})
    inside = set(vertices)
    for a, z in sets['E']:
        if a in inside and z not in inside:
            outside_degrees[z] += 1
        elif z in inside and a not in inside:
            outside_degrees[a] += 1
    histogram = Counter(outside_degrees.values())
    require(histogram == {0: 9556, 1: 447, 2: 52, 3: 1}, 'complete external neighbor census')
    return vertices, edges, score_pairs, links, sizes, dict(sorted(histogram.items()))


def check(cert, parent, prepared, replay_minima=True):
    require(literal_tree(cert), 'certificate uses exact integer/string literals')
    require(cert['schema'] == 'q-defect-lift-v1' and cert['base_commit'] == BASE, 'schema and source base')
    require(cert['joint_certificate_sha256'] == digest(parent), 'fixed T161 expression binding')
    require(cert['geometry_semantic_sha256'] == parent['geometry_semantic_sha256'], 'geometry binding')
    vertices, edges, pairs, links, sizes, outside_histogram = prepared
    penalties = cert['penalties']
    require(len(penalties) == 9 and all(type(x) is int and x >= 0 for x in penalties), 'nine integer penalties')
    require(cert['threshold'] == 9, 'fixed threshold')
    records = cert['cases']
    require(len(records) == 512 and [x['mask'] for x in records] == list(range(512)), 'all 512 exact Q-defect patterns')
    total_nodes = 0
    by_size = defaultdict(list)
    # Check all positive witnesses and the minimal coefficient identity first.
    # This catches inexpensive corruption before replaying negative claims.
    for rec in records:
        mask, minimum, text = rec['mask'], rec['minimum'], rec['word']
        require(type(minimum) is int and 0 <= minimum <= 48, 'integer minimum')
        require(type(text) is str and len(text) == 21 and set(text) <= set('01234'), 'complete local five-color word')
        word = tuple(map(int, text))
        require(word == normalize(word), 'canonical color labels')
        colors = dict(zip(vertices, word))
        require(all(colors[a] != colors[z] for a, z in edges), 'all induced unit edges are proper')
        actual_mask = sum(1 << j for j, (a, z) in enumerate(links) if colors[a] != colors[z])
        require(mask == actual_mask, 'exact defect pattern of positive word')
        require(sum(colors[a] == colors[z] for a, z in pairs) == minimum, 'positive word attains case minimum')
        require(minimum + sum(penalties[j] for j in range(9) if (mask >> j) & 1) >= 9,
                'lifted inequality in every defect case')
        by_size[mask.bit_count()].append(minimum)
    require(penalties == [9 - records[1 << j]['minimum'] for j in range(9)],
            'each coefficient attains its single-defect necessary lower bound')
    require(sum(penalties) == 12, 'optimal penalty sum')
    if replay_minima:
        for rec in records:
            model = build_case(vertices, edges, pairs, links, rec['mask'])
            total_nodes += exclude_lower_score(*model, rec['minimum'])
    # Exact elimination with 2r-p<=1. 36p+12r+12(1-q)>=9.
    require((F(36) + F(12, 2), F(12, 2)) == (F(42), F(6)), 'eliminate r using PRR inequality')
    require((F(42, 3), F(12, 3), F(9-6, 3)) == (F(14), F(4), F(1)), 'normalized robust inequality')
    boundary_q = F(1) - (F(1) - F(14, 27)) / 4
    require(boundary_q == F(95, 108), 'p=1/27 boundary')
    return {
        'schema': 'q-defect-lift-replay-v2', 'status': 'PASS',
        'certificate_sha256': digest(cert), 'joint_certificate_sha256': digest(parent),
        'geometry_semantic_sha256': cert['geometry_semantic_sha256'],
        'transport_component_sizes': sizes,
        'actual_vertices': len(vertices), 'actual_unit_edges': len(edges),
        'local_squared_distances': 210, 'score_events': {'P': 36, 'R': 12},
        'Q_links': 9, 'exact_cases': 512, 'positive_words': 512,
        'single_external_vertex_extension': {
            'outside_vertices': sum(outside_histogram.values()),
            'unit_neighbors_in_W_histogram': {str(k): v for k, v in outside_histogram.items()},
            'maximum_forbidden_colors': 3, 'minimum_available_colors': 2,
            'scope': 'One outside vertex at a time, for the fixed W-only expression; not a common law or simultaneous extension.'},
        'case_count_by_defect_number': {str(d): len(xs) for d, xs in sorted(by_size.items())},
        'minimum_score_by_defect_number': {str(d): min(xs) for d, xs in sorted(by_size.items())},
        'independent_integer_search_nodes': total_nodes,
        'coefficientwise_minimal_penalties': penalties, 'minimum_penalty_sum': 12,
        'necessary_inequalities': ['36p+12r+12(1-q) >= 9', '14p+4(1-q) >= 1'],
        'at_p_1_over_27_q_at_most': str(boundary_q),
        'uses_sat_or_floating_point': False, 'scope': cert['scope'],
    }



def check_envelope(envelope, lift):
    """Complete lower envelope from integer dual rows and rational positive laws.

    The caller must have independently verified every case minimum in lift.
    The four rows give pointwise lower bounds, and the five breakpoint laws
    attain their maximum. Convex mixtures of consecutive laws cover every q.
    Individual P/R event means are deliberately not imposed in this model.
    """
    require(literal_tree(envelope), 'envelope uses exact literals')
    require(envelope['schema'] == 'q-defect-balanced-score-envelope-v1', 'envelope schema')
    require(envelope['lift_certificate_sha256'] == digest(lift), 'envelope source binding')
    rows = envelope['facets']
    require(len(rows) == 4, 'four lower envelope pieces')
    aggregate = []
    for row in rows:
        constant = row['constant_twice']
        weights = row['same_coefficients_twice']
        require(type(constant) is int and len(weights) == 9 and
                all(type(x) is int for x in weights), 'integer dual row')
        aggregate.append((constant, sum(weights)))
        for case in lift['cases']:
            rhs = constant + sum(w for j, w in enumerate(weights)
                                 if not ((case['mask'] >> j) & 1))
            require(2 * case['minimum'] >= rhs, 'pointwise envelope dual inequality')
    require(aggregate == [(6, 2), (5, 5), (3, 9), (-6, 24)], 'four exact aggregate lines')
    expected_q = [F(0), F(1, 3), F(1, 2), F(3, 5), F(1)]
    laws = envelope['breakpoint_laws']
    require(len(laws) == 5, 'all five breakpoints')
    def rational(text):
        require(type(text) is str, 'rational string')
        value = F(text)
        require(str(value) == text, 'canonical rational string')
        return value
    boundary = []
    total_atoms = 0
    for q, law in zip(expected_q, laws):
        require(rational(law['q']) == q, 'ordered exact breakpoint')
        masks = [a['mask'] for a in law['atoms']]
        require(len(masks) == len(set(masks)) and
                all(type(m) is int and 0 <= m < 512 for m in masks), 'distinct valid atom masks')
        masses = [rational(a['weight']) for a in law['atoms']]
        require(all(x > 0 for x in masses) and sum(masses) == 1, 'positive probability law')
        require(all(sum(w for m, w in zip(masks, masses) if not ((m >> j) & 1)) == q
                    for j in range(9)), 'each of nine Q events has the same mean')
        score = sum(lift['cases'][m]['minimum'] * w for m, w in zip(masks, masses))
        lower = max(F(c + a*q, 2) for c, a in aggregate)
        require(score == rational(law['minimum_expected_score']) == lower,
                'positive breakpoint law attains the exact lower envelope')
        total_atoms += len(masks)
        boundary.append({'q': str(q), 'minimum_expected_score': str(score),
                         'atoms': len(masks)})
    for i, (c, a) in enumerate(aggregate):
        # An affine difference nonnegative at both ends is nonnegative on
        # the whole segment; no sampled grid substitutes for the interval.
        for q in expected_q[i:i+2]:
            require(F(c+a*q, 2) == max(F(d+b*q, 2) for d, b in aggregate),
                    'the stated line is active throughout its interval')
    # The old 12p+3r>=2 and r>=0 imply S_mean=36p+12r>=6.
    # Each of the first three lines is at most 6 on the whole unit interval.
    require(all(max(F(c, 2), F(c+a, 2)) <= 6 for c, a in aggregate[:3]),
            'first three pieces redundant under the old PR count')
    return {
        'schema': 'balanced-score-lower-envelope-replay-v1',
        'envelope_certificate_sha256': digest(envelope),
        'pointwise_integer_dual_checks': 4 * 512,
        'breakpoints': boundary, 'positive_atom_occurrences': total_atoms,
        'individual_Q_mean_checks': 5 * 9,
        'lower_envelope': 'max(3+q, (5+5q)/2, (3+9q)/2, 12q-3)',
        'intervals': ['[0,1/3]', '[1/3,1/2]', '[1/2,3/5]', '[3/5,1]'],
        'first_three_pieces_redundant_under_old_PR_count': True,
        'scope': envelope['scope'],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    cert = read(CERT)
    parent = read(ROOT / 'certificates/q_pr_joint_cuts.json')
    g = read(ROOT / 'certificates/Y_full_geometry.json.gz')
    b = read(ROOT / 'certificates/g14_pair_orbit_basis.json.gz')
    r = read(ROOT / 'certificates/g14_r_pair_orbit_basis.json.gz')
    prepared = prepare(parent, g, b, r)
    report = check(cert, parent, prepared)
    envelope = read(ENVELOPE)
    report['balanced_score_envelope'] = check_envelope(envelope, cert)
    if args.self_test:
        mutations = {
            'wrong-schema': lambda c: c.__setitem__('schema', 'invalid'),
            'wrong-base': lambda c: c.__setitem__('base_commit', '0' * 40),
            'wrong-parent': lambda c: c.__setitem__('joint_certificate_sha256', '0' * 64),
            'wrong-geometry': lambda c: c.__setitem__('geometry_semantic_sha256', '0' * 64),
            'smaller-penalty': lambda c: c['penalties'].__setitem__(0, 1),
            'nonminimal-penalty': lambda c: c['penalties'].__setitem__(7, 1),
            'float-penalty': lambda c: c['penalties'].__setitem__(0, 2.0),
            'bool-penalty': lambda c: c['penalties'].__setitem__(0, True),
            'wrong-threshold': lambda c: c.__setitem__('threshold', 8),
            'missing-case': lambda c: c['cases'].pop(),
            'duplicated-mask': lambda c: c['cases'][1].__setitem__('mask', 0),
            'improper-word': lambda c: c['cases'][0].__setitem__('word', '0' * 21),
            'invalid-color': lambda c: c['cases'][0].__setitem__('word', '9' * 21),
            'short-word': lambda c: c['cases'][0].__setitem__('word', '01234'),
            'false-minimum': lambda c: c['cases'][0].__setitem__('minimum', 8),
        }
        for name, mutate in mutations.items():
            damaged = deepcopy(cert)
            mutate(damaged)
            try:
                check(damaged, parent, prepared, replay_minima=False)
            except (ValueError, KeyError, TypeError, IndexError):
                continue
            raise ValueError('mutation not rejected: ' + name)
        envelope_mutations = {
            'wrong-envelope-source': lambda c: c.__setitem__('lift_certificate_sha256', '0' * 64),
            'missing-envelope-facet': lambda c: c['facets'].pop(),
            'false-envelope-row': lambda c: c['facets'][0].__setitem__('constant_twice', 8),
            'float-envelope-coefficient': lambda c: c['facets'][0]['same_coefficients_twice'].__setitem__(0, 0.0),
            'missing-breakpoint': lambda c: c['breakpoint_laws'].pop(),
            'wrong-breakpoint-q': lambda c: c['breakpoint_laws'][1].__setitem__('q', '1/4'),
            'wrong-breakpoint-score': lambda c: c['breakpoint_laws'][1].__setitem__('minimum_expected_score', '3'),
            'wrong-breakpoint-weight': lambda c: c['breakpoint_laws'][1]['atoms'][0].__setitem__('weight', '1/5'),
            'negative-weight': lambda c: c['breakpoint_laws'][1]['atoms'][0].__setitem__('weight', '-1/6'),
            'wrong-breakpoint-mask': lambda c: c['breakpoint_laws'][0]['atoms'][0].__setitem__('mask', 0),
        }
        for name, mutate in envelope_mutations.items():
            damaged = deepcopy(envelope)
            mutate(damaged)
            try:
                check_envelope(damaged, cert)
            except (ValueError, KeyError, TypeError, IndexError):
                continue
            raise ValueError('envelope mutation not rejected: ' + name)
        # Exercise the negative checker itself, not only certificate plumbing.
        model = build_case(*prepared[:4], 0)
        try:
            exclude_lower_score(*model, 10)
        except ValueError:
            pass
        else:
            raise ValueError('negative checker missed the score-nine word')
        # A real negative check may not silently disappear under -O.
        proc = subprocess.run([sys.executable, '-O', str(Path(__file__).resolve())],
                              capture_output=True, text=True)
        require(proc.returncode != 0 and 'not -O' in proc.stderr, 'optimized mode rejected')
        print(json.dumps({'self_test': 'PASS', 'certificate_mutations_rejected': len(mutations),
                          'envelope_mutations_rejected': len(envelope_mutations),
                          'false_lower_bound_rejected': True, 'optimized_mode_rejected': True}, sort_keys=True))
    if args.write_receipt:
        RECEIPT.write_bytes(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n')
    else:
        require(read(RECEIPT) == report, 'saved receipt matches independent replay')
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    main()
