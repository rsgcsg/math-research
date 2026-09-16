"""Independent standard-library checks for T120 / C023, without SAT."""

from fractions import Fraction as Q
from itertools import combinations, product


def quadratic(a=0, b=0):
    """a + b sqrt(15)."""
    return Q(a), Q(b)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, b):
    return a[0] * b[0] + 15 * a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def complex_mul(a, b):
    return sub(mul(a[0], b[0]), mul(a[1], b[1])), add(mul(a[0], b[1]), mul(a[1], b[0]))


def norm(a):
    return add(mul(a[0], a[0]), mul(a[1], a[1]))


def verify():
    if not __debug__:
        raise RuntimeError("this proof checker requires assertions")
    points = [
        (quadratic(0), quadratic(0)),
        (quadratic(1), quadratic(0)),
        (quadratic(2), quadratic(0)),
        (quadratic(Q(7, 4)), quadratic(0, Q(1, 4))),
        (quadratic(Q(7, 8)), quadratic(0, Q(1, 8))),
    ]
    distances = {
        (i, j): norm((sub(points[i][0], points[j][0]), sub(points[i][1], points[j][1])))
        for i, j in combinations(range(5), 2)
    }
    expected = {
        (0, 1): Q(1), (0, 2): Q(4), (0, 3): Q(4), (0, 4): Q(1),
        (1, 2): Q(1), (1, 3): Q(3, 2), (1, 4): Q(1, 4),
        (2, 3): Q(1), (2, 4): Q(3, 2), (3, 4): Q(1),
    }
    assert distances == {ij: quadratic(value) for ij, value in expected.items()}
    edges = {ij for ij, value in distances.items() if value == quadratic(1)}
    assert edges == {(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)}
    old_edges = {ij for ij in edges if max(ij) < 4}
    assert old_edges == {(0, 1), (1, 2), (2, 3)}
    rotation = points[4]
    assert norm(rotation) == quadratic(1)
    mapping = [(i, points[:4].index(complex_mul(rotation, point)))
               for i, point in enumerate(points[:4])
               if complex_mul(rotation, point) in points[:4]]
    assert mapping == [(0, 0), (2, 3)]
    old_words = [word for word in product(range(2), repeat=4)
                 if all(word[i] != word[j] for i, j in old_edges)]
    assert old_words == [(0, 1, 0, 1), (1, 0, 1, 0)]
    assert all(word[0] == word[2] and word[0] != word[3] for word in old_words)
    new_words = [word for word in product(range(2), repeat=5)
                 if all(word[i] != word[j] for i, j in edges)]
    assert not new_words
    three_word = (0, 1, 0, 1, 2)
    assert all(three_word[i] != three_word[j] for i, j in edges)

    # A genuine two-word law on X={0,1,1/3,2/3}, with a repeated code.
    # Reflection swaps both pairs. T(a,b)=(1-b,1-a) fixes code 01.
    calibration_points = (Q(0), Q(1), Q(1, 3), Q(2, 3))
    assert [(i, j) for i, j in combinations(range(4), 2)
            if abs(calibration_points[i] - calibration_points[j]) == 1] == [(0, 1)]
    reflection = [calibration_points.index(1 - x) for x in calibration_points]
    assert reflection == [1, 0, 3, 2]
    source_words = ((0, 1, 0, 0), (0, 1, 1, 1))
    codes = list(zip(*source_words))
    embedding = [(code, i) for i, code in enumerate(codes)]
    vertices = list(product(product(range(2), repeat=2), range(4)))

    def adjacent(x, y):
        return all(a != b for a, b in zip(x[0], y[0]))

    def transform(x):
        code, label = x
        target = 1 - code[1], 1 - code[0]
        # Complete the required 00-label 0 -> 11-label 1 and inverse.
        labels = ((1, 0, 2, 3) if code in ((0, 0), (1, 1))
                  else (0, 1, 3, 2) if code == (0, 1) else (0, 1, 2, 3))
        return target, labels[label]

    assert len(vertices) == 16
    assert len(set(map(transform, vertices))) == len(vertices)
    for x, y in combinations(vertices, 2):
        assert adjacent(x, y) == adjacent(transform(x), transform(y))
        if adjacent(x, y):
            assert x[0][0] != y[0][0]
    assert codes[2] == codes[3] and embedding[2] != embedding[3]
    assert [transform(x) for x in embedding] == [embedding[i] for i in reflection]
    assert adjacent(embedding[0], embedding[1])
    return dict(points=5, pairs=10, old_edges=3, new_edges=5,
                old_two_colorings=len(old_words), new_two_colorings=len(new_words),
                maximum_partial_domain=mapping, completion_vertices=len(vertices),
                completion_pairs=len(vertices) * (len(vertices) - 1) // 2)


if __name__ == '__main__':
    print('PASS finite joint completion', verify())
