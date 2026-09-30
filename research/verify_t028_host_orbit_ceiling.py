#!/usr/bin/env python3
"""Stdlib checks for the T028 finite-table two-terminal relation census.

Checks finite certificate facts only. The valuation argument lifting the
table to all of K^2 is in docs/proofs/residue_field_ceiling.md.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "certificates/residue11_coloring.json"
EXPECTED_TABLE_SHA256 = "ae2fc6b4d66911ce16cc5bafc5199836ae8745e0c53e76249060417a01485d7c"
if not __debug__:
    raise RuntimeError("verification requires assertions")
table_bytes = TABLE_PATH.read_bytes()
table_hash = sha256(table_bytes).hexdigest()
assert table_hash == EXPECTED_TABLE_SHA256, (table_hash, EXPECTED_TABLE_SHA256)
data = json.loads(table_bytes)
assert data["field_order"] == 11 and data["colors"] == 5
rows = data["rows"]
assert len(rows) == 11 and all(len(row) == 11 for row in rows)
color = [[int(c) for c in row] for row in rows]
assert set(c for row in color for c in row) == set(range(5))

# Rebuild the finite norm-one graph directly and check every edge.
vertices = list(product(range(11), repeat=2))
edges = [(p, q) for p, q in combinations(vertices, 2)
         if ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) % 11 == 1]
assert len(edges) == 726
assert all(color[x][y] != color[u][v]
           for (x, y), (u, v) in edges)

# Full census: for each residue norm, count unordered table pairs of the same
# and different colors. This proves both statuses occur at every norm 2..10.
same = Counter()
different = Counter()
for p, q in combinations(vertices, 2):
    norm = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) % 11
    target = same if color[p[0]][p[1]] == color[q[0]][q[1]] else different
    target[norm] += 1
assert same == Counter({
    2: 281, 3: 231, 4: 152, 5: 96, 6: 183,
    7: 134, 8: 172, 9: 88, 10: 76,
})
assert different == Counter({
    1: 726, 2: 445, 3: 495, 4: 574, 5: 630,
    6: 543, 7: 592, 8: 554, 9: 638, 10: 650,
})
assert all(same[r] and different[r] for r in range(2, 11))
assert same[0] == different[0] == 0  # -1 nonsquare: norm is anisotropic
assert same[1] == 0                  # proper coloring on norm-one edges

# Check that O_2(F_11) is transitive on each nonzero norm shell. The proof
# note also gives the short field-extension proof (multiplication by a
# norm-one element in F_121); this is an exhaustive finite check.
def norm(v):
    return (v[0] * v[0] + v[1] * v[1]) % 11

matrices = []
for a, b, c, d in product(range(11), repeat=4):
    col1, col2 = (a, c), (b, d)
    if (norm(col1) == norm(col2) == 1
            and (a * b + c * d) % 11 == 0):
        matrices.append((a, b, c, d))
assert len(matrices) == 24

def act(M, v):
    a, b, c, d = M
    return ((a * v[0] + b * v[1]) % 11,
            (c * v[0] + d * v[1]) % 11)

for r in range(1, 11):
    shell = [v for v in vertices if norm(v) == r]
    assert len(shell) == 12
    orbit = {act(M, shell[0]) for M in matrices}
    assert orbit == set(shell)

# Table pairs based at zero give concrete equal-color witnesses for the four
# square residues relevant to real distances in K after 11-adic reduction.
representatives = {3: (0, 6), 4: (1, 5), 5: (0, 4), 9: (2, 4)}
assert color[0][0] == 0
for r, q in representatives.items():
    assert color[q[0]][q[1]] == 0 and norm(q) == r

print("PASS: exact table SHA256", table_hash)
print("PASS: 121 vertices, 726 norm-one edges, all five colors")
print("same-color counts:", dict(sorted(same.items())))
print("different-color counts:", dict(sorted(different.items())))
print("PASS: O_2(F_11) has 24 elements and acts transitively on each nonzero norm shell")
print("PASS: both terminal color-equality statuses occur for every reduced norm 2..10")
