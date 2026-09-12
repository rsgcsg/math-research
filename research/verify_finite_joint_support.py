"""Exact finite full-joint support calibrations, independent of SAT.

Both configurations use rational coordinates in the triangular basis with
norm a*a + a*b + b*b.  All actual pairs and all k**n color words are inspected.
The normalized partition action is a single cycle of length 2 or 3.  Exact
linear algebra proves its sole invariant probability vector is uniform, so an
equal-weight word-index representation exists exactly at multiples of 2 or 3.
These are low-chromatic examples, not HN obstructions or a Q009 decision.
"""

from fractions import Fraction as Q
from itertools import combinations, permutations, product
import json


def _norm(p):
    a, b = p
    return a * a + a * b + b * b


def _difference(p, q):
    return tuple(x - y for x, y in zip(p, q))


def _pattern(word):
    labels = {}
    return tuple(labels.setdefault(color, len(labels)) for color in word)


def _rref(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    assert rows and all(len(row) == len(rows[0]) for row in rows)
    pivots = []
    target = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(target, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[target], rows[pivot] = rows[pivot], rows[target]
        scale = rows[target][col]
        rows[target] = [value / scale for value in rows[target]]
        for i, row in enumerate(rows):
            if i != target and row[col]:
                scale = row[col]
                rows[i] = [a - scale * b for a, b in zip(row, rows[target])]
        pivots.append(col)
        target += 1
        if target == len(rows):
            break
    return rows, pivots


def _determinant(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    assert rows and all(len(row) == len(rows) for row in rows)
    determinant = Q(1)
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col]), None)
        if pivot is None:
            return Q(0)
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            determinant = -determinant
        scale = rows[col][col]
        determinant *= scale
        for i in range(col + 1, len(rows)):
            factor = rows[i][col] / scale
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[col])]
    return determinant


