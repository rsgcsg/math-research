#!/usr/bin/env python3
"""Exhaustive, replayable three-colouring search tree for Haugland's graph H."""

import json
from pathlib import Path

from search_heptagon_module import ONE, conjugate, mul, point, sub

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "certificates" / "heptagon_three_tree.json"
PALETTE = 3


def build_graph():
    order = [(f, j) for f in "PQR" for j in range(7)]
    coords = [point(f, j) for f, j in order]
    edges = []
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            delta = sub(coords[i], coords[j])
            if mul(delta, conjugate(delta)) == ONE:
                edges.append((i, j))
    if len(edges) != 42:
        raise AssertionError(f"expected 42 induced unit edges, got {len(edges)}")
    return order, coords, edges


def exhaustive_tree(adjacency, colors):
    stats = {"branch_nodes": 0, "blocked_leaves": 0, "assigned_leaves": 0}

    def recurse(colors):
        unassigned = [v for v, c in enumerate(colors) if c < 0]
        if not unassigned:
            stats["assigned_leaves"] += 1
            return {"countercolor": colors}

        available = {}
        for v in unassigned:
            used = {colors[u] for u in adjacency[v] if colors[u] >= 0}
            available[v] = [c for c in range(PALETTE) if c not in used]
        candidates = [v for v in unassigned if available[v]]
        if not candidates:
            v = min(unassigned)
            stats["blocked_leaves"] += 1
            return {"blocked_vertex": v}

        # Minimum remaining colors, then maximum degree in the unassigned graph,
        # then smallest index for a stable, deterministic tie break.
        v = min(candidates, key=lambda x: (len(available[x]),
                                            -sum(colors[u] < 0 for u in adjacency[x]), x))
        stats["branch_nodes"] += 1
        children = {}
        for color in available[v]:
            next_colors = list(colors)
            next_colors[v] = color
            child = recurse(next_colors)
            if "countercolor" in child:
                raise AssertionError("H has a proper 3-colouring extending the root palette")
            children[str(color)] = child
        return {"vertex": v, "children": children}

    tree = recurse(colors)
    if stats["assigned_leaves"]:
        raise AssertionError("unexpected colouring leaf")
    return tree, stats


def main():
    order, coords, edges = build_graph()
    adjacency = [set() for _ in order]
    for i, j in edges:
        adjacency[i].add(j)
        adjacency[j].add(i)

    # Fix the source triangle P0,Q0,R0 to distinct colours 0,1,2.
    root_palette = [[0, 0], [7, 1], [14, 2]]
    colors = [-1] * len(order)
    for vertex, color in root_palette:
        if colors[vertex] >= 0 or any(colors[u] == color for u in adjacency[vertex]):
            raise AssertionError("invalid root palette")
        colors[vertex] = color

    tree, stats = exhaustive_tree(adjacency, colors)
    certificate = {
        "status": "complete exhaustive direct branching tree; H is not 3-colourable",
        "source": {
            "title": "A Moser-spindle-free 5-chromatic unit distance graph on 2131 vertices in the plane",
            "author": "Jan Kristian Haugland",
            "version": "arXiv:2608.04542v4, 2026-08-17",
            "url": "https://arxiv.org/html/2608.04542v4",
            "geometry": "Section 2; exact coordinates in Q(z,w), Phi_7(z)=0 and w^2+w+1=0."
        },
        "point_order": [f"{f}{j}" for f, j in order],
        "edge_count": len(edges),
        "edges": [list(e) for e in edges],
        "root_palette": root_palette,
        "palette_size": PALETTE,
        "branch_rule": "Choose unassigned vertex with fewest currently available colors, then largest degree in unassigned induced graph, then smallest index; branch over all available colors in ascending order; never propagate silently.",
        "stats": stats,
        "nodes": tree
    }
    CERT.parent.mkdir(parents=True, exist_ok=True)
    CERT.write_text(json.dumps(certificate, separators=(",", ":")) + "\n")
    print(json.dumps({"certificate": str(CERT), "vertices": len(order),
                      "edges": len(edges), "stats": stats,
                      "certificate_bytes": CERT.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
