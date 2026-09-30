#!/usr/bin/env python3
"""Exhaustive small-graph check of the projected-flow/SCC rank lemma.

Standard library only. This is a calibration, not a test of any full-Y port
relation or a mathematical certificate for the Hadwiger--Nelson instance.
"""
import sys
from itertools import product

if not __debug__:
    sys.exit("Run without -O: this calibration requires assertions")


def check_graph(n: int, mask: int) -> tuple[int, int]:
    arcs = [(u, v) for u in range(n) for v in range(n)
            if (mask >> (u * n + v)) & 1]
    reach = [[u == v for v in range(n)] for u in range(n)]
    for u, v in arcs:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

    scc_internal = {e for e in arcs if reach[e[1]][e[0]]}
    cycle_arcs = set()
    # Enumerate all vertex-simple directed cycles of length at most n.
    for length in range(1, n + 1):
        for vertices in product(range(n), repeat=length):
            if len(set(vertices)) != length or vertices[0] != min(vertices):
                continue
            cycle = list(zip(vertices, vertices[1:] + vertices[:1]))
            if all(edge in arcs for edge in cycle):
                cycle_arcs.update(cycle)
    assert scc_internal == cycle_arcs, (n, arcs, scc_internal, cycle_arcs)

    remaining = set(range(n))
    components = []
    while remaining:
        root = min(remaining)
        comp = {v for v in remaining if reach[root][v] and reach[v][root]}
        components.append(comp)
        remaining -= comp
    component_of = {v: i for i, comp in enumerate(components) for v in comp}
    dag = {i: set() for i in range(len(components))}
    for u, v in arcs:
        if component_of[u] != component_of[v]:
            dag[component_of[u]].add(component_of[v])

    height = {}

    def to_sink(i: int) -> int:
        if i not in height:
            height[i] = max([1 + to_sink(j) for j in dag[i]] + [0])
        return height[i]

    for i in dag:
        to_sink(i)
    for u, v in arcs:
        hu, hv = height[component_of[u]], height[component_of[v]]
        crosses_scc = component_of[u] != component_of[v]
        assert hu >= hv
        assert (hu > hv) == crosses_scc
    return len(arcs), len(cycle_arcs)


def main() -> None:
    reports = []
    for n in (1, 2, 3):
        graph_count = 1 << (n * n)
        total_arcs = total_cyclic_arcs = 0
        for mask in range(graph_count):
            arcs, cyclic = check_graph(n, mask)
            total_arcs += arcs
            total_cyclic_arcs += cyclic
        reports.append((n, graph_count, total_arcs, total_cyclic_arcs))
    assert reports == [(1, 2, 1, 1), (2, 16, 32, 24), (3, 512, 2304, 1728)]
    print({"status": "PASS", "vertices_1_to_3": reports,
           "total_graphs": sum(row[1] for row in reports),
           "total_cyclic_arcs": sum(row[3] for row in reports),
           "scope": "graph lemma calibration only; no full-Y relation tested"})


if __name__ == "__main__":
    main()
