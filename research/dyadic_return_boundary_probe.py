"""Exact small boundary / power-return probe, with no SAT and no full-Y claim.

Rebuilds the Y coordinates and their archived digest.  Only the 1,378 boundary
pairs are tested for distance one: this is deliberately NOT another full-Y
edge verifier.  Saved words are source-bound inputs for distribution probes;
their full properness remains the obligation of their existing verifiers.
"""

from collections import Counter, deque
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json
import math

from verify_quintic_residue5_ring import verify as ring
from verify_quintic_core_probe import digest, product_twice, conjugate_twice
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping


def partition(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def boundary_assignment(source, image, mapping, edges, k=5):
    """Exact two-partition boundary compatibility, NOT interior extension."""
    left = {x: source[i] for i, (x, _) in enumerate(mapping)}
    right = {y: image[i] for i, (_, y) in enumerate(mapping)}
    if any(left[x] == left[y] for x, y in edges if x in left and y in left):
        return None
    if any(right[x] == right[y] for x, y in edges if x in right and y in right):
        return None
    for perm in permutations(range(k)):
        if any(left[x] != perm[right[x]] for x in left.keys() & right.keys()):
            continue
        word = dict(left)
        word.update((x, perm[b]) for x, b in right.items())
        if all(word[x] != word[y] for x, y in edges):
            return word
    return None


def law_probe(words, mapping):
    source, image = [x for x, _ in mapping], [y for _, y in mapping]
    left = Counter(partition(w, source) for w in words)
    right = Counter(partition(w, image) for w in words)
    mismatch = None
    for i, (x, y) in enumerate(mapping):
        for z, t in mapping[i + 1:]:
            counts = [sum(w[x] == w[z] for w in words),
                      sum(w[y] == w[t] for w in words)]
            if counts[0] != counts[1]:
                mismatch = dict(pairs=[[x, y], [z, t]], same_counts=counts)
                break
        if mismatch:
            break
    return dict(words=len(words), full_joint_equal=left == right,
                distinct_source=len(left), distinct_image=len(right),
                source_image_intersection=len(left.keys() & right.keys()),
                first_pair_mismatch=mismatch)


def probe(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    pricing_raw = (root / 'certificates/dyadic_joint_column_pricing.json').read_bytes()
    pricing = json.loads(pricing_raw)
    _, field = ring(root, geometry_context=True)
    points = sorted(set(field['points']) |
                    {field['mul'](field['tau'], p) for p in field['points']})
    context = dict(points=points, ring=field)
    den = math.lcm(*(a.denominator for p in points for a in p))
    integral = [tuple(int(a * den) for a in p) for p in points]
    assert len(points) == 10077
    assert digest(integral) == pricing['geometry']['point_sha256']
    definition = _new_definitions(context)[0]
    mapping = _mapping(context, definition)
    assert mapping == [tuple(p) for p in pricing['mapping']]
    assert digest(mapping) == pricing['mapping_sha256']
    u = definition[1]
    square = field['mul'](u, u)
    expected_square = tuple({0: Q(7, 16), 4: -Q(3, 16),
                             9: Q(7, 16), 13: Q(1, 16)}.get(i, Q(0))
                            for i in range(32))
    assert square == expected_square
    left, right = set(dict(mapping)), set(dict(mapping).values())
    boundary = sorted(left | right)
    edges = []
    for x, y in combinations(boundary, 2):
        diff = [a - b for a, b in zip(integral[x], integral[y])]
        if product_twice(diff, conjugate_twice(diff), field['table']) == [4 * den * den] + [0] * 31:
            edges.append((x, y))
    assert len(boundary) == 53 and len(edges) == 20
    overlap = sorted(left & right)
    assert overlap == [2321, 3451, 4641, 5557, 9425]
    adjacency = {x: set() for x in boundary}
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    seen, components = set(), []
    for start in boundary:
        if start in seen:
            continue
        seen.add(start)
        component, queue = [], deque([start])
        while queue:
            x = queue.popleft()
            component.append(x)
            for y in adjacency[x] - seen:
                seen.add(y)
                queue.append(y)
        components.append(sorted(component))
    assert Counter(map(len, components)) == {1: 17, 2: 12, 3: 4}
    # Identify every one-step u pair, retaining all actual boundary edges.
    parents = {x: x for x in boundary}
    def find(x):
        while parents[x] != x:
            x = parents[x]
        return x
    for x, y in mapping:
        parents[find(y)] = find(x)
    qedges = sorted({tuple(sorted((find(x), find(y)))) for x, y in edges})
    qadj = {find(x): set() for x in boundary}
    for x, y in qedges:
        assert x != y
        qadj[x].add(y)
        qadj[y].add(x)
    colors = {}
    for start in sorted(qadj):
        if start in colors:
            continue
        colors[start] = 0
        queue = deque([start])
        while queue:
            x = queue.popleft()
            for y in sorted(qadj[x]):
                if y not in colors:
                    colors[y] = 1 - colors[x]
                    queue.append(y)
                assert colors[y] != colors[x]
    boundary_word = {x: colors[find(x)] for x in boundary}
    assert len(qadj) == 25 and len(qedges) == 16
    assert all(boundary_word[x] != boundary_word[y] for x, y in edges)
    assert all(boundary_word[x] == boundary_word[y] for x, y in mapping)
    groups, words, sources = {}, [], []
    for source in pricing['source_files']:
        raw = (root / 'certificates' / source['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['sha256']
        result = json.loads(raw)['result']
        current = result['words'] if 'words' in result else [result['five_coloring']]
        assert len(current) == source['count']
        groups[source['file']] = current
        words.extend(current)
        sources.append(source)
    words.append(pricing['result']['word'])
    assert len(words) == 12
    groups['all_twelve_saved_words_uniform'] = words
    all_states = sorted({partition(w, [x for x, _ in mapping]) for w in words} |
                        {partition(w, [y for _, y in mapping]) for w in words})
    allowed = [(i, j) for i, a in enumerate(all_states) for j, b in enumerate(all_states)
               if boundary_assignment(a, b, mapping, edges) is not None]
    outgoing = {i: [j for a, j in allowed if a == i] for i in range(len(all_states))}
    heights, active = {}, set()
    def height(i):
        if i not in heights:
            assert i not in active, 'Boundary pattern graph contains a cycle'
            active.add(i)
            heights[i] = max([1 + height(j) for j in outgoing[i]] + [0])
            active.remove(i)
        return heights[i]
    potential = [height(i) for i in range(len(all_states))]
    assert len(all_states) == 22 and len(allowed) == 31
    assert potential == [0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 1, 0, 3, 1, 1, 1, 3, 1, 1, 4, 1, 1]
    assert all(potential[i] > potential[j] for i, j in allowed)
    powers, coefficient, chained = [], u, dict(mapping)
    expected = [(29, 29), (805, 5), (5, 1), (1, 1)]
    for n in range(1, 5):
        current = _mapping(context, (f'u^{n}', coefficient, definition[2], False))
        if n > 1:
            step = dict(mapping)
            chained = {x: step[y] for x, y in chained.items() if y in step}
        skips = [(x, y) for x, y in current if x not in chained]
        assert (len(current), len(chained)) == expected[n - 1]
        powers.append(dict(power=n, complete_domain=len(current),
                           common_one_step_domain=len(chained), skipped_returns=len(skips),
                           first_skipped_returns=skips[:5], mapping_sha256=digest(current),
                           non_F_sources=sum(any(points[x][16:]) for x, _ in current),
                           laws={name: law_probe(ws, current) for name, ws in groups.items()}))
        coefficient = field['mul'](u, coefficient)
    # Exact rational unit-star calibration: boundary properness alone is not
    # extension to its one uncolored center, even for a bipartite host.
    leaves = [(Q(1 - t * t, 1 + t * t), Q(2 * t, 1 + t * t)) for t in range(5)]
    assert all(x * x + y * y == 1 for x, y in leaves)
    assert all((x - a) ** 2 + (y - b) ** 2 != 1
               for (x, y), (a, b) in combinations(leaves, 2))
    return dict(status='PASS_BOUNDARY_AND_RETURN_PROBE', point_sha256=digest(integral),
                pricing_sha256=hashlib.sha256(pricing_raw).hexdigest(), sources=sources,
                boundary=dict(vertices=53, actual_pairs=1378, edges=edges,
                              overlap=overlap, components=components,
                              quotient_vertices=25, quotient_edges=qedges,
                              identity_u_proper_two_coloring=boundary_word,
                              saved_pattern_states=len(all_states),
                              states=all_states, state_sha256=digest(all_states),
                              boundary_compatible_pairs=len(allowed),
                              allowed_pattern_arcs=allowed,
                              strict_pattern_potential=potential,
                              boundary_compatible_self_loops=[i for i, j in allowed if i == j]),
                powers=powers, star_calibration=dict(vertices=6, induced_graph='K_1,5',
                                                     leaves=[[str(x), str(y)] for x, y in leaves]),
                scope='Exact coordinate and boundary/power-return checks only; no new full-Y coloring, joint law, negative all-word certificate, or HN bound.')


def verify(root):
    """Recompute independently and compare every field of the frozen report."""
    root = Path(root)
    actual = probe(root)
    expected = json.loads((root / 'certificates/dyadic_return_boundary_probe.json').read_text())
    assert json.loads(json.dumps(actual)) == expected
    return actual


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
