"""Reconstruct a small exact Moser NAE-pair gate, not the historical 28-point orbit module."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
from exact_geometry import field, ZERO, ONE, add, mul, cmul, induced_edges


def build():
    a, b, tip = (field(0, F(1, 2)), field(F(1, 2))), (field(0, F(1, 2)), field(F(-1, 2))), (field(0, 1), ZERO)
    rotation = field(F(5, 6)), field(0, 0, F(1, 6))
    points = [(ZERO, ZERO), a, b, tip] + [cmul(rotation, p) for p in (a, b, tip)]
    spindle = induced_edges(points)
    edges = set(spindle)
    parameters = []
    for i in range(7):
        for t in range(2, 200):
            rot = field(F(1-t*t, 1+t*t)), field(F(2*t, 1+t*t))
            vectors = [cmul(rot, (field(0, F(1, 2)), field(sign*F(1, 2)))) for sign in (1, -1)]
            new = [(add(points[i][0], dx), add(points[i][1], dy)) for dx, dy in vectors]
            candidate = points + new
            if len(set(candidate)) != len(candidate):
                continue
            j = len(points)
            expected = edges | {(i, j), (i, j+1), (j, j+1)}
            if set(induced_edges(candidate)) == expected:
                points = candidate
                edges = expected
                parameters.append(t)
                break
        else:
            raise RuntimeError('No clean pose found')
    # A direct four-coloring: small exhaustive search on only the spindle.
    from itertools import product
    word = next(list(w) for w in product(range(4), repeat=7)
                if all(w[a] != w[b] for a, b in spindle))
    for i in range(7):
        available = [c for c in range(4) if c != word[i]]
        word.extend(available[:2])
    assert all(word[a] != word[b] for a, b in edges)
    return dict(schema=1, radicals=[1, 3, 11, 33],
                points=[[[str(x) for x in axis] for axis in p] for p in points],
                induced_edges=sorted(edges), four_coloring=word,
                boundary_pairs=[[7+2*i, 8+2*i] for i in range(7)],
                rational_rotation_parameters=parameters,
                scope='21-point unit-edge pair gate; not historical 28-point anchored Galois module')


if __name__ == '__main__':
    data = build()
    target = Path(__file__).resolve().parents[1]/'certificates/spindle_pair_gate.json'
    target.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(vertices=len(data['points']), edges=len(data['induced_edges']),
                         parameters=data['rational_rotation_parameters'])))
