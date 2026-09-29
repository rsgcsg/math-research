"""T149: exact geometric/parity calibration; the general claim has a proof."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json

from verify_parts_core import verify_geometry


def require(ok, message):
    if not ok:
        raise ValueError(message)


def connected(n, edges):
    neighbors = [set() for _ in range(n)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    seen = {0}
    stack = [0]
    while stack:
        for v in neighbors[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == n


def partition(word):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in word)


def verify():
    root = Path(__file__).resolve().parents[1]
    core, core_edges = verify_geometry(root / 'certificates/parts509_core.json')
    require(connected(509, core_edges), 'Parts core is not connected')
    require(set(core['five_coloring']) == set(range(5)), 'core palette not full')
    cases = []
    # This integer core is a path, not a substitute for the Parts lower bound.
    core_points = [(-j, 0) for j in range(5)]
    core_colors = [2, 3, 4, 0, 1]
    for n in range(2, 9):
        points = core_points + [(t, 0) for t in range(1, 3*n+1)]
        points += [(3*j, 1) for j in range(1, n+1)]
        actual = [(a, b) for a, b in combinations(range(len(points)), 2)
                  if sum((x-y)**2 for x, y in zip(points[a], points[b])) == 1]
        expected = {(j, j+1) for j in range(4)} | {(0, 5)}
        expected |= {(t+3, t+4) for t in range(2, 3*n+1)}
        expected |= {(3*j+4, 5+3*n+j-1) for j in range(1, n+1)}
        require(set(actual) == expected, 'additional or missing actual unit edge')
        require(connected(len(points), actual), 'calibration graph disconnected')
        fixed = core_colors + [2+t % 3 for t in range(1, 3*n+1)]
        words = list(product((0, 1), repeat=n))
        laws = [[], []]
        for bits in words:
            word = fixed + list(bits)
            require(all(word[a] != word[b] for a, b in actual), 'improper word')
            laws[sum(bits) % 2].append(bits)
        full = [{partition(core_colors + list(bits)) for bits in law} for law in laws]
        require(not (full[0] & full[1]) and all(len(x) == 2**(n-1) for x in full),
                'parity laws coincide after forgetting names')
        checked = 0
        for size in range(n):
            for subset in combinations(range(n), size):
                # Adding all fixed palette anchors is a stronger test than
                # forgetting some fixed vertices in a physical-point marginal.
                marginals = [Counter(partition(core_colors + [bits[j] for j in subset])
                                     for bits in law) for law in laws]
                require(marginals[0] == marginals[1], 'proper marginal differs')
                checked += 1
        cases.append(dict(n=n, points=len(points), actual_edges=len(actual),
                          partitions_per_law=2**(n-1), proper_leaf_subsets=checked))
    return dict(status='PASS', parts_connected=True, parts_actual_edges=len(core_edges),
                calibration_cases=cases,
                scope='Connected geometric parity-law identification ceiling; no colorability or HN obstruction.')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    print(json.dumps(verify(), sort_keys=True))
