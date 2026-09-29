#!/usr/bin/env python3
"""Build and bounded-colour the exact radius-two ball in L_2.

The geometric graph is induced: T150 supplies the complete unit-difference
set U_2, and every possible neighbour is tested by exact translated lookup.
The SAT outcome is only a bounded search observation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import threading
import time
from itertools import combinations
from pathlib import Path

from pysat.solvers import Glucose3

from search_heptagon_module import ONE, W, W2, mul, neg, sub, wpow, zpow


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "certificates" / "heptagon_actual_patch.json.gz"
SCALE = 49
N = 12


def rational_direction_set():
    """Construct mu_42, r, and U_2 in the existing exact tensor arithmetic."""
    # Reproduce r = Q_0 - R_0 from the source's exact 21-point construction.
    # These inverses are rational field operations, never floating point.
    from search_heptagon_module import inv

    z = zpow(1)
    r = sub(mul(W, inv(sub(z, zpow(-1)))),
            mul(W2, inv(sub(zpow(2), zpow(-2)))))
    zeta21 = mul(zpow(5), wpow(2))
    roots = set()
    p = ONE
    for _ in range(21):
        roots.add(p)
        roots.add(neg(p))
        p = mul(p, zeta21)
    assert len(roots) == 42
    directions = set()
    power = ONE
    for _ in range(3):
        directions.update(mul(power, u) for u in roots)
        power = mul(power, r)
    assert len(directions) == 126
    assert all(sum((q * SCALE).denominator != 1 for q in d) == 0 for d in directions)
    assert all(mul(d, conjugate(d)) == ONE for d in directions)
    return {tuple(int(q * SCALE) for q in d) for d in directions}


def conjugate(a):
    from search_heptagon_module import conjugate as exact_conjugate
    return exact_conjugate(a)


def make_geometry():
    units = rational_direction_set()
    zero = (0,) * N
    points = {zero}
    points.update(units)
    points.update(tuple(a + b for a, b in zip(u, v))
                   for u in units for v in units)
    ordered = sorted(points)
    index = {p: i for i, p in enumerate(ordered)}
    # Every actual unit pair is enumerated using the complete direction set.
    edges = set()
    for i, p in enumerate(ordered):
        for u in units:
            q = tuple(a + b for a, b in zip(p, u))
            j = index.get(q)
            if j is not None and i < j:
                edges.add((i, j))
    edges = sorted(edges)
    degrees = [0] * len(ordered)
    for i, j in edges:
        degrees[i] += 1
        degrees[j] += 1
        # Independent direct-difference verification of every listed edge.
        assert tuple(b - a for a, b in zip(ordered[i], ordered[j])) in units
    # Canonically select the lexicographically first triangle containing 0.
    zero_id = index[zero]
    triangle = None
    for a, b in combinations(sorted(units), 2):
        if tuple(x - y for x, y in zip(a, b)) in units:
            # The ordering is geometric: origin first, then the first
            # lexicographic pair of direction vectors completing its triangle.
            triangle = (zero_id, index[a], index[b])
            break
    assert triangle is not None
    assert all(tuple(sorted(pair)) in set(edges)
               for pair in combinations(triangle, 2))
    return units, ordered, edges, degrees, triangle


def clause_hash(clauses):
    payload = "\n".join(",".join(map(str, c)) for c in clauses).encode()
    return hashlib.sha256(payload).hexdigest()


def var(v, c, k=5):
    return v * k + c + 1


def run_sat(vertex_count, edges, triangle):
    k = 5
    clauses = []
    for v in range(vertex_count):
        lits = [var(v, c, k) for c in range(k)]
        clauses.append(lits)
        clauses.extend([[-lits[a], -lits[b]] for a, b in combinations(range(k), 2)])
    for u, v in edges:
        clauses.extend([[-var(u, c, k), -var(v, c, k)] for c in range(k)])
    fixed = [[var(v, c, k)] for v, c in zip(triangle, (0, 1, 2))]
    clauses.extend(fixed)
    solver = Glucose3()
    started = time.monotonic()
    model = None
    timer_fired = threading.Event()

    def interrupt():
        timer_fired.set()
        solver.interrupt()

    timer = threading.Timer(30.0, interrupt)
    timer.daemon = True
    try:
        for clause in clauses:
            solver.add_clause(clause)
        solver.conf_budget(30000)
        timer.start()
        result = solver.solve_limited(expect_interrupt=True)
        conflicts = solver.accum_stats().get("conflicts")
        if result is True:
            model = solver.get_model()
            status = "SAT"
        elif result is False:
            status = "UNSAT_UNCERTIFIED"
        else:
            status = "UNKNOWN"
    finally:
        timer.cancel()
        timer.join()
        solver.delete()
    colors = None
    if model is not None:
        truth = {x for x in model if x > 0}
        colors = [next(c for c in range(k) if var(v, c, k) in truth)
                  for v in range(vertex_count)]
        assert all(colors[u] != colors[v] for u, v in edges)
        assert [colors[v] for v in triangle] == [0, 1, 2]
    return {
        "status": status,
        "solver": "Glucose3",
        "colors_requested": 5,
        "conflict_budget": 30000,
        "wall_time_limit_seconds": 30,
        "wall_seconds": round(time.monotonic() - started, 3),
        "wall_timeout": timer_fired.is_set(),
        "conflicts": conflicts,
        "cnf_clause_count": len(clauses),
        "cnf_sha256": clause_hash(clauses),
        "symmetry_breaking": {"triangle_point_ids": list(triangle),
                              "colors": [0, 1, 2]},
    }, colors


def encode_word(colors):
    # Two symbols per byte, each encoded as one nibble; stable compact word.
    raw = bytearray((len(colors) + 1) // 2)
    for i, c in enumerate(colors):
        raw[i // 2] |= c << (4 * (i % 2))
    return raw.hex()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-provenance-only", action="store_true")
    args = parser.parse_args()
    if args.record_provenance_only:
        with gzip.open(OUT, "rt", encoding="utf-8") as f:
            cert = json.load(f)
        cert["execution_provenance"] = {
            "bounded_sat_executions": 2,
            "note": "Both executions queried this same graph with the same origin triangle and color-label-equivalent symmetry breaking. The first encoded the triangle in sorted point-id order [a,b,0]; the second corrected the order to [0,a,b] and is the saved SAT record. Both returned UNKNOWN.",
            "first_execution": {"status": "UNKNOWN", "conflicts": 30029,
                                "wall_seconds": 1.498,
                                "triangle_point_ids_in_clause_order": [363, 379, 3969]},
            "saved_execution": {"status": cert["sat"]["status"],
                                "conflicts": cert["sat"]["conflicts"],
                                "wall_seconds": cert["sat"]["wall_seconds"],
                                "triangle_point_ids_in_clause_order": cert["sat"]["symmetry_breaking"]["triangle_point_ids"]},
        }
        with gzip.open(OUT, "wt", encoding="utf-8", newline="\n", compresslevel=9) as f:
            json.dump(cert, f, indent=2)
            f.write("\n")
        return
    units, points, edges, degrees, triangle = make_geometry()
    point_hash = hashlib.sha256(json.dumps(points, separators=(",", ":")).encode()).hexdigest()
    edge_hash = hashlib.sha256(json.dumps(edges, separators=(",", ":")).encode()).hexdigest()
    triangle_points = [list(points[i]) for i in triangle]
    cert = {
        "schema": "heptagon-actual-patch-v1",
        "status": "exact induced finite graph; bounded coloring query",
        "construction": "B2={0} union U2 union {u+v:u,v in U2}; U2=mu42 union r*mu42 union r^2*mu42",
        "field": "Q(z,w), Phi_7(z)=0, w^2+w+1=0",
        "basis_order": [f"z^{i}w^{b}" for b in range(2) for i in range(6)],
        "denominator": SCALE,
        "coordinate_representation": "12 integer tensor-basis coordinates scaled by 49; point order is lexicographic",
        "unit_directions": len(units),
        "geometry": {
            "vertices": len(points), "edges": len(edges),
            "max_degree": max(degrees, default=0),
            "point_order": "lexicographic tensor coordinates scaled by 49",
            "point_list_sha256": point_hash,
            "edge_list_sha256": edge_hash,
            "edge_list_hash_encoding": "sha256(json.dumps(edge_list,separators=(',',':')).encode())",
            "point_list_hash_encoding": "sha256(json.dumps(point_list,separators=(',',':')).encode())",
            "edge_generation": "for each point p and each complete T150 direction u, lookup p+u in the exact point hash",
            "edge_direct_difference_rebuilt": True,
            "origin_triangle_point_ids": list(triangle),
            "origin_triangle_points": triangle_points,
        },
        "sat": {"status": "NOT_RUN_MEMORY_LIMIT"},
    }
    # Geometry is complete and compactly represented in memory before the SAT
    # encoding is allocated. Avoid entering SAT if geometry itself is large.
    if len(points) > 20000 or len(edges) > 1_000_000:
        cert["sat"]["reason"] = "geometry memory guard reached before SAT"
    else:
        sat, colors = run_sat(len(points), edges, triangle)
        cert["sat"] = sat
        if colors is not None:
            cert["color_word_encoding"] = "two 4-bit nibbles per byte in point order; symbols 0..4"
            cert["color_word_hex"] = encode_word(colors)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8", newline="\n", compresslevel=9) as f:
        json.dump(cert, f, indent=2)
        f.write("\n")
    print(json.dumps({"certificate": str(OUT), "status": cert["sat"]["status"],
                      "vertices": len(points), "edges": len(edges),
                      "max_degree": max(degrees, default=0), "triangle": list(triangle)}, indent=2))


if __name__ == "__main__":
    main()
