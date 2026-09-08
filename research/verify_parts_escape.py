"""Independent all-cross-pair geometry for four escaped-field core doubles.

Unlike search, constructs rotated coordinates in a 16-dimensional multiquadratic
basis and squares every cross displacement. No collinearity pruning is used.
Within each copy, all unit edges follow from the verified core and an exactly
orthogonal rotation. This checks every pair in the induced union.
"""
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from verify_parts_core import RADICANDS, verify_geometry


def verify(root, geometry=None):
    core, base_edges = geometry or verify_geometry(root/'certificates/parts509_core.json')
    data = json.loads((root/'certificates/parts509_escape_rotations.json').read_text())
    expected = {7: (13, 22, 5, 3), 13: (5, 8, 3, 1),
                17: (7, 10, 3, 1), 41: (19, 22, 3, 1)}
    assert len(data['cases']) == 4 and {c['radicand'] for c in data['cases']} == set(expected)
    results = []
    for record in data['cases']:
        d = record['radicand']; num, denom, inside, factor = expected[d]
        assert record['cosine'] == [num, denom]
        assert 2*num % denom != 0  # T031's non-root-of-unity criterion.
        assert num*num + d*inside*factor*factor == denom*denom
        assert pow(d % 11, 5, 11) == 10
        rad = RADICANDS + tuple(d*r for r in RADICANDS)
        assert len(set(rad)) == 16
        products = {}
        for i, j in combinations(range(16), 2):
            g = math.gcd(rad[i], rad[j])
            products[i, j] = (rad.index(rad[i]*rad[j]//(g*g)), 2*g)
        def unit(p, q):
            squared = [0]*16
            for pa, qa in zip(p, q):
                delta = [a-b for a, b in zip(pa, qa)]
                squared[0] += sum(a*a*r for a, r in zip(delta, rad))
                nz = [i for i, a in enumerate(delta) if a]
                for i, j in combinations(nz, 2):
                    k, f = products[i, j]
                    squared[k] += f*delta[i]*delta[j]
            return squared == [(core['coordinate_denominator']*denom)**2]+[0]*15
        old = [tuple(tuple(denom*a for a in axis)+(0,)*8 for axis in p) for p in core['points']]
        rotated = []
        for x, y in core['points']:
            nx = [num*a for a in x]+[0]*8
            ny = [num*a for a in y]+[0]*8
            for i, r in enumerate(RADICANDS):
                g = math.gcd(inside, r)
                j = rad.index(inside*r*d//(g*g))
                nx[j] -= factor*g*y[i]
                ny[j] += factor*g*x[i]
            rotated.append((tuple(nx), tuple(ny)))
        assert len(set(old)) == len(set(rotated)) == 509
        assert set(old) & set(rotated) == {old[0]} and old[0] == rotated[0]
        cross = [(a, b) for a in range(1, 509) for b in range(1, 509) if unit(old[a], rotated[b])]
        assert cross == list(map(tuple, record['cross_edges']))
        assert max(Counter(a for a, b in cross).values()) == 1
        assert max(Counter(b for a, b in cross).values()) == 1
        other = lambda v: v+508 if v else 0
        edges = set(base_edges)
        edges.update(tuple(sorted((other(a), other(b)))) for a, b in base_edges)
        edges.update((a, other(b)) for a, b in cross)
        assert record['vertices'] == 1017 and record['induced_edges'] == len(edges)
        colors = record['five_coloring']
        assert len(colors) == 1017 and all(type(c) == int and 0 <= c < 5 for c in colors)
        assert all(colors[a] != colors[b] for a, b in edges)
        results.append(dict(radicand=d, vertices=1017, induced_edges=len(edges),
                            noncommon_cross_edges=len(cross), cross_pairs_checked=508**2,
                            chromatic_number=5))
        print(f'Independent escaped-field double verified: sqrt({d})', flush=True)
    return dict(status='VERIFIED_EXACT_FIVE_COLOR_ESCAPED_CORE_DOUBLES', cases=results,
                scope='Only these four finite graphs; extended infinite fields not classified')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
