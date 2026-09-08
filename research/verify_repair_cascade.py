"""Independent exact geometry, full rigid-overlap coverage, and repair automaton.

No imports from the search constructor, its compiler, or its field arithmetic.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
import hashlib
import json

RADICALS = (1, 3, 11, 33)
ZERO, ONE = (F(0),)*4, (F(1), F(0), F(0), F(0))


def plus(a, b):
    return tuple(x+y for x, y in zip(a, b))


def minus(a, b):
    return tuple(x-y for x, y in zip(a, b))


def times(a, b):
    result = [F(0)]*4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            common = gcd(RADICALS[i], RADICALS[j])
            index = RADICALS.index(RADICALS[i]*RADICALS[j]//common**2)
            result[index] += x*y*common
    return tuple(result)


def distance(p, q):
    x, y = (minus(a, b) for a, b in zip(p, q))
    return plus(times(x, x), times(y, y))


def determinant(a, b, c):
    u, v = [minus(x, y) for x, y in zip(b, a)], [minus(x, y) for x, y in zip(c, a)]
    return minus(times(u[0], v[1]), times(u[1], v[0]))


def read_points(data):
    result = [tuple(tuple(map(F, axis)) for axis in p) for p in data['points']]
    assert all(len(p) == 2 and all(len(a) == 4 for a in p) for p in result)
    assert len(result) == len(set(result))
    return result


def verify_overlap(boundary, saved):
    # Two equal-length ordered pairs determine exactly two planar isometries.
    # Two distances and a signed area identify every further point uniquely.
    # Search used dot-product profiles; this checker uses distance profiles.
    distances = {(a, b): distance(boundary[a], boundary[b])
                 for a in range(14) for b in range(14)}
    length_groups, signatures = defaultdict(list), {}
    for a, b in permutations(range(14), 2):
        length_groups[distances[a, b]].append((a, b))
        signatures[a, b] = [(distances[a, k], distances[b, k],
                              determinant(boundary[a], boundary[b], boundary[k]))
                             for k in range(14)]
    histogram, fours = Counter(), []
    for group in length_groups.values():
        for source, target in product(group, repeat=2):
            target_table = {key: i for i, key in enumerate(signatures[target])}
            assert len(target_table) == 14
            for sign in (1, -1):
                pairs = []
                for i, (d1, d2, area) in enumerate(signatures[source]):
                    key = d1, d2, tuple(sign*x for x in area)
                    if key in target_table:
                        pairs.append([i, target_table[key]])
                histogram[len(pairs)] += 1
                if len(pairs) == 14:
                    assert pairs == [[i, i] for i in range(14)] and sign == 1
                else:
                    assert len(pairs) <= 4
                if len(pairs) == 4:
                    fours.append(dict(source=list(source), target=list(target),
                                      orientation=sign, mapping=pairs))
    assert dict(histogram) == {14: 182, 2: 958, 4: 36}
    assert saved['anchor_cases'] == sum(histogram.values()) == 1176
    assert saved['overlap_histogram'] == {str(k): v for k, v in sorted(histogram.items())}
    assert saved['four_overlap_anchor_witnesses'] == fours
    assert saved['max_nonidentity_overlap'] == 4
    # T044: every four-point intersection is the union of two boundary edges.
    four_maps = {tuple(tuple(pair) for pair in w['mapping']) for w in fours}
    assert len(four_maps) == 3
    for mapping in four_maps:
        for side in (0, 1):
            common = {pair[side] for pair in mapping}
            assert all((v ^ 1) in common for v in common)
            for triple in combinations(common, 3):
                assert any((v ^ 1) in triple for v in triple)
    # Each equal-length ordered source pair allows two isometries.
    nonunit = [len(group)//2 for length, group in length_groups.items() if length != ONE]
    assert Counter(nonunit) == {1: 78, 2: 1, 4: 1}
    return dict(anchor_cases=1176, histogram=dict(histogram), maximum_distinct_overlap=4,
                same_color_repair_edge_intersection_bound=2,
                nonunit_distance_multiplicity_histogram=dict(Counter(nonunit)),
                maximum_gate_poses_through_nonunit_pair=16)


def verify_compiler_automaton():
    # A local choice is ordered old colors a != b and no/left/right recoloring.
    # State records exactly the quantities relevant to the complete predicate:
    # common old palette (0 if not constant), common output palette, all-pair
    # forbidden-beta mask, and whether any vertex has been selected.
    # Each transition depends only on this state. Thus the quotient covers all
    # 36^r concrete inputs, not a sampling of length-r words.
    local = []
    for a, b in permutations(range(4), 2):
        for choice in (-1, 0, 1):
            out = (4 if choice == 0 else a, 4 if choice == 1 else b)
            beta = 0 if choice == -1 else 1 << (b if choice == 0 else a)
            local.append(((1 << a) | (1 << b), (1 << out[0]) | (1 << out[1]),
                          beta, choice != -1))
    assert len(local) == 36
    states, counts, transitions = set(local), [], 0
    for r in range(1, 8):
        for old, out, blocked, selected in states:
            formula_accepts = not (old and not selected) and not blocked
            actual_accepts = out == 0
            assert formula_accepts == actual_accepts
        counts.append(len(states))
        if r == 7:
            break
        following = set()
        for (old, out, blocked, selected), (a, b, beta, sel) in product(states, local):
            following.add((old if old == a else 0, out if out == b else 0,
                           blocked & beta, selected or sel))
            transitions += 1
        if r >= 2:
            assert following == states
        states = following
    return dict(local_inputs=36, states_by_pair_count=counts,
                transitions=transitions, seven_pair_inputs_covered=36**7)


def verify(root):
    base_file = root/'certificates/spindle_pair_gate.json'
    base_data = json.loads(base_file.read_text())
    data = json.loads((root/'certificates/gate_repair_cascade.json').read_text())
    assert data['schema'] == 1 and data['radicals'] == list(RADICALS)
    assert data['base_sha256'] == hashlib.sha256(base_file.read_bytes()).hexdigest()
    base, points = read_points(base_data), read_points(data)
    assert len(base) == 21 and len(points) == 161
    overlap = verify_overlap(base[7:], data['overlap'])
    distances = {(a, b): distance(points[a], points[b]) for a, b in combinations(range(161), 2)}
    actual_edges = [list(pair) for pair, value in distances.items() if value == ONE]
    assert actual_edges == data['induced_edges'] and len(actual_edges) == 256
    modules, gates = data['modules'], data['boundary_pairs']
    assert len(modules) == len(gates) == 8
    expected_edges, interior, boundary = set(), set(), set()
    base_distances = {(a, b): distance(base[a], base[b]) for a, b in combinations(range(21), 2)}
    for m, pairs in zip(modules, gates):
        assert len(m) == len(set(m)) == 21 and all(0 <= i < 161 for i in m)
        assert pairs == [[m[a], m[b]] for a, b in base_data['boundary_pairs']]
        assert not interior.intersection(m[:7])
        interior.update(m[:7])
        boundary.update(m[7:])
        for (a, b), value in base_distances.items():
            assert distances[tuple(sorted((m[a], m[b])))] == value
        expected_edges.update(tuple(sorted((m[a], m[b]))) for a, b in base_data['induced_edges'])
    assert not interior.intersection(boundary)
    assert len(interior) == 56 and len(boundary) == 105
    assert interior | boundary == set(range(161))
    assert actual_edges == [list(e) for e in sorted(expected_edges)]
    c = data['initial_boundary_coloring']
    assert len(c) == 161
    assert all(c[i] == -1 for i in interior)
    assert all(c[i] in range(4) for i in boundary)
    boundary_edges = [(a, b) for a, b in actual_edges if a in boundary and b in boundary]
    assert len(boundary_edges) == 56 and all(c[a] != c[b] for a, b in boundary_edges)
    trace = []
    for chosen in ([], data['initial_repair'], data['exchanged_repair']):
        assert len(chosen) == len(set(chosen)) and set(chosen) <= boundary
        recolored = [4 if v in chosen else c[v] for v in range(161)]
        assert all(recolored[a] != recolored[b] for a, b in boundary_edges)
        bad = []
        for j, pairs in enumerate(gates):
            palettes = [{recolored[a], recolored[b]} for a, b in pairs]
            assert all(len(p) == 2 for p in palettes)
            if all(p == palettes[0] for p in palettes):
                bad.append(j)
        trace.append(bad)
    assert trace == data['bad_gate_trace'] == [list(range(1, 8)), [0], []]
    assert len(data['initial_repair']) == len(data['exchanged_repair']) == 7
    assert len(set(data['initial_repair']) ^ set(data['exchanged_repair'])) == 2
    full = data['final_five_coloring']
    assert len(full) == 161 and all(v in range(5) for v in full)
    assert all(full[a] != full[b] for a, b in actual_edges)
    assert all(full[v] == (4 if v in data['exchanged_repair'] else c[v]) for v in boundary)
    four = data['unrestricted_four_coloring']
    assert len(four) == 161 and all(v in range(4) for v in four)
    assert all(four[a] != four[b] for a, b in actual_edges)
    spindle = [(a, b) for a, b in actual_edges if a < 7 and b < 7]
    assert not any(all(w[a] != w[b] for a, b in spindle) for w in product(range(3), repeat=7))
    # Independently reconstruct every clause from the point-level coloring.
    clauses = [[-a-1, -b-1] for a, b in boundary_edges]
    for pairs in gates:
        all_colors = [{c[a], c[b]} for a, b in pairs]
        if all(x == all_colors[0] for x in all_colors):
            clauses.append([v+1 for pair in pairs for v in pair])
        for beta in range(4):
            if all(beta in s for s in all_colors):
                clauses.append([-(a if c[a] != beta else b)-1 for a, b in pairs])
    assert data['repair_cnf'] == clauses
    for selected, expected in ((set(data['initial_repair']), False),
                               (set(data['exchanged_repair']), True)):
        assert all(any((abs(lit)-1 in selected) == (lit > 0) for lit in clause)
                   for clause in clauses) == expected
    # Exact LLL substitution x=1/(D+1), with p=1/64 and D=22.
    assert F(1, 64) <= F(1, 23)*F(22, 23)**22
    packing_bound = lambda v: (v*(((v-1)*((v-2)//5))//6))//7
    assert packing_bound(31) == 110 and packing_bound(32) == 141
    assert all(packing_bound(v) < 128 for v in range(7, 32))
    return dict(status='VERIFIED_RIGID_OVERLAP_AND_REPAIRABLE_CASCADE', overlap=overlap,
                vertices=161, all_pairs=len(distances), induced_edges=256,
                bad_gate_trace=trace, complete_five_coloring=True,
                unrestricted_chromatic_number=4,
                repair_cnf_clauses=len(clauses), compiler=verify_compiler_automaton(),
                scope='Seven-bad-gate theorem uses written proof; not a new HN bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
