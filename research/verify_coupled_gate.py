"""Independent all-pairs verification of the coupled gate boundary obstruction.

Recomputes field arithmetic using squarefree-radical gcd multiplication, not
the generator's bit-mask multiplication or search backtracker.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import gcd
from pathlib import Path
import json


def verify(root):
    data = json.loads((root / 'certificates/coupled_gate.json').read_text())
    assert data['schema'] == 1
    radicals = (1, 3, 11, 33)
    points = [tuple(tuple(F(c) for c in a) for a in p) for p in data['vertices']]
    assert len(points) == len(set(points)) == 40
    assert all(len(p) == 2 and all(len(a) == 4 for a in p) for p in points)
    assert list(map(F, data['coordinate_scale_factor'])) == [F(1,3),0,0,0]
    unit = [F(1,9),F(0),F(0),F(0)]
    assert list(map(F, data['unit_quadrance_scaled'])) == unit

    def square(a):
        result = [F(0)] * 4
        for i, x in enumerate(a):
            for j, y in enumerate(a):
                g = gcd(radicals[i], radicals[j])
                result[radicals.index(radicals[i] * radicals[j] // g**2)] += g*x*y
        return result

    def distance(a, b):
        xx, yy = [square([x-y for x,y in zip(a[k], b[k])]) for k in range(2)]
        return [x+y for x,y in zip(xx, yy)]

    pairs = list(combinations(range(40), 2))
    assert len(data['all_pair_quadrances']) == len(pairs) == 780
    edges = set()
    for (a,b), saved in zip(pairs, data['all_pair_quadrances']):
        assert saved['pair'] == [a,b]
        d = distance(points[a], points[b])
        assert d == list(map(F, saved['quadrance']))
        if d == unit:
            edges.add((a,b))
    assert sorted(edges) == [tuple(e) for e in data['unit_edges']]
    assert len(edges) == data['unit_edge_count'] == 81

    mapping = {}
    assert len(data['occurrences']) == 40
    for v, refs in enumerate(data['occurrences']):
        assert refs
        for raw in refs:
            ref = tuple(raw)
            assert len(ref) == 2 and ref not in mapping
            mapping[ref] = v
    assert set(mapping) == set(product(range(2), range(21)))
    shared = [refs for refs in data['occurrences'] if len(refs) > 1]
    assert shared == [[[0,9],[1,10]], [[0,15],[1,16]]]
    assert shared == data['shared_boundary_occurrences']
    spindle = {(0,1),(0,2),(0,4),(0,5),(1,2),(1,3),(2,3),(3,6),(4,5),(4,6),(5,6)}
    gate_edges = set(spindle)
    for v in range(7):
        gate_edges.update(((v,7+2*v),(v,8+2*v),(7+2*v,8+2*v)))
    local_union = set()
    def edge(a,b):
        return tuple(sorted((a,b)))
    # Check complete distance matrices against the independently certified
    # base gate, not merely the chosen edges, to establish congruence.
    base = json.loads((root / 'certificates/spindle_pair_gate.json').read_text())
    bp = [tuple(tuple(F(c) for c in a) for a in p) for p in base['points']]
    for pose in range(2):
        for a,b in combinations(range(21),2):
            actual = distance(points[mapping[pose,a]], points[mapping[pose,b]])
            assert actual == [x/9 for x in distance(bp[a],bp[b])]
            assert (actual == unit) == ((a,b) in gate_edges)
        local_union.update(edge(mapping[pose,a], mapping[pose,b]) for a,b in gate_edges)
    assert len(local_union) == 64
    interior_cross = {edge(mapping[0,v], mapping[1,v]) for v in range(7)}
    boundary_cross = {edge(mapping[0,v], mapping[1,v]) for v in (7,8,11,12,13,14,17,18,19,20)}
    assert edges - local_union == interior_cross | boundary_cross
    assert len(interior_cross) == 7 and len(boundary_cross) == 10

    boundary = {int(v): c for v,c in data['boundary_coloring'].items()}
    assert set(boundary) == {mapping[p,v] for p in range(2) for v in range(7,21)}
    assert len(boundary) == 26 and set(boundary.values()) == {0,3,4}
    for pose in range(2):
        for v in range(7):
            colors = [3,4] if v == 0 else [0,4]
            if pose:
                colors.reverse()
            for offset, c in enumerate(colors):
                local = 7+2*v+offset
                assert boundary[mapping[pose,local]] == c
                assert data['boundary_occurrence_coloring'][f'{pose}:{local}'] == c
    bedges = {e for e in edges if all(v in boundary for v in e)}
    assert sorted(bedges) == [tuple(e) for e in data['boundary_unit_edges']]
    assert len(bedges) == 24 and all(boundary[a] != boundary[b] for a,b in bedges)
    lists = [set(range(5)) - {boundary[mapping[0,7+2*v]], boundary[mapping[0,8+2*v]]}
             for v in range(7)]
    assert lists == [{0,1,2}] + [{1,2,3}]*6
    assert {int(v): set(cs) for v,cs in data['standalone_spindle_lists'].items()} == dict(enumerate(lists))
    words = [w for w in product(*(sorted(L) for L in lists))
             if all(w[a] != w[b] for a,b in spindle)]
    assert len(words) == 24 and {w[0] for w in words} == {0}
    assert data['standalone_spindle_counts'] == [24,24]
    assert data['standalone_root_support'] == [[0],[0]]
    for raw in data['standalone_spindle_witnesses']:
        assert tuple(raw[str(v)] for v in range(7)) in words
    assert len(data['standalone_spindle_witnesses']) == 2
    roots = edge(mapping[0,0], mapping[1,0])
    assert roots in edges and list(roots) == data['joint_failure_edge']
    # Exhaust all 24 x 24 independently reconstructed extensions of the two
    # separate gates. Every pair fails the root edge; no SAT status is used.
    assert all(a[0] == b[0] for a,b in product(words, repeat=2))
    assert data['joint_fixed_boundary_list_colorings'] == 0
    coloring = {int(v):c for v,c in data['full_unrestricted_4_coloring'].items()}
    assert set(coloring) == set(range(40)) and all(type(c) is int and 0 <= c < 4 for c in coloring.values())
    assert all(coloring[a] != coloring[b] for a,b in edges)
    assert not any(all(w[a] != w[b] for a,b in spindle) for w in product(range(3),repeat=7))
    return dict(status='VERIFIED_COUPLED_GATE_STRICT_BOUNDARY_RELATION', vertices=40,
                all_pairs=780, induced_edges=81, boundary_vertices=26, boundary_edges=24,
                extra_interior_edges=7, standalone_extensions=[24,24],
                checked_extension_pairs=576, joint_extensions=0, chromatic_number=4,
                scope='One explicit excluded boundary, not a full boundary census; no new HN bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
