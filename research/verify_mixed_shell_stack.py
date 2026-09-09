"""Independent T067 finite targets, RUP refutation, and actual induced geometry.

No search or SAT code is imported. The infinite conclusion uses the proof.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

from verify_rup_lrat import check


def verify_finite(root, data):
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == data['core_sha256']
    den = data['denominator']
    assert den == 13248
    core = json.loads(raw)
    centers = [(m, n) for m, n in product(range(-1, 2), repeat=2)
               if m*m+m*n+n*n <= 1]
    assert list(map(list, centers)) == data['centers']
    base = {tuple(tuple(F(a, 96) for a in ax)+(F(0),)*8 for ax in p) for p in core['points']}
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            continue
        for sign in (-1, 1):
            x, y = [F(0)]*16, [F(0)]*16
            if norm == 3:
                x[0], y[1] = -sign*F(13*n, 46), sign*F(13*(2*m+n), 138)
            else:
                x[1], y[0] = -sign*F(7*n, 92), sign*F(7*(2*m+n), 92)
            base.add((tuple(x), tuple(y)))
    base = sorted(base)
    assert len(base) == data['labels_per_center']
    points = []
    for m, n in centers:
        for x, y in base:
            x, y = list(x), list(y)
            x[13] += F(2*m+n, 23)
            y[12] += F(3*n, 23)
            assert all((a*den).denominator == 1 for a in x+y)
            points.append(tuple(tuple(int(a*den) for a in ax) for ax in (x, y)))
    assert len(points) == len(set(points)) == data['vertices']
    rad = (1, 3, 11, 33, 5, 15, 55, 165, 2, 6, 22, 66, 10, 30, 110, 330)
    products = {}
    for i, r in enumerate(rad):
        for j, s in enumerate(rad):
            g = math.gcd(r, s)
            products[i, j] = rad.index(r*s//(g*g)), g
    prime = 1031
    assert all(prime % d for d in range(2, math.isqrt(prime)+1))
    roots = {a*a % prime: a for a in range(prime)}
    images = []
    for r in rad:
        z = 1
        for p in (2, 3, 5, 11):
            if r % p == 0:
                z = z*roots[p] % prime
        images.append(z)
    for (i, j), (k, g) in products.items():
        assert images[i]*images[j] % prime == g*images[k] % prime
    residues = [tuple(sum(a*b for a, b in zip(ax, images)) % prime for ax in p) for p in points]
    colors = list(map(int, data['word']))
    assert len(colors) == len(points) and set(colors) <= set(range(6))
    five_colors = list(map(int, data['five_word']))
    assert len(five_colors) == len(points) and set(five_colors) <= set(range(5))
    edges = []
    counts = {3: 0, 4: 0}
    candidates = 0
    for i, j in combinations(range(len(points)), 2):
        if sum((a-b)**2 for a, b in zip(residues[i], residues[j])) % prime != den*den % prime:
            continue
        candidates += 1
        squared = [0]*16
        for ax, bx in zip(points[i], points[j]):
            delta = [(k, a-b) for k, (a, b) in enumerate(zip(ax, bx)) if a != b]
            for k, a in delta:
                for l, b in delta:
                    r, g = products[k, l]
                    squared[r] += a*b*g
        if squared != [den*den]+[0]*15:
            continue
        assert colors[i] != colors[j]
        assert five_colors[i] != five_colors[j]
        edges.append((i, j))
        if i//len(base) != j//len(base):
            m, n = (b-a for a, b in zip(centers[i//len(base)], centers[j//len(base)]))
            norm = m*m+m*n+n*n
            assert norm in counts
            counts[norm] += 1
    assert len(edges) == data['edges']
    assert counts == {int(k): v for k, v in data['cross_edges_by_shell'].items()}
    assert all(counts.values())
    assert hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest() == data['edge_sha256']
    # Each translated full Parts core is present, not merely the extra contacts.
    assert len(core['points']) == 509 and len(base) >= 509
    return dict(vertices=len(points), edges=len(edges), cross_edges_by_shell=counts, five_coloring_verified=True,
                all_pairs_checked=len(points)*(len(points)-1)//2, radical_candidates=candidates)


def verify(root, data_override=None):
    data = data_override if data_override is not None else json.loads((root/'certificates/mixed_shell_stack.json').read_text())
    assert data['schema'] == 1 and data['beta'] == [120, 529] and data['matrix'] == [0, 1, 3, 2]
    beta = F(*data['beta'])
    assert F(1, 7) < beta < F(1, 4)
    assert F(13, 23)**2+3*beta == 1 and F(7, 23)**2+4*beta == 1
    vertices = list(product(range(11), repeat=2))
    unit = {p for p in vertices if sum(a*a for a in p) % 11 == 1}
    lifted = 0
    for x, y in unit:
        if (x, y) == (10, 0):
            a, b = F(-1), F(0)
        else:
            t = F(y*pow(x+1, -1, 11) % 11)
            a, b = (1-t*t)/(1+t*t), 2*t/(1+t*t)
        assert a*a+b*b == 1
        assert tuple(z.numerator*pow(z.denominator, -1, 11) % 11 for z in (a, b)) == (x, y)
        lifted += 1
    steps = set(unit)
    transports = 0
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            continue
        # Exact real coefficients reduce independently to these two residues.
        t = F(13, 23) if norm == 3 else F(7, 23)
        norm_root = 5 if norm == 3 else 2
        r = t.numerator*pow(t.denominator, -1, 11)*pow(norm_root, -1, 11) % 11
        for sign in (-1, 1):
            z = ((n-sign*r*5*n*6) % 11, (3*m+2*n+sign*r*(2*m+n)*6) % 11)
            steps.add(z)
            transports += 1
    assert transports == 24 and len(steps) == 24 and (0, 0) not in steps
    assert [list(z) for z in sorted(steps)] == data['generators']
    colors = list(map(int, data['word']))
    assert len(colors) == 121 and set(colors) == set(range(6))
    scalar_steps = {(x+y) % 11 for x, y in steps}
    assert scalar_steps == set(range(11))-{0, 4, 7}
    scalar_colors = list(map(int, data['scalar_word']))
    assert scalar_colors == [(3*z % 11)//2 for z in range(11)]
    assert colors == [scalar_colors[(x+y) % 11] for x, y in vertices]
    for x, y in combinations(range(11), 2):
        if (x-y) % 11 in scalar_steps:
            assert scalar_colors[x] != scalar_colors[y]
    assert all(any((x-y) % 11 in scalar_steps for x, y in combinations(triple, 2))
               for triple in combinations(range(11), 3))
    edges = []
    for i, j in combinations(range(121), 2):
        if tuple((a-b) % 11 for a, b in zip(vertices[i], vertices[j])) in steps:
            edges.append((i, j))
            assert colors[i] != colors[j]
    assert len(edges) == data['edges'] == 1452
    triangle = (0, 11, 74)
    assert all((i, j) in edges for i, j in combinations(triangle, 2))
    initial = [[5*v+c+1 for c in range(5)] for v in range(121)]
    initial += [[-5*v-a-1, -5*v-b-1] for v in range(121) for a, b in combinations(range(5), 2)]
    initial += [[-5*a-c-1, -5*b-c-1] for a, b in edges for c in range(5)]
    initial += [[5*v+c+1] for c, v in enumerate(triangle)]
    refutation = check(initial, data['five_color_lrat'])
    squares = {a*a % 11 for a in range(11)}
    allowed = {b: [n for n in (1, 3, 4) if (1-b*n) % 11 in squares] for b in range(11) if b not in squares}
    assert allowed == {2: [4], 6: [3], 7: [1], 8: [1], 10: [3, 4]}
    short = {m*m+m*n+n*n for m, n in product(range(-4, 5), repeat=2) if 0 < m*m+m*n+n*n < 7}
    assert short == {1, 3, 4}
    # This is a graph target lower bound only: there is no target-to-real embedding.
    return dict(status='PASS',scalar_target_vertices=11,scalar_target_chromatic_number=6,
                target_chromatic_number=6,target_vertices=121,target_edges=len(edges),
                exact_transports=transports,rational_unit_direction_lifts=lifted,five_color_refutation=refutation,
                allowed_shells=allowed,finite_probe=verify_finite(root,data['finite_probe']),
                scope='Real K^2+(2sqrt(30)/23)Lambda is between five and six; not certified six-chromatic')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
