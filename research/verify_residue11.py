"""Standard-library check of a finite-field coloring and Parts509 pullbacks.

No SAT imports. Integer arithmetic checks all 726 finite edges, all 64 basis
products of each of the four reduction maps, and every actual core edge.
The infinite-field statement requires the valuation proof in docs/proofs.
"""
import json
import math
from itertools import combinations, product
from pathlib import Path
from verify_parts_core import RADICANDS, verify_geometry, verify_coloring


def verify(root, geometry=None):
    data = json.loads((root/'certificates/residue11_coloring.json').read_text())
    rows = data['rows']
    assert data['field_order'] == 11 and data['colors'] == 5
    assert len(rows) == 11 and all(len(r) == 11 for r in rows)
    colors = list(map(int, ''.join(rows)))
    assert set(colors) == set(range(5))
    points = list(product(range(11), repeat=2))
    edges = [(i, j) for i, j in combinations(range(121), 2)
             if sum((a-b)**2 for a, b in zip(points[i], points[j])) % 11 == 1]
    assert len(edges) == 726
    assert all(colors[i] != colors[j] for i, j in edges)
    squares = {x*x % 11 for x in range(11)}
    assert squares == {0, 1, 3, 4, 5, 9} and 10 not in squares
    assert all(x == y == 0 for x, y in points if (x*x+y*y) % 11 == 0)
    core, core_edges = geometry or verify_geometry(root/'certificates/parts509_core.json')
    den_inv = pow(core['coordinate_denominator'], -1, 11)
    pullbacks = []
    for r3, r5 in product((5, 6), (4, 7)):
        images = [1, r3, 0, 0, r5, r3*r5 % 11, 0, 0]
        for i, j in product(range(8), repeat=2):
            g = math.gcd(RADICANDS[i], RADICANDS[j])
            k = RADICANDS.index(RADICANDS[i]*RADICANDS[j]//(g*g))
            assert images[i]*images[j] % 11 == g*images[k] % 11
        reduced = [tuple(sum(a*b for a, b in zip(axis, images))*den_inv % 11
                         for axis in point) for point in core['points']]
        for a, b in core_edges:
            assert sum((x-y)**2 for x, y in zip(reduced[a], reduced[b])) % 11 == 1
        word = [colors[11*x+y] for x, y in reduced]
        verify_coloring(word, core_edges)
        pullbacks.append(dict(sqrt3=r3, sqrt5=r5, image_vertices=len(set(reduced))))
    # Repeated simple-root lifting is also independently calibrated. Existence
    # at every precision follows by the unique linear correction, not this cutoff.
    for d, a in ((3, 5), (5, 4)):
        modulus = 11
        for _ in range(8):
            correction = (-(a*a-d)//modulus)*pow(2*a, -1, 11) % 11
            a += correction*modulus
            modulus *= 11
            assert (a*a-d) % modulus == 0
    return dict(status='VERIFIED_FIVE_COLOR_RESIDUE_TARGET_AND_CORE_PULLBACKS',
                finite_vertices=121, finite_edges=len(edges), colors=5,
                reduction_maps=pullbacks, core_edge_checks=4*len(core_edges),
                infinite_scope='See residue_field_ceiling.md; not a coloring of R^2')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
