"""Independent six-pair certificate verifier; no search code imports.

Coverage uses per-underlying-graph counting of distinct normalized sign words.
Geometric negatives use circle intersections, integer unit rhombi, or T035.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import gzip
import json


def rhombus_implies_collision(edges, pair):
    """Solve R^T lambda = e_a-e_b, independently of search's row-basis code."""
    assert len(pair) == 2 and pair[0] != pair[1]
    has = lambda a, b: tuple(sorted((a, b))) in edges
    constraints = set()
    for a, c in combinations(range(12), 2):
        neighbors = [b for b in range(12) if has(a, b) and has(c, b)]
        for b, d in combinations(neighbors, 2):
            row = tuple(int(i == a)+int(i == c)-int(i == b)-int(i == d) for i in range(12))
            constraints.add(row)
    columns = sorted(constraints)
    equations = [[F(col[i]) for col in columns] + [F(int(i == pair[0])-int(i == pair[1]))]
                 for i in range(12)]
    rank = 0
    for j in range(len(columns)):
        pivot = next((i for i in range(rank, 12) if equations[i][j]), None)
        if pivot is None:
            continue
        equations[rank], equations[pivot] = equations[pivot], equations[rank]
        scale = equations[rank][j]
        equations[rank] = [x/scale for x in equations[rank]]
        for i in range(rank+1, 12):
            scale = equations[i][j]
            if scale:
                equations[i] = [a-scale*b for a, b in zip(equations[i], equations[rank])]
        rank += 1
        if rank == 12:
            break
    return all(any(row[:-1]) or not row[-1] for row in equations)


def verify(root):
    data = json.loads(gzip.decompress((root/'certificates/pair_orbits_six_uniform.json.gz').read_bytes()))
    assert data['schema'] == 1 and not data['first_unresolved_codes']
    pairs = list(combinations(range(6), 2))
    forest_masks, expected = [], []
    for mask in range(32768):
        components = [{v} for v in range(6)]
        forest = 0
        edge_count = 0
        tree_count = 0
        for j, (a, b) in enumerate(pairs):
            if not mask >> j & 1:
                continue
            edge_count += 1
            left = next(block for block in components if a in block)
            right = next(block for block in components if b in block)
            if left != right:
                merged = left | right
                components = [block for block in components if block != left and block != right]+[merged]
                forest |= 1 << j
                tree_count += 1
        forest_masks.append(forest)
        expected.append(2**(edge_count-tree_count))
    assert sum(expected) == 460728
    counts = dict(total=0, k23=0, k4=0, three_coloring=0, rhombus_collapse=0, trace_obstruction=0, unresolved=0)
    seen = set()
    per_mask = [0]*32768
    for code, kind, witness in data['records']:
        assert isinstance(code, int) and 0 <= code < 3**15 and code not in seen
        seen.add(code)
        counts['total'] += 1
        assert kind in counts and kind not in ('total', 'unresolved')
        counts[kind] += 1
        digits = [(code // 3**j) % 3 for j in range(15)]
        mask = sum(1 << j for j, digit in enumerate(digits) if digit)
        assert all(digits[j] == 1 for j in range(15) if forest_masks[mask] >> j & 1)
        per_mask[mask] += 1
        edges = set()
        for (a, b), digit in zip(pairs, digits):
            if digit == 1:
                edges.update(((2*a, 2*b), (2*a+1, 2*b+1)))
            elif digit == 2:
                edges.update(((2*a, 2*b+1), (2*a+1, 2*b)))
        has = lambda a, b: tuple(sorted((a, b))) in edges
        assert all(has(a ^ 1, b ^ 1) for a, b in edges)
        if kind == 'three_coloring':
            assert isinstance(witness, str) and len(witness) == 12
            word = list(map(int, witness))
            assert all(0 <= c <= 2 for c in word)
            assert all(word[a] != word[b] for a, b in edges)
            continue
        assert all(isinstance(v, int) and 0 <= v < 12 for v in witness)
        if kind == 'k23':
            assert len(witness) == len(set(witness)) == 5
            assert all(has(a, b) for a in witness[:2] for b in witness[2:])
        elif kind == 'k4':
            assert len(witness) == len(set(witness)) == 4
            assert all(has(a, b) for a, b in combinations(witness, 2))
        elif kind == 'rhombus_collapse':
            assert rhombus_implies_collision(edges, witness)
        else:
            assert len(witness) == 6
            a, b, c, d, r, s = witness
            assert len({a, b, c, d}) == 4 and len({a, b ^ 1, r, s}) == 4
            assert has(a, b) and all(has(u, v) for u in (a, b) for v in (c, d))
            assert has(c, d ^ 1)
            assert has(r, s) and all(has(u, v) for u in (a, b ^ 1) for v in (r, s))
    assert per_mask == expected
    assert counts == data['counts'] == dict(total=460728, k23=210849, k4=5130,
                                           three_coloring=240003, rhombus_collapse=4656,
                                           trace_obstruction=90, unresolved=0)
    return dict(status='VERIFIED_SIX_ORBIT_COMMON_THREE_LIST_CLASSIFICATION',
                counts=counts, raw_signed_graphs_covered=3**15,
                geometry_requires='Real involution fixing sqrt(3); T035 trace obstruction',
                scope='Not arbitrary nonuniform lists, not historical six-orbit full-extension certification')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
