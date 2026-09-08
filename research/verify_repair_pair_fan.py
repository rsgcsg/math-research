"""Independent all-pose coverage and disjoint forbidden-pair certificate.

Uses the independent verifier's field arithmetic, not the fan search module.
No maximum-clique answer from the search is trusted or needed for the upper bound.
"""
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
from fractions import Fraction as F
import json
from verify_repair_cascade import read_points, distance, determinant, times, minus, ONE


def verify(root):
    base_data = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    base = read_points(base_data)
    data = json.loads((root/'certificates/repair_pair_fan.json').read_text())
    assert data['schema'] == 1 and len(data['cases']) == 2
    groups = defaultdict(list)
    for a, b in combinations(range(7, 21), 2):
        value = distance(base[a], base[b])
        if value != ONE:
            groups[value].append((a, b))
    exceptional = {d: g for d, g in groups.items() if len(g) > 1}
    assert sorted(map(len, exceptional.values())) == [2, 4]
    seen, counts = set(), []
    for case in data['cases']:
        cert = case['certificate']
        d = tuple(map(F, cert['squared_anchor_distance']))
        assert d in exceptional and d not in seen
        seen.add(d)
        group = exceptional[d]
        labels = cert['labels']
        assert set(map(tuple, labels)) == {(a, b, sign) for u, v in group
                                         for a, b in ((u, v), (v, u)) for sign in (1, -1)}
        assert len(labels) == 4*len(group)
        poses = [read_points(dict(points=q)) for q in cert['scaled_poses']]
        assert len(poses) == len(labels)
        assert len({tuple(q) for q in poses}) == len(poses)
        x, y = case['anchor_pair']
        assert (x, y) in group
        target_x = tuple(times(d, axis) for axis in base[x])
        target_y = tuple(times(d, axis) for axis in base[y])
        scale_squared = times(d, d)
        for q, (a, b, sign) in zip(poses, labels):
            assert len(q) == 21 and q[a] == target_x and q[b] == target_y
            for i, j in combinations(range(21), 2):
                assert distance(q[i], q[j]) == times(scale_squared, distance(base[i], base[j]))
            k = next(k for k in range(21) if determinant(base[a], base[b], base[k]) != (0,)*4)
            expected_area = times(scale_squared, determinant(base[a], base[b], base[k]))
            assert determinant(q[a], q[b], q[k]) == tuple(sign*v for v in expected_area)
        # Every pose occurs in exactly one forbidden pair. Thus at most half
        # can coexist, regardless of additional incompatibilities.
        covered = Counter()
        for i, j, a, b in cert['forbidden_pair_witnesses']:
            assert 0 <= i < j < len(poses) and 0 <= a < 21 and 0 <= b < 21
            assert a < 7 or b < 7
            # Structural explanation: the two source anchor pairs differ by
            # the same unit translation, hence the aligned gate origins do too.
            s, t, sign = labels[i]
            u, v, other_sign = labels[j]
            assert sign == other_sign
            assert tuple(minus(base[u][k], base[s][k]) for k in range(2)) == tuple(
                minus(base[v][k], base[t][k]) for k in range(2))
            assert distance(base[u], base[s]) == ONE
            assert a == b == 0
            left, right = poses[i], poses[j]
            assert distance(left[a], right[b]) == scale_squared
            expected_edges = {frozenset((p[u], p[v])) for p in (left, right)
                              for u, v in base_data['induced_edges']}
            assert frozenset((left[a], right[b])) not in expected_edges
            # No vertex-identification ambiguity in the cross-interior witness.
            assert not set(left[:7]).intersection(right)
            assert not set(right[:7]).intersection(left)
            covered[i] += 1
            covered[j] += 1
        assert covered == Counter({i: 1 for i in range(len(poses))})
        counts.append(dict(poses=len(poses), forbidden_matching=len(poses)//2,
                           compatible_upper_bound=len(poses)//2))
    assert seen == set(exceptional)
    assert all(len(group) == 1 for d, group in groups.items() if d not in seen)
    return dict(status='VERIFIED_GEOMETRIC_PAIR_REUSE_AT_MOST_EIGHT', cases=counts,
                ordinary_distance_pose_bound=4, pair_reuse_bound=8,
                scope='Specified template; no extra cross-interior unit edges; not a chromatic bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
