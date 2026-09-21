#!/usr/bin/env python3
"""Rebuild the frozen E095 witness, including a complete non-3 proof tree.

The 114 retained indices were discovered by exploratory vertex deletion in
an 830-point binary-sum set. They are seed data, not a minimum-size claim.
This producer uses sextic arithmetic and colour-labelled backtracking; the
independent checker uses cubic trace arithmetic and domain propagation.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = (1, 0, -1, -1, -1, 0, 1)
ONE = (1, 0, 0, 0, 0, 0)
INDICES = [3,7,11,15,23,24,25,26,38,42,43,69,76,83,85,111,112,114,122,126,
138,140,141,155,157,158,182,184,185,186,201,203,204,205,223,224,226,231,233,
304,315,317,319,320,332,333,335,347,348,350,355,374,386,387,389,398,419,426,
447,449,450,452,466,482,491,497,500,503,521,579,581,583,585,587,589,591,615,
619,648,651,655,657,659,674,688,691,692,699,715,728,730,736,746,747,754,756,
761,763,765,767,784,790,791,793,794,797,798,806,807,814,820,821,823,825]


def multiply(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    c = [0]*11
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] += x*y
    for j in range(10, 5, -1):
        for k in range(6):
            c[j-6+k] -= c[j]*P[k]
    return tuple(c[:6])


def build() -> dict[str, object]:
    a = (0, 1, 0, 0, 0, 0)
    inverse = (0, 1, 1, 1, 0, -1)
    if multiply(a, inverse) != ONE:
        raise RuntimeError('bad inverse formula')
    conjugate_powers = [ONE]
    for _ in range(5):
        conjugate_powers.append(multiply(conjugate_powers[-1], inverse))
    def conjugate(x: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(sum(x[j]*conjugate_powers[j][k] for j in range(6))
                     for k in range(6))
    points = {(0,)*6}
    power = ONE
    for _ in range(10):
        points |= {tuple(x+y for x, y in zip(p, power)) for p in points}
        power = multiply(power, a)
    cube = sorted(points)
    if len(cube) != 830:
        raise RuntimeError('binary-sum seed changed')
    pts = [cube[i] for i in INDICES]
    n = len(pts)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            difference = tuple(x-y for x, y in zip(pts[u], pts[v]))
            if multiply(difference, conjugate(difference)) == ONE:
                edges.append([u, v])
    adjacency = [set() for _ in pts]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    def solve(colours: list[int], proof: bool = False):
        # -1 is undecided; -2 is a deleted vertex.
        while True:
            changed = False
            for v in range(n):
                if colours[v] != -1:
                    continue
                available = {0, 1, 2}-{colours[w] for w in adjacency[v] if colours[w] >= 0}
                if not available:
                    return None, -1
                if len(available) == 1:
                    colours[v] = available.pop()
                    changed = True
            if not changed:
                break
        undecided = [v for v in range(n) if colours[v] == -1]
        if not undecided:
            return colours, None
        v = max(undecided, key=lambda v: (
            len({colours[w] for w in adjacency[v] if colours[w] >= 0}),
            len(adjacency[v]), -v))
        available = sorted({0, 1, 2}-{colours[w] for w in adjacency[v] if colours[w] >= 0})
        children = [None]*3
        for colour in available:
            child = colours[:]
            child[v] = colour
            solution, subtree = solve(child, proof)
            if solution is not None:
                return solution, None
            if proof:
                children[colour] = subtree
        return None, [v, children]

    anchor = max(range(n), key=lambda v: len(adjacency[v]))
    neighbour = min(adjacency[anchor])
    colours = [-1]*n
    colours[anchor], colours[neighbour] = 0, 1
    solution, tree = solve(colours, True)
    if solution is not None:
        raise RuntimeError('seed graph is three-colourable')
    four = []
    for point in pts:
        colour = 0
        for coefficient, residue in zip(point, (1, 2, 3, 1, 2, 3)):
            if coefficient % 2:
                colour ^= residue
        four.append(str(colour))
    deletion_words = []
    for deleted in range(n):
        colours = [-1]*n
        colours[deleted] = -2
        u = next(v for v in range(n) if v != deleted and adjacency[v]-{deleted})
        v = min(adjacency[u]-{deleted})
        colours[u], colours[v] = 0, 1
        solution, _ = solve(colours)
        if solution is None:
            raise RuntimeError(f'vertex deletion {deleted} is still non-3')
        deletion_words.append(''.join('-' if c == -2 else str(c) for c in solution))
    return {'schema': 'salem-sextic-four-v1',
            'base_commit': 'efd931eeac7c04cff167eaca544cd96ab501b702',
            'polynomial': P, 'points': pts, 'edges': edges,
            'colors4': ''.join(four), 'anchor': [anchor, neighbour],
            'non3_tree': tree, 'vertex_deletion_colors3': deletion_words}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'certificates/salem_sextic_four.json.gz')
    args = parser.parse_args()
    raw = (json.dumps(build(), separators=(',', ':'), sort_keys=True)+'\n').encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(gzip.compress(raw, mtime=0) if args.output.suffix == '.gz' else raw)
    print(f'WROTE {args.output} ({len(raw)} uncompressed bytes)')


if __name__ == '__main__':
    main()
