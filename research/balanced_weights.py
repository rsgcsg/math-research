"""Exact linear feasibility of equal color-class mass, for fully enumerated graphs."""
from fractions import Fraction
from relations import color_partitions, calibrate


def solve(rows, rhs, n):
    matrix = [[Fraction(x) for x in row] + [Fraction(b)] for row, b in zip(rows, rhs)]
    rank, pivots = 0, []
    for col in range(n):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        a = matrix[rank][col]
        matrix[rank] = [x / a for x in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][col]:
                a = matrix[i][col]
                matrix[i] = [x-a*y for x, y in zip(matrix[i], matrix[rank])]
        pivots.append(col)
        rank += 1
    if any(not any(row[:n]) and row[n] for row in matrix):
        return None, rank
    answer = [Fraction(0)] * n
    for i, col in enumerate(pivots):
        answer[col] = matrix[i][n]
    assert all(sum(Fraction(a)*b for a, b in zip(row, answer)) == v for row, v in zip(rows, rhs))
    return answer, rank


def check(n, edges, k):
    partitions = list(color_partitions(n, edges, k))
    assert partitions, 'Empty coloring set already gives an obstruction'
    rows = sorted({tuple(k*int(coloring[v] == c)-1 for v in range(n))
                   for coloring in partitions for c in range(k)})
    weights, rank = solve(rows + [(1,)*n], [0]*len(rows) + [1], n)
    return dict(vertices=n, colors=k, complete_partitions=len(partitions),
                distinct_mass_rows=len(rows), rank=rank,
                normalized_weights=None if weights is None else [str(w) for w in weights])


def run():
    triangle = check(3, [(0, 1), (0, 2), (1, 2)], 3)
    assert triangle['normalized_weights'] == ['1/3']*3
    cycle = check(5, [(i, (i+1) % 5) for i in range(5)], 3)
    spindle = check(7, calibrate()['spindle_edges'], 4)
    assert cycle['normalized_weights'] is spindle['normalized_weights'] is None
    return dict(triangle=triangle, odd_cycle=cycle, moser_spindle=spindle)


if __name__ == '__main__':
    import json
    print(json.dumps(run(), indent=2))
