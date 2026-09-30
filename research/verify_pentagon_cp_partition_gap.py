#!/usr/bin/env python3
"""Exact, standard-library calibration for the pentagon matching/blossom example."""
import argparse
import json
from pathlib import Path
if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')
from fractions import Fraction as F
from itertools import combinations

N = 5
UNIT_EDGES = {tuple(sorted((i, (i + 1) % N))) for i in range(N)}
ALLOWABLE_PAIRS = {tuple(sorted(p)) for p in combinations(range(N), 2)} - UNIT_EDGES

# Arithmetic in Q(sqrt(5)): store u + v*sqrt(5) as (u, v).
def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])


def mul(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
B2 = (F(10), F(2))  # b^2 = 10 + 2*sqrt(5)

# Each point is (x, y_coefficient) with y = b*y_coefficient.
# This is the exact unit-side regular pentagon model specified in the research brief.
POINTS = [
    ((F(0), F(0)), ZERO),
    (ONE, ZERO),
    ((F(3, 4), F(1, 4)), (F(1, 4), F(0))),
    ((F(1, 2), F(0)), (F(1, 8), F(1, 8))),
    ((F(1, 4), F(-1, 4)), (F(1, 4), F(0))),
]


def distance_squared(i, j):
    dx = sub(POINTS[i][0], POINTS[j][0])
    dy_coeff = sub(POINTS[i][1], POINTS[j][1])
    return add(mul(dx, dx), mul(B2, mul(dy_coeff, dy_coeff)))


UNIT_D2 = ONE
DIAGONAL_D2 = (F(3, 2), F(1, 2))  # (3 + sqrt(5))/2 = phi^2

# Directly certify all ten exact squared distances and the graph labels.
DISTANCES = {tuple(sorted((i, j))): distance_squared(i, j)
             for i, j in combinations(range(N), 2)}
assert {e for e, d2 in DISTANCES.items() if d2 == UNIT_D2} == UNIT_EDGES
assert {e for e, d2 in DISTANCES.items() if d2 == DIAGONAL_D2} == ALLOWABLE_PAIRS
assert len(UNIT_EDGES) == len(ALLOWABLE_PAIRS) == 5


def restricted_growth_strings(n):
    """Generate each set partition once as a restricted-growth string."""
    def rec(prefix):
        if len(prefix) == n:
            yield tuple(prefix)
            return
        for label in range(max(prefix) + 2):
            yield from rec(prefix + [label])
    yield from rec([0])


def blocks_of(rgs):
    blocks = {}
    for vertex, label in enumerate(rgs):
        blocks.setdefault(label, []).append(vertex)
    return tuple(sorted(tuple(block) for block in blocks.values()))


def is_proper_partition(blocks):
    return all(len(block) <= 2 and
               (len(block) == 1 or tuple(sorted(block)) in ALLOWABLE_PAIRS)
               for block in blocks)

ALL_PARTITIONS = [blocks_of(rgs) for rgs in restricted_growth_strings(N)]
def directly_proper(blocks):
    return all(tuple(sorted(e)) not in UNIT_EDGES
               for block in blocks for e in combinations(block, 2))

PROPER_PARTITIONS = [p for p in ALL_PARTITIONS if directly_proper(p)]
assert all(is_proper_partition(p) for p in PROPER_PARTITIONS)
assert len(ALL_PARTITIONS) == 52  # Bell(5)
assert len(PROPER_PARTITIONS) == 11

# Independently enumerate all matchings of the complement and map each to its
# pair classes plus singleton classes; compare with proper set partitions.
def matching_partition(edge_subset):
    used = set()
    blocks = []
    for edge in edge_subset:
        assert not (used & set(edge))
        used.update(edge)
        blocks.append(edge)
    blocks.extend((v,) for v in range(N) if v not in used)
    return tuple(sorted(blocks))


MATCHING_PARTITIONS = set()
for mask in range(1 << len(ALLOWABLE_PAIRS)):
    chosen = [e for bit, e in enumerate(sorted(ALLOWABLE_PAIRS)) if (mask >> bit) & 1]
    used_vertices = [v for edge in chosen for v in edge]
    if len(used_vertices) == len(set(used_vertices)):
        MATCHING_PARTITIONS.add(matching_partition(chosen))
assert MATCHING_PARTITIONS == set(PROPER_PARTITIONS)

# Candidate pair-marginal vector q_e=1/2 on all five complement edges.
q = {edge: F(1, 2) for edge in ALLOWABLE_PAIRS}
assert sum(q.values(), F(0)) == F(5, 2)
# Degree constraints are tight at every vertex.
for v in range(N):
    assert sum((value for edge, value in q.items() if v in edge), F(0)) == 1
# Every 3-set odd/blossom inequality passes.
for S in combinations(range(N), 3):
    lhs = sum((q[e] for e in ALLOWABLE_PAIRS if set(e) <= set(S)), F(0))
    assert lhs <= F(len(S) - 1, 2)
# The full 5-set blossom inequality fails: 5/2 > 2.
full_blossom_rhs = F(N - 1, 2)
assert sum(q.values(), F(0)) > full_blossom_rhs

# Build Q with diagonal 1, q on allowable pairs, and 0 on unit edges.
Q = [[F(0) for _ in range(N)] for _ in range(N)]
for i in range(N):
    Q[i][i] = F(1)
for i, j in ALLOWABLE_PAIRS:
    Q[i][j] = Q[j][i] = F(1, 2)

# All ordered triangle inequalities of the partition correlation matrix.
for a in range(N):
    for b in range(N):
        for c in range(N):
            assert Q[a][b] + Q[b][c] - Q[a][c] <= 1
# For k=5 and at most5 vertices, every k-block subset pigeonhole lower bound is0.
for m in range(N+1):
    for subset in combinations(range(N),m):
        assert sum((Q[a][b] for a,b in combinations(subset,2)),F(0)) >= 0

# Exact CP witness: P(X=1_e)=1/10 for each allowable pair; P(X=0)=1/2.
# Verify total mass, vertex marginals, and Q=5*E[XX^T].
weights = [(F(1, 10), edge) for edge in sorted(ALLOWABLE_PAIRS)] + [(F(1, 2), ())]
assert sum((weight for weight, _ in weights), F(0)) == 1
EX = [F(0) for _ in range(N)]
EXX = [[F(0) for _ in range(N)] for _ in range(N)]
for weight, support in weights:
    indicator = [int(v in support) for v in range(N)]
    for i in range(N):
        EX[i] += weight * indicator[i]
        for j in range(N):
            EXX[i][j] += weight * indicator[i] * indicator[j]
assert EX == [F(1, 5)] * N
assert [[5 * EXX[i][j] for j in range(N)] for i in range(N)] == Q

# Exact Sylvester PSD certificate. A=20*(Q-J/5) is integral, symmetric,
# and positive leading principal minors imply positive definiteness.
A = [[int(20 * (Q[i][j] - F(1, 5))) for j in range(N)] for i in range(N)]
assert A == [[16 if i == j else (-4 if tuple(sorted((i, j))) in UNIT_EDGES else 6)
               for j in range(N)] for i in range(N)]


def determinant_bareiss(matrix):
    """Exact integer determinant via fraction-free Bareiss elimination."""
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0:
        return 1
    sign, previous_pivot = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            pivot_row = next((i for i in range(k + 1, n) if a[i][k] != 0), None)
            if pivot_row is None:
                return 0
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                assert numerator % previous_pivot == 0
                a[i][j] = numerator // previous_pivot
        for i in range(k + 1, n):
            a[i][k] = 0
        previous_pivot = pivot
    return sign * a[n - 1][n - 1]


leading_minors = [determinant_bareiss([row[:k] for row in A[:k]])
                  for k in range(1, N + 1)]
assert leading_minors == [16, 240, 3200, 26000, 200000]
assert all(det > 0 for det in leading_minors)

# No proper partition contains more than two pairs, so the candidate total 5/2
# cannot be a convex combination of proper-partition pair indicators.
max_pairs = max(sum(len(block) == 2 for block in p) for p in PROPER_PARTITIONS)
assert max_pairs == 2
assert F(5, 2) > max_pairs

report = dict(status='PASS_C027_PENTAGON_CP_NOT_PARTITION',
              vertices=N,actual_unit_edges=[list(x) for x in sorted(UNIT_EDGES)],
              allowed_pairs=[list(x) for x in sorted(ALLOWABLE_PAIRS)],
              exact_pair_distances=[dict(pair=list(e),coefficients=[str(a) for a in d]) for e,d in sorted(DISTANCES.items())],
              all_partitions=len(ALL_PARTITIONS),proper_partitions=len(PROPER_PARTITIONS),
              complement_matchings=len(MATCHING_PARTITIONS),candidate_sum='5/2',
              maximum_partition_pairs=max_pairs,degree_constraints='PASS',
              triangle_constraints='PASS',subset_k5_pigeonhole_constraints='PASS',
              CP_representation='5 E[XX^T]: each allowed pair mass1/10, empty mass1/2',
              shifted_matrix_integer_scale=20,positive_leading_principal_minors=leading_minors,
              scope='A specific CP single-independent-set matrix on an exact unit pentagon is not any proper-partition pair-marginal matrix. No claim about stationary dodecagon moments or HN bounds.')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-certificate',action='store_true')
args=parser.parse_args()
path=Path(__file__).resolve().parents[1]/'certificates/pentagon_cp_partition_gap.json'
if args.write_certificate:
    path.write_text(json.dumps(report,indent=2)+'\n')
else:
    assert json.loads(path.read_text())==report, 'saved pentagon receipt differs'
print(json.dumps(report,indent=2))
