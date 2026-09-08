"""Independent positive-cover, negative-list, and two-port relation checks."""
from itertools import combinations, product
from pathlib import Path
import gzip
import json
from verify_coupled_gate import verify as verify_coupled_geometry

SPINDLE = ((0,1),(0,2),(0,4),(0,5),(1,2),(1,3),(2,3),(3,6),(4,5),(4,6),(5,6))


def verify(root):
    data = json.loads(gzip.decompress((root/'certificates/spindle_joint_support.json.gz').read_bytes()))
    assert data['schema'] == 1
    saved = data['equal_lists']
    lists = [set(c) for c in combinations(range(5),3)]
    assert saved['root_list'] == [0,1,2]
    assert saved['normalized_cases'] == 1000000
    covered = bytearray(1000000)
    unique_pairs = set()
    for raw in saved['positive_pairs']:
        assert len(raw) == 2
        a,b = tuple(raw[0]),tuple(raw[1])
        assert (a,b) not in unique_pairs
        unique_pairs.add((a,b))
        for w in (a,b):
            assert len(w) == 7 and all(type(c) is int and 0 <= c < 5 for c in w)
            assert w[0] in {0,1,2} and all(w[x] != w[y] for x,y in SPINDLE)
        assert all(x != y for x,y in zip(a,b))
        indices = [0]
        for v in range(1,7):
            choices = [i for i,L in enumerate(lists) if {a[v],b[v]} <= L]
            assert len(choices) == 3
            indices = [10*i+j for i in indices for j in choices]
        assert len(indices) == 729
        for i in indices:
            covered[i] = 1
    assert sum(covered) == saved['positive_cases'] == 999915
    negatives = set(); kinds = {'empty':0,'forced':0}
    for record in saved['negative_cases']:
        ids = record['lists']
        assert len(ids) == 7 and ids[0] == 0 and all(type(i) is int and 0 <= i < 10 for i in ids)
        code = 0
        for i in ids[1:]:
            code = 10*code+i
        assert code not in negatives and not covered[code]
        negatives.add(code)
        words = [w for w in product(*(sorted(lists[i]) for i in ids))
                 if all(w[x] != w[y] for x,y in SPINDLE)]
        kind = record['reason']; assert kind in kinds
        kinds[kind] += 1
        if kind == 'empty':
            assert not words
        else:
            v,c = record['vertex'],record['color']
            assert type(v) is int and 0 <= v < 7 and type(c) is int and 0 <= c < 5
            assert words and all(w[v] == c for w in words)
        covered[code] = 2
    assert kinds == {'empty':1,'forced':84} and len(negatives) == 85
    assert all(covered)

    # T050's right diamond factor: a pair of nonempty residual lists fails
    # iff both are the same singleton. Directly verify all lists of size>=3.
    big_lists = [set(s) for n in range(3,6) for s in combinations(range(5),n)]
    diamond_cases = 0
    for D,E,x,z in product(big_lists,big_lists,range(5),range(5)):
        actual = any(d != e and d not in {x,z} and e not in {x,z} for d,e in product(D,E))
        predicted = not (x != z and D == E and len(D) == 3 and {x,z} <= D)
        assert actual == predicted
        diamond_cases += 1
    assert diamond_cases == 6400
    # T050's left factor, independently enumerate triangles after fixing x,z.
    left_cases = 0
    for A,B,C,x,z in product(big_lists,big_lists,big_lists,range(5),range(5)):
        actual = any(a != b and a != c and b != c and a != x and b != x and c != z
                     for a,b,c in product(A,B,C))
        forbidden = A == B and len(A) == 3 and x in A and C-(A-{x}) == {z}
        assert actual == (not forbidden)
        left_cases += 1
    assert left_cases == 102400

    verify_coupled_geometry(root)
    source = json.loads((root/'certificates/coupled_gate.json').read_text())
    mapping = {tuple(r):v for v,refs in enumerate(source['occurrences']) for r in refs}
    edges = [tuple(e) for e in source['unit_edges']]
    asym = data['asymmetric']
    missing = [[2,1,1,1,3,3,1],[1,3,3,3,1,1,1]]
    assert asym['missing_colors'] == missing
    boundary = {int(v):c for v,c in asym['boundary'].items()}
    assert set(boundary) == {mapping[p,v] for p in range(2) for v in range(7,21)}
    assert set(boundary.values()) == {1,2,3,4}
    for p in range(2):
        for v in range(7):
            expected = [4,missing[p][v]] if p == 0 else [missing[p][v],4]
            assert [boundary[mapping[p,7+2*v+k]] for k in range(2)] == expected
    assert all(boundary[a] != boundary[b] for a,b in edges if a in boundary and b in boundary)
    words = []
    for p in range(2):
        L = [set(range(5)) - {boundary[mapping[p,7+2*v]],boundary[mapping[p,8+2*v]]} for v in range(7)]
        words.append([w for w in product(*(sorted(s) for s in L)) if all(w[a] != w[b] for a,b in SPINDLE)])
    assert list(map(len,words)) == asym['standalone_counts'] == [20,12]
    assert {(w[0],w[6]) for w in words[0]} == set(map(tuple,asym['left_two_port_support'])) == {(0,3),(1,3),(3,0),(3,2)}
    assert {(w[0],w[6]) for w in words[1]} == set(map(tuple,asym['right_two_port_support'])) == {(3,3)}
    assert len(asym['edgewise_witnesses']) == 7
    for v,(a,b) in enumerate(asym['edgewise_witnesses']):
        assert tuple(a) in words[0] and tuple(b) in words[1] and a[v] != b[v]
    assert all(a[0] == b[0] or a[6] == b[6] for a,b in product(*words))
    assert asym['joint_count'] == 0
    repair = asym['repair']; v = repair['vertex']
    assert v in boundary and repair['color'] == 0
    b = dict(boundary);b[v] = 0
    w = repair['word']
    assert len(w) == 40 and all(type(c) is int and 0 <= c < 5 for c in w)
    assert all(w[v] == c for v,c in b.items()) and all(w[a] != w[b] for a,b in edges)
    return dict(status='VERIFIED_SPINDLE_JOINT_SUPPORT', normalized_cases=1000000,
                full_equal_list_cases=10000000, positive_pair_certificates=len(unique_pairs),
                normalized_positive=999915, normalized_empty=1, normalized_forced=84,
                diamond_factor_cases=diamond_cases, triangle_factor_cases=left_cases,
                asymmetric_words=[20,12], asymmetric_pair_checks=240,
                individually_feasible_cross_edges=7, jointly_conflicting_cross_edges=2,
                one_point_repair_vertex=v, scope='Equal-list classification and fixed asymmetric boundary; no new HN bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
