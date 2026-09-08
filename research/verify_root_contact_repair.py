"""Independent repair census, local reset lemma, and escaped all-pairs geometry."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from math import gcd
from pathlib import Path
import json
from verify_coupled_gate import verify as verify_coupled_source


def verify(root):
    verify_coupled_source(root)
    data = json.loads((root/'certificates/root_contact_repair.json').read_text())
    assert data['schema'] == 1
    # Direct local calibration for T048: change ONE wing endpoint to fresh4.
    # Enumerate actual triangle colors, rather than invoking its list identity.
    old_pairs = list(combinations(range(4),2))
    local_cases = 0
    for pair, selected, other_pair, tip_pair in product(old_pairs, range(2), old_pairs, old_pairs):
        changed = set(pair); changed.remove(pair[selected]); changed.add(4)
        A = set(range(5))-changed
        B = set(range(5))-set(other_pair)
        C = set(range(5))-set(tip_pair)
        assert A != B and 4 not in A and 4 in B
        for x in range(5):
            tips = {c for a,b,c in product(A,B,C) if a != x and b != x and len({a,b,c}) == 3}
            assert tips == C
            local_cases += 1
    assert local_cases == 2160

    source = json.loads((root/'certificates/coupled_gate.json').read_text())
    boundary = {int(v):c for v,c in source['boundary_coloring'].items()}
    edges = {tuple(e) for e in source['unit_edges']}
    occurrence = {tuple(r):v for v,refs in enumerate(source['occurrences']) for r in refs}
    blocks = [[occurrence[p,v] for v in range(7)] for p in range(2)]
    spindle = ((0,1),(0,2),(0,4),(0,5),(1,2),(1,3),(2,3),(3,6),(4,5),(4,6),(5,6))

    def reconstruct_words(b, block):
        lists = []
        for v in block:
            neighbors = set()
            for a,z in edges:
                if a == v and z in b:
                    neighbors.add(b[z])
                if z == v and a in b:
                    neighbors.add(b[a])
            lists.append(sorted(set(range(5))-neighbors))
        return [w for w in product(*lists) if all(w[a] != w[z] for a,z in spindle)]

    expected_cases = {(v,c) for v in boundary for c in (1,2)}
    seen = set(); counts = Counter(); negatives = []
    for case in data['coupled_one_point_census']:
        key = (case['vertex'],case['new_color'])
        assert key in expected_cases and key not in seen
        seen.add(key)
        b = dict(boundary); b[key[0]] = key[1]
        assert all(b[a] != b[z] for a,z in edges if a in b and z in b)
        left,right = [reconstruct_words(b,block) for block in blocks]
        assert list(map(len,(left,right))) == case['standalone_counts']
        # The source verifier established exactly the corresponding matching
        # as the only extra interior edges; check every pairing, including zero.
        actual = sum(all(a[i] != z[i] for i in range(7)) for a,z in product(left,right))
        assert actual == case['joint_count']
        counts[actual] += 1
        if actual:
            w = case['witness']
            assert len(w) == 40 and all(type(c) is int and 0 <= c < 5 for c in w)
            assert all(w[v] == c for v,c in b.items())
            assert all(w[a] != w[z] for a,z in edges)
        else:
            assert case['witness'] is None
            assert {w[0] for w in left} == {w[0] for w in right} == {0}
            negatives.append(key)
    assert seen == expected_cases and len(seen) == 52
    assert dict(counts) == {0:4,32:40,44:4,72:4}
    assert set(negatives) == {(occurrence[0,7],c) for c in (1,2)} | {(occurrence[1,8],c) for c in (1,2)}

    escaped = data['escaped_root_pair']
    rad = (1,3,11,33,13,39,143,429)
    assert escaped['radicals'] == list(rad)
    pts = [tuple(tuple(F(c) for c in a) for a in p) for p in escaped['points']]
    assert len(pts) == len(set(pts)) == 42
    assert all(len(p) == 2 and all(len(a) == 8 for a in p) for p in pts)

    def square(a):
        result = [F(0)]*8
        for i,x in enumerate(a):
            for j,y in enumerate(a):
                common = gcd(rad[i],rad[j])
                result[rad.index(rad[i]*rad[j]//common**2)] += x*y*common
        return result

    def norm(p,q):
        xx,yy = [square([x-y for x,y in zip(p[k],q[k])]) for k in range(2)]
        return [x+y for x,y in zip(xx,yy)]

    base = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    old = [tuple(tuple(F(c) for c in a)+(F(0),)*4 for a in p) for p in base['points']]
    assert pts[:21] == old
    for (x,y),(nx,ny) in zip(old,pts[21:]):
        assert nx == tuple((-4*a-3*b)/5 + (F(5,8) if i == 0 else 0) for i,(a,b) in enumerate(zip(x,y)))
        assert ny == tuple((3*a-4*b)/5 + (F(1,8) if i == 5 else 0) for i,(a,b) in enumerate(zip(x,y)))
    actual_edges = {(a,b) for a,b in combinations(range(42),2) if norm(pts[a],pts[b]) == [1]+[0]*7}
    local = {tuple(e) for e in base['induced_edges']}
    assert actual_edges == local | {(a+21,b+21) for a,b in local} | {(0,21)}
    assert sorted(actual_edges) == [tuple(e) for e in escaped['edges']]
    assert len(actual_edges) == 65
    # Q(sqrt3,sqrt5,sqrt11) has square classes generated by 3,5,11;
    # sqrt39 introduces the independent square class13. This is not a claim
    # that the abstract graph has no alternative realization in the safe field.
    assert 39 not in (1,3,5,15,11,33,55,165)
    assert pts[21][1][5] == F(1,8)
    b = {int(v):c for v,c in escaped['boundary'].items()}
    expected = {}
    for pose in range(2):
        for i in range(7):
            expected[21*pose+7+2*i],expected[21*pose+8+2*i] = (1,2) if i == 0 else (0,2)
    assert b == expected
    assert all(b[a] != b[z] for a,z in actual_edges if a in b and z in b)
    L = [{0,3,4}] + [{1,3,4}]*6
    words = [w for w in product(*L) if all(w[a] != w[z] for a,z in spindle)]
    assert len(words) == 24 and {w[0] for w in words} == {0}
    assert escaped['original_standalone_counts'] == [24,24] and escaped['original_joint_count'] == 0
    assert all(a[0] == z[0] for a,z in product(words,repeat=2))
    assert escaped['repair_vertex'] == 9 and escaped['repair_color'] == 4
    b[9] = 4
    for name,k in (('repaired_word',5),('unrestricted_four_word',4)):
        w = escaped[name]
        assert len(w) == 42 and all(type(c) is int and 0 <= c < k for c in w)
        assert all(w[a] != w[z] for a,z in actual_edges)
        if k == 5:
            assert all(w[v] == c for v,c in b.items())
    assert not any(all(w[a] != w[z] for a,z in spindle) for w in product(range(3),repeat=7))
    return dict(status='VERIFIED_ROOT_CONTACT_REPAIR', local_reset_cases=local_cases,
                one_point_edits=52, repairable_edits=48, extension_count_histogram=dict(counts),
                escaped_vertices=42, escaped_all_pairs=861, escaped_edges=65,
                escaped_cross_edges=1, escaped_chromatic_number=4,
                scope='T048 uses written proof; root-only hypothesis does not include seven-matching T047')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
