"""Cover equal-list matching doubles, then exhibit a two-contact joint gap."""
from itertools import combinations, product
from pathlib import Path
import json
import gzip

EDGES = ((0,1),(0,2),(0,4),(0,5),(1,2),(1,3),(2,3),(3,6),(4,5),(4,6),(5,6))
LISTS = tuple(combinations(range(5),3))


def build(root):
    words = [w for w in product(range(5),repeat=7) if all(w[a] != w[b] for a,b in EDGES)]
    masks = [[0]*5 for _ in range(7)]
    for i,w in enumerate(words):
        for v,c in enumerate(w):
            masks[v][c] |= 1 << i
    all_words = (1 << len(words))-1
    allowed = [[sum(masks[v][c] for c in L) for L in LISTS] for v in range(7)]
    compatible = []
    for w in words:
        S = all_words
        for v,c in enumerate(w):
            S &= all_words ^ masks[v][c]
        compatible.append(S)
    # Normalize L(o)={0,1,2}; all 10 root lists are equivalent by color relabeling.
    covered = bytearray(10**6)
    positive_pairs, negatives = [], []
    powers = [10**i for i in range(5,-1,-1)]
    for ids in product(range(10),repeat=6):
        code = sum(i*p for i,p in zip(ids,powers))
        if covered[code]:
            continue
        S = allowed[0][0]
        for v,i in enumerate(ids,1):
            S &= allowed[v][i]
        if not S:
            negatives.append(dict(lists=[0]+list(ids), reason='empty'))
            continue
        forced = next(((v,c) for v in range(7) for c in range(5) if S & masks[v][c] == S), None)
        if forced is not None:
            negatives.append(dict(lists=[0]+list(ids),reason='forced',vertex=forced[0],color=forced[1]))
            continue
        remaining = S
        while remaining:
            bit = remaining & -remaining; i = bit.bit_length()-1
            partners = compatible[i] & S
            if partners:
                j = (partners & -partners).bit_length()-1
                break
            remaining ^= bit
        else:
            raise AssertionError(('Non-unary obstruction',ids))
        a,b = words[i],words[j]
        positive_pairs.append([a,b])
        # The two words use two distinct colors at each vertex. Every list
        # containing those two colors is covered, not only the searched input.
        choices = [[k for k,L in enumerate(LISTS) if a[v] in L and b[v] in L] for v in range(1,7)]
        for pattern in product(*choices):
            covered[sum(i*p for i,p in zip(pattern,powers))] = 1
    assert sum(covered) == 999915 and len(negatives) == 85
    assert sum(n['reason'] == 'empty' for n in negatives) == 1

    source = json.loads((root/'certificates/coupled_gate.json').read_text())
    mapping = {tuple(r):v for v,refs in enumerate(source['occurrences']) for r in refs}
    missing = ((2,1,1,1,3,3,1),(1,3,3,3,1,1,1))
    boundary = {}
    for pose in range(2):
        for v in range(7):
            colors = (4,missing[pose][v]) if pose == 0 else (missing[pose][v],4)
            for k,c in enumerate(colors):
                physical = mapping[pose,7+2*v+k]
                assert physical not in boundary or boundary[physical] == c
                boundary[physical] = c
    edges = [tuple(e) for e in source['unit_edges']]
    assert all(boundary[a] != boundary[b] for a,b in edges if a in boundary and b in boundary)

    def local_words(b,pose):
        lists = [sorted(set(range(5)) - {b[mapping[pose,7+2*v]],b[mapping[pose,8+2*v]]}) for v in range(7)]
        return [w for w in product(*lists) if all(w[a] != w[z] for a,z in EDGES)]

    left,right = [local_words(boundary,p) for p in range(2)]
    assert (len(left),len(right)) == (20,12)
    assert {tuple(w[v] for v in (0,6)) for w in left} == {(0,3),(1,3),(3,0),(3,2)}
    assert {tuple(w[v] for v in (0,6)) for w in right} == {(3,3)}
    assert all(a[0] == b[0] or a[6] == b[6] for a,b in product(left,right))
    edgewise = [next([a,b] for a,b in product(left,right) if a[v] != b[v]) for v in range(7)]
    repair = None
    for vertex in sorted(boundary):
        b = dict(boundary);b[vertex] = 0  # The original boundary omits0.
        l,r = [local_words(b,p) for p in range(2)]
        pair = next(((a,z) for a,z in product(l,r) if all(a[i] != z[i] for i in range(7))),None)
        if pair is not None:
            w = dict(b)
            for p,local in enumerate(pair):
                w.update({mapping[p,i]:c for i,c in enumerate(local)})
            assert all(w[a] != w[z] for a,z in edges)
            repair = dict(vertex=vertex,color=0,word=[w[v] for v in range(40)])
            break
    assert repair is not None
    return dict(schema=1,equal_lists=dict(root_list=[0,1,2],normalized_cases=10**6,
        positive_cases=sum(covered), negative_cases=negatives,positive_pairs=positive_pairs),
        asymmetric=dict(missing_colors=missing,boundary=boundary,
                        standalone_counts=[20,12],left_two_port_support=[[0,3],[1,3],[3,0],[3,2]],
                        right_two_port_support=[[3,3]], edgewise_witnesses=edgewise,
                        joint_count=0,repair=repair))


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = build(root)
    payload = json.dumps(data,separators=(',',':')).encode()
    (root/'certificates/spindle_joint_support.json.gz').write_bytes(gzip.compress(payload,mtime=0))
    print(json.dumps(dict(positive_pairs=len(data['equal_lists']['positive_pairs']),
                          normalized_positive_cases=data['equal_lists']['positive_cases'],
                          normalized_negatives=len(data['equal_lists']['negative_cases']),
                          asymmetric_standalone_counts=data['asymmetric']['standalone_counts'],
                          repair_vertex=data['asymmetric']['repair']['vertex'])))
