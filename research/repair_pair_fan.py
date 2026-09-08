"""Exact diagnostic: compatible gate poses through a fixed nonunit port pair.

Coordinates are multiplied by the common squared anchor distance, avoiding
field division. This is a search-side diagnostic, not an independent certificate.
"""
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict, Counter
from pathlib import Path
import json
from exact_geometry import add, sub, mul, distance_squared, ONE


def run():
    root = Path(__file__).resolve().parents[1]
    base = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    points = [tuple(tuple(map(F, axis)) for axis in p) for p in base['points']]
    groups = defaultdict(list)
    for a, b in combinations(range(7, 21), 2):
        d = distance_squared(points[a], points[b])
        if d != ONE:
            groups[d].append((a, b))
    results = []
    # Start with exceptional distances; normal distances can be diagnosed later.
    for distance, group in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:2]:
        x, y = (points[i] for i in group[0])
        target_vector = tuple(sub(y[k], x[k]) for k in range(2))
        poses, labels = [], []
        for a, b in group:
            for a, b in ((a, b), (b, a)):
                u = tuple(sub(points[b][k], points[a][k]) for k in range(2))
                for sign in (1, -1):
                    q = []
                    for p in points:
                        v = tuple(sub(p[k], points[a][k]) for k in range(2))
                        dot = add(mul(u[0], v[0]), mul(u[1], v[1]))
                        area = tuple(sign*z for z in sub(mul(u[0], v[1]), mul(u[1], v[0])))
                        q.append((add(mul(distance, x[0]), sub(mul(dot, target_vector[0]), mul(area, target_vector[1]))),
                                  add(mul(distance, x[1]), add(mul(dot, target_vector[1]), mul(area, target_vector[0])))))
                    poses.append(q)
                    labels.append([a, b, sign])
        threshold = mul(distance, distance)
        compatible, reasons, forbidden = set(), Counter(), []
        for i, j in combinations(range(len(poses)), 2):
            left, right = poses[i], poses[j]
            if set(left[:7]) & set(right) or set(right[:7]) & set(left):
                reasons['interior_collision'] += 1
                continue
            expected = {frozenset((p[a], p[b])) for p in (left, right) for a, b in base['induced_edges']}
            bad = next(((k, l) for k, a in enumerate(left) for l, b in enumerate(right)
                      if (k < 7 or l < 7) and distance_squared(a, b) == threshold
                      and frozenset((a, b)) not in expected), None)
            if bad is not None:
                reasons['extra_cross_interior_edge'] += 1
                forbidden.append([i, j, bad[0], bad[1]])
            else:
                compatible.add((i, j))
        maximum, witness = 0, []
        for mask in range(1 << len(poses)):
            if bin(mask).count('1') <= maximum:
                continue
            chosen = [i for i in range(len(poses)) if mask >> i & 1]
            if all(pair in compatible for pair in combinations(chosen, 2)):
                maximum, witness = len(chosen), chosen
        result = dict(anchor_pair=group[0], distance_multiplicity=len(group), poses=len(poses),
                      compatible_pairs=len(compatible), maximum_compatible_fan=maximum,
                      witness=witness, excluded=dict(reasons), scope='Diagnostic, no independent replay yet')
        results.append(result)
        result['certificate'] = dict(
            squared_anchor_distance=list(map(str, distance)), labels=labels,
            scaled_poses=[[[list(map(str, axis)) for axis in p] for p in q] for q in poses],
            forbidden_pair_witnesses=forbidden)
        print(json.dumps({k: v for k, v in result.items() if k != 'certificate'}), flush=True)
    return results


if __name__ == '__main__':
    data = run()
    (Path(__file__).resolve().parents[1]/'certificates/repair_pair_fan.json').write_text(
        json.dumps(dict(schema=1, cases=data), indent=2)+'\n')
