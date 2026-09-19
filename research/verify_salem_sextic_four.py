#!/usr/bin/env python3
"""Independent exact E095 checker; Python standard library only.

Geometry uses the cubic trace field, not the producer's sextic multiplication.
The non-3-colouring certificate is a branching tree with singleton propagation.
The checker never searches for a branch and does not import the producer.
"""
from __future__ import annotations
import argparse
import gzip
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: object) -> bool:
    return type(value) is int


def trace_times_t(a: tuple[int, int, int]) -> tuple[int, int, int]:
    """Multiply by t in Z[t]/(t^3-4t-1)."""
    x, y, z = a
    return z, x + 4*z, y


def unit_difference(a: list[int], b: list[int]) -> bool:
    d = [x-y for x, y in zip(a, b)]
    total = [sum(x*x for x in d), 0, 0]
    previous, current = (2, 0, 0), (0, 1, 0)
    for k in range(1, 6):
        coefficient = sum(d[j]*d[j+k] for j in range(6-k))
        total = [x + coefficient*y for x, y in zip(total, current)]
        nxt = tuple(x-y for x, y in zip(trace_times_t(current), previous))
        previous, current = current, nxt
    return total == [1, 0, 0]


def propagate(domains: list[int], adjacency: list[set[int]]) -> bool:
    """Only the sound rule: a neighbour of a fixed colour cannot use it."""
    pending = deque(v for v, mask in enumerate(domains) if mask in (1, 2, 4))
    while pending:
        u = pending.popleft()
        mask = domains[u]
        require(mask in (1, 2, 4), 'invalid singleton propagation state')
        for v in sorted(adjacency[u]):
            if domains[v] & mask:
                domains[v] &= ~mask
                if domains[v] == 0:
                    return False
                if domains[v] in (1, 2, 4):
                    pending.append(v)
    return True


def check_tree(tree: object, domains: list[int], adjacency: list[set[int]],
               counts: dict[str, int]) -> None:
    counts['nodes'] += 1
    consistent = propagate(domains, adjacency)
    if integer(tree) and tree == -1:
        require(not consistent, 'false contradiction leaf')
        counts['leaves'] += 1
        return
    require(consistent, 'noncanonical branch below a contradiction')
    require(type(tree) is list and len(tree) == 2, 'invalid branch node')
    v, children = tree
    require(integer(v) and 0 <= v < len(domains), 'invalid branch vertex')
    require(domains[v].bit_count() >= 2, 'branch must be on an undecided vertex')
    require(type(children) is list and len(children) == 3, 'three colour slots required')
    counts['branches'] += 1
    for colour in range(3):
        allowed = bool(domains[v] & (1 << colour))
        require((children[colour] is not None) == allowed, 'missing or extra colour branch')
        if allowed:
            child_domains = domains[:]
            child_domains[v] = 1 << colour
            check_tree(children[colour], child_domains, adjacency, counts)


def verify(path: Path) -> dict[str, int | str]:
    require(__debug__, 'run without -O or -OO')
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    data = json.loads(raw.decode('utf-8'))
    require(data['schema'] == 'salem-sextic-four-v1', 'unknown certificate schema')
    require(data['polynomial'] == [1, 0, -1, -1, -1, 0, 1], 'wrong field polynomial')
    pts = data['points']
    require(type(pts) is list and len(pts) == 114, 'expected 114 vertices')
    require(all(type(p) is list and len(p) == 6 and all(integer(x) for x in p)
                for p in pts), 'coordinates must be integer sextuples')
    require(len({tuple(p) for p in pts}) == len(pts), 'duplicate vertex')
    n = len(pts)
    edges = [[u, v] for u in range(n) for v in range(u+1, n)
             if unit_difference(pts[u], pts[v])]
    require(len(edges) == 267, 'unexpected unit-edge count')
    require(data['edges'] == edges, 'edge list is not the full induced unit graph')
    adjacency: list[set[int]] = [set() for _ in pts]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    require(all(not (adjacency[u] & adjacency[v]) for u, v in edges), 'triangle found')
    four = data['colors4']
    require(type(four) is str and len(four) == n and set(four) <= set('0123'),
            'invalid four-colour word')
    require(all(four[u] != four[v] for u, v in edges), 'four-colouring has a bad edge')
    anchor = data['anchor']
    require(type(anchor) is list and len(anchor) == 2 and
            all(integer(v) and 0 <= v < n for v in anchor), 'invalid palette anchor')
    u, v = anchor
    require(v in adjacency[u], 'palette anchor is not an edge')
    domains = [7]*n
    domains[u], domains[v] = 1, 2
    counts = {'nodes': 0, 'branches': 0, 'leaves': 0}
    check_tree(data['non3_tree'], domains, adjacency, counts)
    deletion_words = data['vertex_deletion_colors3']
    require(type(deletion_words) is list and len(deletion_words) == n,
            'one colouring for each vertex deletion is required')
    for deleted, word in enumerate(deletion_words):
        require(type(word) is str and len(word) == n and word[deleted] == '-',
                'invalid deletion word')
        require(all(c in '012' for i, c in enumerate(word) if i != deleted),
                'invalid deletion colour')
        require(all(word[a] != word[b] for a, b in edges if deleted not in (a, b)),
                'vertex-deletion colouring has a bad edge')
    return {'status': 'PASS', 'vertices': n, 'unit_edges': len(edges),
            'exact_pairs': n*(n-1)//2, 'triangles': 0, 'chromatic_number': 4,
            'deletion_witnesses': n, **counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', nargs='?', type=Path,
                        default=ROOT/'certificates/salem_sextic_four.json.gz')
    args = parser.parse_args()
    try:
        result = verify(args.certificate)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as exc:
        raise SystemExit(f'FAIL: {exc}') from exc
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
