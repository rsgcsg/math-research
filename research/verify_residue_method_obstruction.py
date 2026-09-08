"""Independent integer checks for residue exclusion and full conic edge lifting.

Does not import the exporter. Does NOT certify the general Weil bound by
sampling: that is an explicitly cited external theorem in the written proof.
"""
import json
from itertools import combinations, product
from pathlib import Path


def verify(root):
    data = json.loads((root/'certificates/residue_method_obstruction.json').read_text())
    assert data['schema'] == 1 and data['spectral_cutoff'] == 97
    # q^2-98q+1 is positive at 98 and strictly increasing on integers >=98.
    assert 98**2-98*98+1 == 1 and 2*98-97 > 0
    def factor(n):
        factors = []
        for d in range(2, n+1):
            while n % d == 0:
                factors.append(d)
                n //= d
        return factors
    expected = []
    for q in range(3, 98, 4):
        factors = factor(q)
        if len(set(factors)) == 1:
            p = factors[0]
            squares = {x*x % p for x in range(p)}
            missing = [d for d in (3, 5, 11) if d % p not in squares]
            expected.append(dict(q=q, p=p, exponent=len(factors),
                                 base_blocker=missing[0] if missing else None))
    assert data['small_anisotropic_orders'] == expected and len(expected) == 14
    assert [r['q'] for r in expected if r['base_blocker'] is None] == [11]
    assert all(r['p'] % 4 == 3 and r['exponent'] % 2 == 1 for r in expected)
    squares11 = {x*x % 11 for x in range(11)}
    assert data['escape_nonsquares_mod11'] == [7, 13, 17, 41]
    assert all(d % 11 not in squares11 for d in data['escape_nonsquares_mod11'])

    conics = []
    for case in data['conics']:
        p = case['p']
        assert p in (131, 491) and factor(p) == [p] and p % 4 == 3
        assert set(case['roots']) == {'3', '5', '11', '13'}
        assert all(0 <= x < p and x*x % p == int(d) for d, x in case['roots'].items())
        actual = {(x, y) for x in range(p) for y in range(p) if (x*x+y*y) % p == 1}
        images = []
        params = case['homogeneous_parameters']
        assert len(params) == p+1
        for a, b in params:
            den = (a*a+b*b) % p
            assert den
            inv = pow(den, -1, p)
            images.append(((a*a-b*b)*inv % p, 2*a*b*inv % p))
        assert len(set(images)) == len(images) == len(actual) == p+1
        assert set(images) == actual
        conics.append((p, params, images))
    assert [c[0] for c in conics] == [131, 491]

    # Every pair of directions, including both exceptional affine-chart cases,
    # lifts simultaneously to ONE rational unit vector by integer CRT.
    p, params_p, images_p = conics[0]
    q, params_q, images_q = conics[1]
    def crt(a, b):
        return a+p*((b-a)*pow(p, -1, q) % q)
    lift_count = 0
    for ((a0,b0),(x0,y0)), ((a1,b1),(x1,y1)) in product(zip(params_p,images_p), zip(params_q,images_q)):
        a, b = crt(a0,a1), crt(b0,b1)
        X, Y, D = a*a-b*b, 2*a*b, a*a+b*b
        assert D > 0 and X*X+Y*Y == D*D
        for modulus, target in ((p,(x0,y0)),(q,(x1,y1))):
            assert D % modulus
            assert (X*pow(D,-1,modulus) % modulus, Y*pow(D,-1,modulus) % modulus) == target
        lift_count += 1
    assert lift_count == 64944

    # Exact cyclotomic coefficient calibration of the Fourier/Kloosterman
    # identity for all nonzero frequencies, not floating-point eigenvalues.
    frequencies = 0
    for p in (11, 131):
        circle = [(x,y) for x in range(p) for y in range(p) if (x*x+y*y) % p == 1]
        assert len(circle) == p+1
        kl = {}
        for n in range(1, p):
            counts = [0]*p
            for t in range(1, p):
                counts[(-t-n*pow(4*t,-1,p)) % p] += 1
            kl[n] = counts
        for a,b in product(range(p), repeat=2):
            if a == b == 0:
                continue
            n = (a*a+b*b) % p
            assert n
            counts = [0]*p
            for x,y in circle:
                counts[(a*x+b*y) % p] += 1
            assert all(c+k == 2 for c,k in zip(counts, kl[n]))
            frequencies += 1
    assert frequencies == 17280

    # Palette split used in the framework audit: every 4-subset of six colors
    # hits BOTH sides of every 3+3 split, irrespective of the graph size.
    palette_checks = 0
    for left in combinations(range(6), 3):
        left = set(left)
        right = set(range(6))-left
        for allowed in combinations(range(6), 4):
            assert left.intersection(allowed) and right.intersection(allowed)
            palette_checks += 1
    assert palette_checks == 300
    return dict(status='VERIFIED_RESIDUE_METHOD_OBSTRUCTION_CALIBRATION',
                small_orders=len(expected), sole_small_base_residue=11,
                excluded_quadratic_extensions=4, conic_points=624,
                simultaneous_rational_edge_lifts=lift_count,
                exact_fourier_frequencies=frequencies, palette_split_checks=palette_checks,
                scope='T053/T054 need written spectral, number-field CRT and edge-surjectivity proofs; no HN bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