def _calibration(name, points, colors, motion, expected_edges,
                 expected_partitions, expected_mapping):
    points = [tuple(Q(value) for value in p) for p in points]
    lookup = {p: i for i, p in enumerate(points)}
    assert len(lookup) == len(points)
    mapped = [motion(p) for p in points]
    assert all(p in lookup for p in mapped)
    mapping = [lookup[p] for p in mapped]
    assert mapping == expected_mapping
    assert sorted(mapping) == list(range(len(points)))

    distances = {}
    edges = []
    for i, j in combinations(range(len(points)), 2):
        distance = _norm(_difference(points[i], points[j]))
        assert distance > 0
        assert distance == _norm(_difference(mapped[i], mapped[j]))
        distances[(i, j)] = distance
        if distance == 1:
            edges.append((i, j))
    assert edges == expected_edges

    all_words = list(product(range(colors), repeat=len(points)))
    proper_words = [word for word in all_words
                    if all(word[i] != word[j] for i, j in edges)]
    partitions = sorted({_pattern(word) for word in proper_words})
    assert partitions == expected_partitions
    assert len(partitions) == colors
    action = [partitions.index(_pattern(tuple(word[i] for i in mapping)))
              for word in partitions]
    assert sorted(action) == list(range(len(partitions)))
    orbit, current = [], 0
    while current not in orbit:
        orbit.append(current)
        current = action[current]
    assert current == 0 and len(orbit) == len(partitions)
    assert all(action[i] != i for i in range(len(partitions)))

    # D is the exact full-domain source-pattern minus image-pattern matrix.
    size = len(partitions)
    D = [[int(row == col) - int(row == action[col]) for col in range(size)]
         for row in range(size)]
    A = [[1] * size] + D
    rhs = [1] + [0] * size
    augmented = [row + [value] for row, value in zip(A, rhs)]
    reduced, pivots = _rref(augmented)
    assert len(_rref(D)[1]) == size - 1
    assert len(_rref(A)[1]) == size
    assert pivots == list(range(size))
    weights = [reduced[i][-1] for i in range(size)]
    assert weights == [Q(1, size)] * size
    assert all(sum(a * weight for a, weight in zip(row, weights)) == value
               for row, value in zip(A, rhs))
    assert all(not any(row) for row in reduced[size:])

    # An independent determinant calculation checks the rational vertex and
    # the denominator bound for s=1, without floating-point square roots.
    row_indices = next(indices for indices in combinations(range(len(A)), size)
                       if _determinant([A[i] for i in indices]))
    B = [A[i] for i in row_indices]
    b = [rhs[i] for i in row_indices]
    determinant = _determinant(B)
    cramer_weights = []
    for col in range(size):
        replaced = [row[:] for row in B]
        for i in range(size):
            replaced[i][col] = b[i]
        cramer_weights.append(_determinant(replaced) / determinant)
    assert cramer_weights == weights
    assert abs(determinant) == size
    full_column_norms = [sum(row[col] ** 2 for row in A) for col in range(size)]
    column_norms = [sum(row[col] ** 2 for row in B) for col in range(size)]
    assert all(norm <= 3 for norm in full_column_norms)
    hadamard_product = 1
    for norm, full_norm in zip(column_norms, full_column_norms):
        assert norm <= full_norm
        hadamard_product *= norm
    assert determinant ** 2 <= hadamard_product <= 3 ** size

    # Build the uniform positive witness with exactly size representative
    # words, checking the same sigma/pi semantics used in the large search.
    sigma = [action.index(atom) for atom in range(size)]
    color_permutations = []
    for atom, target in enumerate(sigma):
        source_word, image_word = partitions[atom], partitions[target]
        pi = next(pi for pi in permutations(range(colors))
                  if all(image_word[mapping[i]] == pi[source_word[i]]
                         for i in range(len(points))))
        color_permutations.append(list(pi))
    assert sorted(sigma) == list(range(size))
    assert all(partitions[sigma[atom]][mapping[i]] ==
               color_permutations[atom][partitions[atom][i]]
               for atom in range(size) for i in range(len(points)))
    # Equal-weight m words have integer counts in each normalized partition.
    # Since the unique weights are 1/size, such counts require size | m;
    # repeating the verified uniform witness proves sufficiency for every
    # positive multiple.  This is the exact arithmetic mechanism, not a
    # conclusion extrapolated from checking finitely many values of m.
    assert all(weight.numerator == 1 and weight.denominator == size
               for weight in weights)

    return dict(
        name=name, vertices=len(points), colors=colors,
        actual_pairs=len(distances), induced_edges=len(edges),
        labeled_words_checked=len(all_words), proper_labeled_words=len(proper_words),
        proper_partitions=len(partitions), complete_domain=len(mapping),
        partition_action=action, cycle_length=size,
        invariant_matrix_rank=size - 1, augmented_matrix_rank=size,
        unique_partition_weights=[str(weight) for weight in weights],
        cramer_denominator=size, hadamard_squared_upper_bound=3 ** size,
        equal_weight_word_count_divisibility=size,
        witness_word_permutation=sigma,
        witness_color_permutations=color_permutations)


def verify():
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    line = _calibration(
        'three_point_reflection', [(0, 0), (1, 0), (Q(1, 2), 0)], 2,
        lambda p: (1 - p[0] - p[1], p[1]), [(0, 1)],
        [(0, 1, 0), (0, 1, 1)], [1, 0, 2])
    triangle = _calibration(
        'equilateral_triangle_and_center',
        [(0, 0), (1, 0), (0, 1), (Q(1, 3), Q(1, 3))], 3,
        lambda p: (1 - p[0] - p[1], p[0]), [(0, 1), (0, 2), (1, 2)],
        [(0, 1, 2, 0), (0, 1, 2, 1), (0, 1, 2, 2)], [1, 2, 0, 3])
    return dict(
        status='PASS', calibrations=[line, triangle],
        scope=('Exact two- and three-color finite full-joint calibrations; '
               'word-index count is not the S_k-averaged labeled support; '
               'not a Q009 decision, NON-5 witness, or new HN bound'))


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
