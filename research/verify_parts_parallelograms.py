"""Independent full four-port check for equal-midpoint Parts509 quadruples.

The search groups diagonals by midpoint. Here equal *directed displacements*
generate opposite sides, and every quadruple must occur exactly twice.
Only verified full colorings, not SAT statuses or request lists, are used.
"""
import gzip
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
from verify_parts_core import canonical, verify_coloring, verify_geometry


def verify(root, geometry=None):
    core, edges = geometry or verify_geometry(root/'certificates/parts509_core.json')
    points = [tuple(x for axis in p for x in axis) for p in core['points']]
    segments = defaultdict(list)
    for a, b in combinations(range(509), 2):
        delta = tuple(y-x for x, y in zip(points[a], points[b]))
        if next(x for x in delta if x) < 0:
            delta = tuple(-x for x in delta)
            a, b = b, a
        segments[delta].append((a, b))
    multiplicity = Counter()
    for parallel in segments.values():
        for (a, b), (c, d) in combinations(parallel, 2):
            if len({a, b, c, d}) == 4:
                multiplicity[tuple(sorted((a, b, c, d)))] += 1
    assert set(multiplicity.values()) == {2}
    data = json.loads(gzip.decompress((root/'certificates/parts509_parallelograms.json.gz').read_bytes()))
    words = data['models']
    assert words and len(words) == len(set(words))
    masks = [[0]*5 for _ in range(509)]
    for i, word in enumerate(words):
        colors = list(map(int, word))
        verify_coloring(colors, edges)
        for v, color in enumerate(colors):
            masks[v][color] |= 1 << i
    equality = {}
    for a, b in combinations(range(509), 2):
        equality[a, b] = sum(masks[a][c] & masks[b][c] for c in range(5))
    patterns = sorted({canonical(word) for word in product(range(4), repeat=4)})
    assert len(patterns) == 15
    pair_positions = list(combinations(range(4), 2))
    requirements = [(p, [p[i] == p[j] for i, j in pair_positions]) for p in patterns]
    edge_set = set(edges)
    universe = (1 << len(words))-1
    counts = Counter()
    for ports in sorted(multiplicity):
        pairs = list(combinations(ports, 2))
        unit = [pair in edge_set for pair in pairs]
        eq = [equality[pair] for pair in pairs]
        for pattern, same in requirements:
            if any(u and s for u, s in zip(unit, same)):
                continue
            hits = universe
            for mask, required in zip(eq, same):
                hits &= mask if required else universe ^ mask
            assert hits, (ports, pattern)
            counts[max(pattern)+1] += 1
    assert len(multiplicity) == data['family_size'] == 794256
    assert dict(counts) == {int(k): v for k, v in data['patterns_by_blocks'].items()}
    return dict(status='VERIFIED_ALL_EQUAL_MIDPOINT_FOUR_PORT_PRECOLORINGS_EXTEND',
                quadruples=len(multiplicity), patterns_by_blocks=dict(counts),
                total_proper_partitions=sum(counts.values()), full_colorings=len(words),
                includes_collinear_quadruples=True,
                scope='Parts509 equal-midpoint quadruples only; not arbitrary four ports')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
