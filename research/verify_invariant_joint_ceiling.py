"""Exact finite calibration of T082; infinite scope is the compactness proof.

No producer or optimizer. Average the known finite-field coloring over its
entire isometry group, then check all partial congruences of a five-point cross.
"""
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path
import json


def partition(word):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in word)


def verify(root):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    data = json.loads((root/'certificates/residue11_coloring.json').read_text())
    base = tuple(map(int, ''.join(data['rows'])))
    assert len(base) == 121 and set(base) == set(range(5))
    points = list(product(range(11), repeat=2))
    def distance(a, b):
        return sum((x-y)**2 for x, y in zip(a, b)) % 11
    edges = [(i, j) for i, j in combinations(range(121), 2) if distance(points[i], points[j]) == 1]
    assert len(edges) == 726
    matrices = [(a, -sign*b % 11, b, sign*a % 11)
                for a, b in points if (a*a+b*b) % 11 == 1 for sign in (-1, 1)]
    assert len(set(matrices)) == 24
    for a, b, c, d in matrices:
        assert (a*a+c*c) % 11 == (b*b+d*d) % 11 == 1 and (a*b+c*d) % 11 == 0
    samples = []
    for a, b, c, d in matrices:
        for u, v in points:
            image = [11*((a*x+b*y+u) % 11)+(c*x+d*y+v) % 11 for x, y in points]
            assert len(set(image)) == 121
            word = tuple(base[i] for i in image)
            assert all(word[i] != word[j] for i, j in edges)
            samples.append(word)
    assert len(samples) == 2904
    cross = [(0, 0), (1, 0), (0, 1), (10, 0), (0, 10)]
    indices = [11*x+y for x, y in cross]
    words = [tuple(word[i] for i in indices) for word in samples]
    subsets = [s for n in range(6) for s in combinations(range(5), n)]
    law = {s: Counter(partition(tuple(word[i] for i in s)) for word in words) for s in subsets}
    congruences = 0
    for domain in subsets:
        for image in permutations(range(5), len(domain)):
            if any(distance(cross[domain[i]], cross[domain[j]]) !=
                   distance(cross[image[i]], cross[image[j]])
                   for i, j in combinations(range(len(domain)), 2)):
                continue
            image_law = Counter(partition(tuple(word[i] for i in image)) for word in words)
            assert law[domain] == image_law
            congruences += 1
    # True marginal consistency, retaining entire color partitions.
    restrictions = 0
    for domain in subsets:
        for size in range(len(domain)+1):
            for selected in combinations(range(len(domain)), size):
                target = tuple(domain[i] for i in selected)
                projected = Counter()
                for word, count in law[domain].items():
                    projected[partition(tuple(word[i] for i in selected))] += count
                assert projected == law[target]
                restrictions += 1
    return dict(status='PASS', theorem='T082', finite_field_order=11,
                group_words=len(samples), proper_edge_checks=len(samples)*len(edges),
                cross_points=5, full_partition_support=len(law[tuple(range(5))]),
                partial_congruences=congruences, marginal_checks=restrictions,
                scope='finite calibration; full safe-field theorem uses written compactness proof')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
