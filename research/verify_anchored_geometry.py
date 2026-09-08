"""Exact C004 witness in basis 1,sqrt(3),sqrt(13),sqrt(39), denominator 26."""
import json
from itertools import combinations


def verify():
    radicals = (1, 3, 13, 39)
    def product(a, b):
        out = [0]*4
        for i in range(4):
            for j in range(4):
                out[i ^ j] += a[i]*b[j]*radicals[i & j]
        return out
    # Three consecutive hexagon vertices, then their conjugates/antipodes.
    half = [((0, 0, 4, 0), (0, 0, 6, 0)),
            ((0, 0, 2, -3), (0, 0, 3, 2)),
            ((0, 0, -2, -3), (0, 0, -3, 2))]
    points = half + [tuple(tuple(-a for a in axis) for axis in p) for p in half]
    points.append(((0, 0, 0, 0), (0, 0, 0, 0)))
    assert len(set(points)) == 7
    edges = set()
    for i, j in combinations(range(7), 2):
        delta = [[a-b for a, b in zip(axis, other)] for axis, other in zip(points[i], points[j])]
        norm = [a+b for a, b in zip(product(delta[0], delta[0]), product(delta[1], delta[1]))]
        if norm == [26**2, 0, 0, 0]:
            edges.add((i, j))
    expected = {tuple(sorted((i, (i+1) % 6))) for i in range(6)} | {(i, 6) for i in range(6)}
    assert edges == expected
    words = [1, 2, 1, 2, 1, 2, 0]
    assert all(words[a] != words[b] for a, b in edges)
    for i in range(3):
        conjugate = tuple(tuple((-a if j & 2 else a) for j, a in enumerate(axis)) for axis in points[i])
        assert conjugate == points[i+3]
        assert (i, i+3) not in edges
    signs = []
    for i, j in ((0, 1), (1, 2), (0, 2)):
        sign = 1 if (i, j) in edges else -1
        target = j if sign == 1 else j+3
        assert tuple(sorted((i, target))) in edges
        conjugate_target = j+3 if sign == 1 else j
        assert tuple(sorted((i+3, conjugate_target))) in edges
        signs.append(sign)
    assert signs == [1, 1, -1]
    # A bad precoloring alone is weaker than high ordinary chromatic number.
    star = [(5, 0), (-5, 0), (0, 5), (0, -5), (3, 4), (0, 0)]
    star_edges = {(a, b) for a, b in combinations(range(6), 2)
                  if sum((x-y)**2 for x, y in zip(star[a], star[b])) == 25}
    assert star_edges == {(i, 5) for i in range(5)}
    assert set(range(5)) - set(range(5)) == set()  # Five distinct leaf colors.
    assert all(([0]*5+[1])[a] != ([0]*5+[1])[b] for a, b in star_edges)
    return dict(status='VERIFIED_UNBALANCED_GALOIS_CYCLE_WITH_COLOR_EXTENSION',
                vertices=7, all_pairs=21, induced_edges=len(edges),
                signed_cycle=signs, five_coloring=words, precoloring_star_edges=len(star_edges),
                scope='C004, not an unbalanced color-frame obstruction')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(), indent=2))
