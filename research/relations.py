"""Tiny exact color-partition engine. No numerical geometry or SAT dependency."""
from itertools import combinations


def canonical(word):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in word)


def color_partitions(n, edges, k):
    """All proper colorings modulo global S_k, each once as a restricted word."""
    earlier = [[] for _ in range(n)]
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n and a != b
        a, b = sorted((a, b))
        earlier[b].append(a)
    word = []
    def visit(v, maximum):
        if v == n:
            yield tuple(word)
            return
        for c in range(min(k - 1, maximum + 1) + 1):
            if all(word[u] != c for u in earlier[v]):
                word.append(c)
                yield from visit(v + 1, max(c, maximum))
                word.pop()
    yield from visit(0, -1)


def boundary_relation(n, edges, ports, k):
    return sorted({canonical([c[i] for i in ports]) for c in color_partitions(n, edges, k)})


def lattice_edges(points):
    """All induced unit edges using the exact Eisenstein quadratic form."""
    result = []
    for i, j in combinations(range(len(points)), 2):
        a = points[i][0] - points[j][0]
        b = points[i][1] - points[j][1]
        if a*a + a*b + b*b == 1:
            result.append((i, j))
    return result


def calibrate():
    triangle = [(0, 1), (1, 2), (0, 2)]
    assert boundary_relation(3, triangle, (0, 1, 2), 5) == [(0, 1, 2)]
    # Two diamonds share vertex 0; tips 3 and 6 are joined.
    spindle = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3),
               (0, 4), (0, 5), (4, 5), (4, 6), (5, 6), (3, 6)]
    assert not list(color_partitions(7, spindle, 3))
    c4 = list(color_partitions(7, spindle, 4))
    assert c4
    # An abstract copier only: K3 joined to two disjoint K2 ports.
    copier = triangle + [(3, 4), (5, 6)] + [(a, b) for a in range(3) for b in range(3, 7)]
    colorings = list(color_partitions(7, copier, 5))
    assert colorings and all(set(c[3:5]) == set(c[5:7]) for c in colorings)
    return dict(spindle_edges=spindle, spindle_4_colorings=len(c4),
                spindle_4_witness=c4[0], abstract_copier_partitions=len(colorings),
                abstract_copier_boundary=boundary_relation(7, copier, (3, 4, 5, 6), 5))
