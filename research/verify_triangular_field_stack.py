"""Independent exhaustive finite targets and all-pairs radical geometry.

No generator or solver is imported. The infinite lift needs the written proof.
"""
from itertools import combinations, product
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math


def verify_finite(root, case):
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == case['core_sha256']
    core = json.loads(raw)
    shell = case['shell']
    assert shell in (1, 3)
    assert case['alpha'] == ('2sqrt(2)/3' if shell == 1 else '2sqrt(6)/9')
    assert case['core_rotation'] == ('quarter_turn' if shell == 1 else 'identity')
    centers = [list(z) for z in product(range(-1, 2), repeat=2)
               if max(abs(z[0]), abs(z[1]), abs(z[0]+z[1])) <= 1]
    assert case['centers'] == centers
    radical = (1, 3, 11, 33, 5, 15, 55, 165, 2, 6, 22, 66, 10, 30, 110, 330)
    points = []
    for m, n in centers:
        for x, y in core['points']:
            a, b = [[3*z for z in ax]+[0]*8 for ax in (x, y)]
            if shell == 1:
                a, b = [-z for z in b], a
                a[8], b[9] = 192*m+96*n, 96*n
            else:
                a[9], b[8] = 64*m+32*n, 96*n
            points.append((tuple(a), tuple(b)))
    assert len(points) == len(set(points)) == case['vertices'] == 3563
    # A verified ring homomorphism is used only to reject impossible pairs.
    prime = 1000
    while True:
        prime += 1
        if any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)):
            continue
        roots = {a*a % prime: a for a in range(prime)}
        if all(r in roots for r in (2, 3, 5, 11)):
            break
    images = []
    for r in radical:
        z = 1
        for factor in (2, 3, 5, 11):
            if r % factor == 0:
                z = z*roots[factor] % prime
        images.append(z)
    products = {}
    for i, r in enumerate(radical):
        for j, s in enumerate(radical):
            g = math.gcd(r, s)
            k = radical.index(r*s//(g*g))
            products[i, j] = (k, g)
            assert images[i]*images[j] % prime == g*images[k] % prime
    projected = [tuple(sum(a*b for a, b in zip(ax, images)) % prime for ax in p) for p in points]
    colors = list(map(int, case['word']))
    assert len(colors) == len(points) and set(colors) <= set(range(5))
    edges = []
    interfaces = {}
    survivors = 0
    for i, j in combinations(range(len(points)), 2):
        if sum((a-b)**2 for a, b in zip(projected[i], projected[j])) % prime != 288**2 % prime:
            continue
        survivors += 1
        norm = [0]*16
        for ax, bx in zip(points[i], points[j]):
            nz = [(k, a-b) for k, (a, b) in enumerate(zip(ax, bx)) if a != b]
            for k, a in nz:
                for l, b in nz:
                    r, g = products[k, l]
                    norm[r] += a*b*g
        if norm != [288**2]+[0]*15:
            continue
        assert colors[i] != colors[j]
        edges.append((i, j))
        if i//509 != j//509:
            key = (i//509, j//509)
            interfaces[key] = interfaces.get(key, 0)+1
    expected = []
    for i, j in combinations(range(len(centers)), 2):
        dm, dn = (b-a for a, b in zip(centers[i], centers[j]))
        if dm*dm+dm*dn+dn*dn == shell:
            expected.append([i, j, interfaces.pop((i, j), 0)])
    assert not interfaces and expected == case['interfaces']
    assert len(edges) == case['edges']
    assert hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest() == case['edge_sha256']
    return dict(shell=shell, vertices=len(points), edges=len(edges),
                all_pairs_checked=len(points)*(len(points)-1)//2,
                radical_candidates=survivors, cross_edges=sum(t[2] for t in expected))


def verify(root, data_override=None):
    data = data_override if data_override is not None else json.loads((root/'certificates/triangular_field_stack.json').read_text())
    assert data['schema'] == 1 and data['prime'] == 11 and data['status'] == 'SAT_CANDIDATE'
    colors = list(map(int, data['word']))
    assert len(colors) == 121 and set(colors) <= set(range(5))
    vertices = list(product(range(11), repeat=2))
    extra = {(1, 3), (3, 1), (4, 4), (7, 7), (8, 10), (10, 8)}
    steps = {(a, b) for a, b in vertices if (a*a+b*b) % 11 == 1} | extra
    assert data['target_generators'] == [list(z) for z in sorted(steps)]
    assert len(steps) == 18 and (0, 0) not in steps
    edges = 0
    for i, j in combinations(range(121), 2):
        z = tuple((a-b) % 11 for a, b in zip(vertices[i], vertices[j]))
        if z in steps:
            assert colors[i] != colors[j]
            edges += 1
    assert edges == data['target_edges'] == 1089
    # All six geometric direction labels are kept distinct from color labels.
    directions = [(m, n) for m, n in product(range(-2, 3), repeat=2) if m*m+m*n+n*n == 1]
    assert len(directions) == 6
    assert [c['residue'] for c in data['shears']] == list(range(11))
    transport_checks = 0
    for case in data['shears']:
        r = case['residue']
        a, b, c, d = case['matrix']
        assert all(isinstance(z, int) and 0 <= z < 11 for z in (a, b, c, d))
        for m, n in directions:
            # e=(m+n/2,sqrt(3)n/2), J e=(-sqrt(3)n/2,m+n/2).
            for sign in (-1, 1):
                z = ((a*m+b*n-sign*r*5*n*6) % 11,
                     (c*m+d*n+sign*r*(2*m+n)*6) % 11)
                assert z in steps
                transport_checks += 1
    squares = {z*z % 11 for z in range(11)}
    nonsquares = set(range(11))-squares
    assert nonsquares == {2, 6, 7, 8, 10}
    allowed = {str(b): [n for n in (1, 3) if (1-n*b) % 11 in squares] for b in sorted(nonsquares)}
    assert allowed == data['nonsquare_shells'] == {'2': [], '6': [3], '7': [1], '8': [1], '10': [3]}
    # The written identity bounds all omitted integer lattice vectors.
    short = [(m, n) for m, n in product(range(-3, 4), repeat=2) if 0 < m*m+m*n+n*n < 4]
    assert len(short) == 12 and {m*m+m*n+n*n for m, n in short} == {1, 3}
    decomposition_checks = 0
    for m, n in product(range(-10, 11), repeat=2):
        c = (m-n) % 3
        a, b = (2*(m-c)+n)//3, (n-m+c)//3
        assert (m, n) == (c+a-b, a+2*b)
        decomposition_checks += 1
    assert [p['shell'] for p in data['finite_probes']] == [1, 3]
    boundary = data['mixed_shell_boundary']
    beta, t3, t4 = (Fraction(*boundary[k]) for k in ('beta', 't3', 't4'))
    assert beta == Fraction(120, 529) and Fraction(1, 7) < beta < Fraction(1, 4)
    assert t3*t3 == 1-3*beta and t4*t4 == 1-4*beta
    assert 1-beta == Fraction(409, 529)
    assert all(409 % p for p in range(2, math.isqrt(409)+1))
    assert 409 not in {1, 3, 5, 11, 15, 33, 55, 165}  # K's rational square-root classes.
    safe = {z for z in vertices if all(colors[11*x+y] != colors[11*((x+z[0]) % 11)+(y+z[1]) % 11]
                                     for x, y in vertices)}
    assert safe == steps
    mixed_directions = [(m, n) for m, n in product(range(-3, 4), repeat=2)
                        if m*m+m*n+n*n in (3, 4)]
    assert len(mixed_directions) == 12
    residues = {3: (t3.numerator*pow(t3.denominator, -1, 11)*pow(5, -1, 11)) % 11,
                4: (t4.numerator*pow(t4.denominator, -1, 11)*pow(2, -1, 11)) % 11}
    rejected = 0
    for a, b, c, d in product(range(11), repeat=4):
        images = set()
        for m, n in mixed_directions:
            r = residues[m*m+m*n+n*n]
            for sign in (-1, 1):
                images.add(((a*m+b*n-sign*r*5*n*6) % 11,
                            (c*m+d*n+sign*r*(2*m+n)*6) % 11))
        assert not images <= safe
        rejected += 1
    assert boundary['accepted_matrices'] == [] and boundary['matrix_count'] == rejected == 14641
    probes = [verify_finite(root, p) for p in data['finite_probes']]
    return dict(status='PASS',target_vertices=121,target_edges=edges,
                target_pairs_checked=121*120//2, residue_direction_transports=transport_checks,
                center_coset_calibrations=decomposition_checks, nonsquare_shells=allowed,
                fixed_word_mixed_shell_shears_rejected=rejected,
                finite_probes=probes,
                scope='T064/T065 provide infinite completeness; no unrestricted extension-field or plane coloring')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
