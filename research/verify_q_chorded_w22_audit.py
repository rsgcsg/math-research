#!/usr/bin/env python3
"""Exact W22 audit of the smallest facet-inducing q-chorded cycle inequalities.

The audit is deliberately local: it uses only pair types already certified in
q_joint_boundary_gap.json.  Unit edges are reconstructed from the seven
saturated K7 windows exactly as in the inherited verifier.  No unclassified
pair is ever treated as known.

For C030 the common moments are
  P=1/27, Q=7/10, R=14/27, E=0.
We scale by 270, so the corresponding pair weights are
  P=10, Q=189, R=140, E=0.

For a cyclic word v_0,...,v_{k-1}, the q-chorded k-cycle functional is
  sum_i x(v_i,v_{i+1}) - sum_i x(v_i,v_{i+q}),
with indices modulo k.  The valid upper bound is k-ceil(k/q).

This script exhausts the smallest cases which are facet-inducing by the
Irmai--Naumann--Andres criterion and whose support size is at most ten:
(5,2), (7,2), (9,2), (7,3), (9,4), (10,3).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "certificates/q_joint_boundary_gap.json"
CERT = ROOT / "certificates/q_chorded_w22_audit.json"

SCALE = 270
WEIGHT = {"P": 10, "Q": 189, "R": 140, "E": 0}
TARGETS = [(5,2),(7,2),(9,2),(7,3),(9,4),(10,3)]


def pair(a, b):
    return (a, b) if a < b else (b, a)


def ceil_div(a, b):
    return (a + b - 1) // b


def build_tags(source):
    tags = {}
    for term in source["boundary"]["terms"]:
        p = pair(*term["pair"])
        if p in tags:
            raise ValueError("duplicate certified P/Q/R pair")
        tags[p] = term["type"]

    # Every saturated window is a complete K7 with pair types E/P/R.
    # P and R are already listed individually in boundary.terms.
    for window in source["boundary"]["saturated_windows"]:
        if len(window) != 7 or len(set(window)) != 7:
            raise ValueError("bad saturated window")
        for i, a in enumerate(window):
            for b in window[i+1:]:
                p = pair(a, b)
                tags.setdefault(p, "E")

    counts = {t: 0 for t in WEIGHT}
    for t in tags.values():
        if t not in counts:
            raise ValueError("unexpected pair type")
        counts[t] += 1
    if counts != {"P": 47, "Q": 11, "R": 31, "E": 31}:
        raise ValueError("unexpected certified local pair counts")
    return tags


def audit_known_support_cliques(vertices, tags, windows):
    """Prove the known-pair support has clique number exactly seven.

    Direct combination enumeration is intentionally independent of the
    q-chorded DFS below: all 8-subsets are rejected, and all 7-subsets are
    collected exactly.
    """
    from itertools import combinations
    known = set(tags)
    size7 = []
    for C in combinations(vertices, 7):
        if all(pair(a, b) in known for a, b in combinations(C, 2)):
            size7.append(list(C))
    for C in combinations(vertices, 8):
        if all(pair(a, b) in known for a, b in combinations(C, 2)):
            raise ValueError("known-pair support contains a K8")
    expected = sorted(sorted(w) for w in windows)
    if sorted(size7) != expected:
        raise ValueError("maximal K7 family is not exactly the seven saturated windows")
    return {"maximum_clique_size": 7, "size7_cliques": size7}


def audit_case(vertices, tags, k, q):
    known = {a: set() for a in vertices}
    for a, b in tags:
        known[a].add(b)
        known[b].add(a)

    best_num = None
    best_cycle = None
    cycles = 0
    nodes = 0
    path = []
    used = set()

    def w(a, b):
        t = tags.get(pair(a, b))
        return None if t is None else WEIGHT[t]

    def run_from(start_index):
        nonlocal path, used, cycles, nodes, best_num, best_cycle
        start = vertices[start_index]
        path = [start]
        used = {start}

        def rec():
            nonlocal cycles, nodes, best_num, best_cycle
            nodes += 1
            n = len(path)
            if n == k:
                # Reflection symmetry: retain one orientation.
                if path[1] > path[-1]:
                    return
                # Closure may introduce adjacency/q-chord pairs not checked
                # during forward construction.
                for i in range(k):
                    if w(path[i], path[(i+1) % k]) is None:
                        return
                    if w(path[i], path[(i+q) % k]) is None:
                        return
                cycles += 1
                num = sum(
                    w(path[i], path[(i+1) % k])
                    - w(path[i], path[(i+q) % k])
                    for i in range(k)
                )
                if best_num is None or num > best_num:
                    best_num = num
                    best_cycle = list(path)
                return

            # start is the minimum vertex of the cycle, removing rotations.
            for j in range(start_index + 1, len(vertices)):
                v = vertices[j]
                if v in used:
                    continue
                if v not in known[path[-1]]:
                    continue
                if n >= q and v not in known[path[-q]]:
                    continue
                path.append(v)
                used.add(v)
                rec()
                used.remove(v)
                path.pop()

        rec()

    for si in range(len(vertices)):
        run_from(si)

    if best_num is None:
        raise ValueError("no supported cycle found")
    rhs_num = SCALE * (k - ceil_div(k, q))
    return {
        "k": k,
        "q": q,
        "supported_cycles": cycles,
        "search_nodes": nodes,
        "best_numerator_over_270": best_num,
        "rhs_numerator_over_270": rhs_num,
        "slack_numerator_over_270": rhs_num - best_num,
        "best_cycle": best_cycle,
        "cycle_pair_types": [
            tags[pair(best_cycle[i], best_cycle[(i+1) % k])]
            for i in range(k)
        ],
        "q_chord_pair_types": [
            tags[pair(best_cycle[i], best_cycle[(i+q) % k])]
            for i in range(k)
        ],
    }


def main():
    source = json.loads(SOURCE.read_text())
    cert = json.loads(CERT.read_text())
    if source.get("schema") != "q-joint-boundary-gap-v1":
        raise ValueError("wrong source schema")
    if source["fractional_cover"]["means"] != {
        "P": [1,27], "Q": [7,10], "R": [14,27]
    }:
        raise ValueError("unexpected C030 means")
    vertices = source["boundary"]["vertices"]
    if len(vertices) != 22 or vertices != sorted(set(vertices)):
        raise ValueError("unexpected W22 vertex set")

    tags = build_tags(source)
    clique_audit = audit_known_support_cliques(
        vertices, tags, source["boundary"]["saturated_windows"]
    )
    if clique_audit != cert["known_support_cliques"]:
        raise ValueError("known-support clique audit differs from frozen certificate")
    got = [audit_case(vertices, tags, k, q) for k, q in TARGETS]

    # The frozen certificate intentionally excludes node counts: they are
    # implementation diagnostics, not mathematical output.
    compact = []
    for r in got:
        compact.append({
            k: v for k, v in r.items()
            if k != "search_nodes"
        })

    expected = cert["cases"]
    if compact != expected:
        raise ValueError("q-chorded audit differs from frozen certificate")
    if any(r["slack_numerator_over_270"] <= 0 for r in got):
        raise ValueError("C030 violates an audited q-chorded cycle inequality")

    print(json.dumps({
        "status": "PASS",
        "certified_pair_counts": {"P":47,"Q":11,"R":31,"E":31},
        "targets": TARGETS,
        "known_support_cliques": clique_audit,
        "cases": got,
        "scope": cert["scope"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
