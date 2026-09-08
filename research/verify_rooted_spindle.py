"""Independent direct-triangle verification of the rooted spindle census.

No imports from the generator. The certificate partitions all 1000 ordered
list triples; every signature entry is recomputed by literal color enumeration.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json


def verify(root):
    data = json.loads((root / 'certificates/rooted_spindle.json').read_text())
    assert data['schema'] == 1 and data['palette_size'] == 5 and data['list_size'] == 3
    lists = [frozenset(x) for x in combinations(range(5), 3)]
    masks = {sum(1 << c for c in x): x for x in lists}
    groups, covered = [], set()
    for group in data['groups']:
        signature = tuple(group['signature'])
        assert len(signature) == 5
        members = []
        for raw in group['triples']:
            triple = tuple(raw)
            assert len(triple) == 3 and all(m in masks for m in triple)
            assert triple not in covered
            covered.add(triple)
            A, B, C = [masks[m] for m in triple]
            actual = []
            for x in range(5):
                tips = {c for a, b, c in product(A, B, C)
                        if a != x and b != x and len({a, b, c}) == 3}
                actual.append(sum(1 << c for c in tips))
            assert actual == list(signature)
            members.append(triple)
        assert members
        flags = {a == b == c for a, b, c in members}
        assert len(flags) == 1
        groups.append((signature, members, flags.pop()))
    assert covered == set(product(masks, repeat=3))
    assert len(groups) == len({s for s, _, _ in groups}) == 110
    counts = Counter()
    for O in lists:
        for ls, lm, lh in groups:
            for rs, rm, rh in groups:
                support = {x for x in O if any(
                    a != b and ls[x] & (1 << a) and rs[x] & (1 << b)
                    for a, b in product(range(5), repeat=2))}
                counts[len(support)] += len(lm) * len(rm)
                S, T = masks[lm[0][0]], masks[rm[0][0]]
                if lh and rh:
                    assert support == O - (S & T)
                if len(O - support) >= 2:
                    assert lh and rh
                assert (len(support) == 1) == (lh and rh and len(O - (S & T)) == 1)
    assert dict(counts) == {0: 10, 1: 240, 2: 1650, 3: 9998100}
    assert {str(k): v for k, v in counts.items()} == data['support_size_counts']
    assert sum(counts.values()) == data['weighted_assignments'] == 10**7
    assert data['compressed_cases'] == 121000
    assert data['forcing_lists'] == [7] + [14] * 6 and data['forcing_support'] == 1
    # Direct 3^7 spindle enumeration independently checks the forcing example.
    edges = ((0,1),(0,2),(1,2),(1,3),(2,3),(0,4),(0,5),(4,5),(4,6),(5,6),(3,6))
    words = [w for w in product(*(masks[m] for m in data['forcing_lists']))
             if all(w[a] != w[b] for a, b in edges)]
    assert len(words) == 24 and {w[0] for w in words} == {0}
    return dict(status='VERIFIED_ROOTED_SPINDLE', triangle_triples=len(covered),
                signatures=len(groups), compressed_cases=121000,
                weighted_assignments=sum(counts.values()), support_size_counts=dict(counts),
                forcing_colorings=24, scope='Finite five-color calibration; arbitrary palette theorem uses written proof')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
