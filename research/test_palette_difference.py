"""Elementary palette-group calibration, not an HN obstruction."""
from itertools import combinations, permutations
import json


def check():
    # F_2^2 is encoded by two bits; its additive operation is XOR.
    affine4 = set()
    for a in (1, 2, 3):
        for b in (1, 2, 3):
            if a == b:
                continue
            for shift in range(4):
                affine4.add(tuple(shift ^ (a if x & 1 else 0)
                                  ^ (b if x & 2 else 0) for x in range(4)))
    if affine4 != set(permutations(range(4))):
        raise ValueError('AGL(2,2) != S4')
    for q in affine4:
        for d in range(1, 4):
            if len({q[x] ^ q[x ^ d] for x in range(4)}) != 1:
                raise ValueError('four-color difference changed')
    affine5 = {tuple((a*x+b) % 5 for x in range(5))
               for a in range(1, 5) for b in range(5)}
    preserving = {q for q in permutations(range(5))
                  if all(len({(q[(x+d) % 5]-q[x]) % 5
                              for x in range(5)}) == 1 for d in range(5))}
    if preserving != affine5 or len(preserving) != 20:
        raise ValueError('five-color affine classification')
    points = [(0, 0), (1, 0), (0, 3), (1, 3), (4, 4)]
    distances = [(i, j, sum((x-y)**2 for x, y in zip(points[i], points[j])))
                 for i, j in combinations(range(5), 2)]
    edges = [(i, j) for i, j, d in distances if d == 1]
    if edges != [(0, 1), (2, 3)]:
        raise ValueError('actual unit pairs')
    q = (2, 1, 0, 3, 4)
    before = [(j-i) % 5 for i, j in edges]
    after = [(q[j]-q[i]) % 5 for i, j in edges]
    if before != [1, 1] or after != [4, 3]:
        raise ValueError('renaming counterexample')
    if len({min(x, 5-x) for x in after}) != 2:
        raise ValueError('unoriented counterexample')
    return dict(status='PASS', four_color_renamings=24, five_color_renamings=120,
                five_color_difference_preservers=20, squared_distances=[d for _, _, d in distances],
                actual_unit_edges=edges, hn_bound_changed=False)


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
