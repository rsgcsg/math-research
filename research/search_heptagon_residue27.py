#!/usr/bin/env python3
"""Bounded SAT probe for the residue-field heptagon graph over F_3.

The arithmetic and graph checks are exact. SAT outcomes are only bounded
search observations: UNKNOWN is not a non-colourability result.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path

from pysat.solvers import Glucose3


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "certificates" / "heptagon_residue27_probe.json"
Q = 3
N = 6
MOD = (1, 1, 1, 1, 1, 1)  # Phi_7(X)=1+X+...+X^6; X^6=-(1+...+X^5).


def add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((x + y) % Q for x, y in zip(a, b))


def neg(a: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((-x) % Q for x in a)


def mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    c = [0] * 11
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    for k in range(10, 5, -1):
        x = c[k] % Q
        if x:
            for j in range(6):
                c[k - 6 + j] -= x * MOD[j]
    return tuple(x % Q for x in c[:6])


ZERO = (0,) * 6
ONE = (1, 0, 0, 0, 0, 0)
X = (0, 1, 0, 0, 0, 0)


def power(a: tuple[int, ...], n: int) -> tuple[int, ...]:
    r = ONE
    while n:
        if n & 1:
            r = mul(r, a)
        a = mul(a, a)
        n >>= 1
    return r


def code(a: tuple[int, ...]) -> int:
    return sum(x * (Q**i) for i, x in enumerate(a))


def decode(v: int) -> tuple[int, ...]:
    a = []
    for _ in range(N):
        a.append(v % Q)
        v //= Q
    return tuple(a)


def build_graph():
    # The reduced geometric unit differences are the relative-norm-one
    # elements for F_729/F_27, so d^(27+1)=1. Enumerate every root.
    unit_dirs = {code(a) for a in map(decode, range(Q**N)) if a != ZERO and power(a, 28) == ONE}
    assert len(unit_dirs) == 28
    assert {1, 2} <= unit_dirs
    edges = []
    for u in range(Q**N):
        a = decode(u)
        for d in unit_dirs:
            v = code(add(a, decode(d)))
            if u < v:
                edges.append((u, v))
    edges.sort()
    degree = [0] * (Q**N)
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    assert set(degree) == {28}
    return sorted(unit_dirs), edges, degree


def var(v: int, c: int, k: int) -> int:
    return v * k + c + 1


def make_cnf(k: int, edges: list[tuple[int, int]], fixed_clique: bool):
    clauses = []
    for v in range(Q**N):
        literals = [var(v, c, k) for c in range(k)]
        clauses.append(literals)
        clauses.extend([[-literals[i], -literals[j]] for i in range(k) for j in range(i + 1, k)])
    for u, v in edges:
        for c in range(k):
            clauses.append([-var(u, c, k), -var(v, c, k)])
    symbreak = []
    if fixed_clique:
        # Vertices 0,1,2 are the constant-field F_3 clique; fix its colors.
        assert all(tuple(sorted((u, v))) in set(edges) for u, v in ((0, 1), (0, 2), (1, 2)))
        symbreak = [[var(v, c, k)] for v, c in ((0, 0), (1, 1), (2, 2))]
        clauses.extend(symbreak)
    canonical_cnf = "\n".join(",".join(map(str, clause)) for clause in clauses).encode()
    return clauses, symbreak, hashlib.sha256(canonical_cnf).hexdigest()


def timed_probe(k: int, edges: list[tuple[int, int]], fixed_clique: bool) -> dict:
    clauses, symbreak, cnf_hash = make_cnf(k, edges, fixed_clique)
    start = time.monotonic()
    status = "UNKNOWN"
    model = None
    conflicts = None
    timed_out = False
    solver = Glucose3(bootstrap_with=clauses)
    timer_fired = threading.Event()

    def interrupt_solver():
        timer_fired.set()
        solver.interrupt()

    timer = threading.Timer(20, interrupt_solver)
    timer.daemon = True
    try:
        solver.conf_budget(150000)
        timer.start()
        sat = solver.solve_limited(expect_interrupt=True)
        timed_out = timer_fired.is_set()
        conflicts = solver.accum_stats().get("conflicts")
        if sat is True:
            status = "SAT"
            model = solver.get_model()
        elif sat is False:
            status = "UNSAT_WITHIN_SOLVER_RESULT"
    finally:
        timer.cancel()
        timer.join()
        solver.delete()
    coloring = None
    if model is not None:
        true = {x for x in model if x > 0}
        coloring = [next(c for c in range(k) if var(v, c, k) in true) for v in range(Q**N)]
        assert all(coloring[u] != coloring[v] for u, v in edges)
    return {
        "colors": k,
        "solver": "Glucose3",
        "conflict_budget": 150000,
        "wall_time_limit_seconds": 20,
        "symmetry_normalized": fixed_clique,
        "symmetry_breaking_unit_clauses": symbreak,
        "cnf_clause_count": len(clauses),
        "cnf_sha256": cnf_hash,
        "status": status,
        "wall_seconds": round(time.monotonic() - start, 3),
        "conflicts": conflicts,
        "wall_timeout": timed_out,
        "coloring": coloring,
    }


def main() -> None:
    dirs, edges, degree = build_graph()
    edge_bytes = "\n".join(f"{u},{v}" for u, v in edges).encode()
    result = json.loads(OUT.read_text())
    assert result["exact_graph_checks"]["sorted_edge_list_sha256"] == hashlib.sha256(edge_bytes).hexdigest()
    result["field"]["unit_difference_equation"] = "Relative norm F_729/F_27: d^(3^3+1)=d^28=1; kernel has 28 elements"
    result["exact_graph_checks"]["clique_vertices"] = [0, 1, 2]
    result["symmetry_normalized_sat"] = [timed_probe(k, edges, True) for k in (5, 6)]
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    printable = {key: value for key, value in result.items() if key not in {"sat", "symmetry_normalized_sat"}}
    printable["sat"] = [{k: v for k, v in row.items() if k != "coloring"} for row in result["sat"]]
    printable["symmetry_normalized_sat"] = [
        {k: v for k, v in row.items() if k != "coloring"} for row in result["symmetry_normalized_sat"]
    ]
    print(json.dumps(printable, indent=2))


if __name__ == "__main__":
    main()
