"""Independent positive-model checker, no SAT imports or generator imports.

Uses the quadratic distance form on all patch pairs; verifies periodic torus
models as formulas on Z^2. Negative search statuses are never certified here.
"""
from collections import Counter
from itertools import combinations


def verify(data):
    ds = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
    positive, negative_search_only, edge_checks = 0, 0, 0
    for record in data['torus']:
        if record['status'] != 'SAT':
            negative_search_only += 1
            continue
        w, h, rows = record['width'], record['height'], record['rows']
        assert len(rows) == h and all(len(row) == w for row in rows)
        assert all(type(c) is int and 0 <= c < 6 for row in rows for c in row)
        def color(x, y):
            return rows[y % h][x % w]
        for y in range(h):
            for x in range(w):
                c = color(x, y)
                ns = [color(x+a, y+b) for a, b in ds]
                counts = Counter(ns)
                assert set(counts) == set(range(6)) - {c}
                assert sorted(counts.values()) == [1, 1, 1, 1, 2]
                repeated = next(k for k, n in counts.items() if n == 2)
                if record['opposite_only']:
                    i, j = [i for i, k in enumerate(ns) if k == repeated]
                    assert abs(i-j) == 3
                if record['triangle_partners']:
                    assert c//3 == repeated//3
                edge_checks += 6
        positive += 1
    for record in data['patches']:
        if record['status'] != 'SAT':
            negative_search_only += 1
            continue
        r = record['radius']
        colors = {(x, y): c for x, y, c in record['coloring']}
        expected = {(x, y) for x in range(-r-1, r+2) for y in range(-r-1, r+2)
                    if max(abs(x), abs(y), abs(x+y)) <= r+1}
        assert set(colors) == expected
        assert len(colors) == len(record['coloring'])
        assert all(type(c) is int and 0 <= c < 6 for c in colors.values())
        for a, b in combinations(colors, 2):
            dx, dy = a[0]-b[0], a[1]-b[1]
            if dx*dx+dx*dy+dy*dy == 1:
                assert colors[a] != colors[b]
                edge_checks += 1
        for x, y in colors:
            if max(abs(x), abs(y), abs(x+y)) > r:
                continue
            counts = Counter(colors[x+a, y+b] for a, b in ds)
            c = colors[x, y]
            assert set(counts) == set(range(6)) - {c}
            assert sorted(counts.values()) == [1, 1, 1, 1, 2]
            repeated = next(k for k, n in counts.items() if n == 2)
            assert c//3 == repeated//3
        positive += 1
    return dict(positive_models_checked=positive,
                negative_statuses_not_certified=negative_search_only, edge_checks=edge_checks)
