"""Independent standard-library checks for the CM residue-29 review.

Reconstructs every pair, verifies optional positive words, and proves a
one-coordinate quotient ceiling by exhaustive five-set rejection.  UNKNOWN
search records are never consumed as mathematical negative certificates.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json


def verify(root):
    if not __debug__:
        raise RuntimeError('This checker requires assertions; do not use -O.')
    p = 29
    points = list(product(range(p), repeat=2))
    edges = [(i, j) for i, j in combinations(range(p*p), 2)
             if ((points[i][0]-points[j][0])**2
                 + 3*(points[i][1]-points[j][1])**2) % p == 1]
    assert len(edges) == 12615
    directions = [points[j] for i, j in edges if i == 0]
    assert len(directions) == 30
    assert all((-a % p, -b % p) in directions for a, b in directions)
    edge_sha = hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest()
    assert edge_sha == 'b353daf496b3cedada84119213a54df9b280eef56f80590a0374dd49e999f150'

    def mul(x, y):
        a, b = x
        c, d = y
        return ((a*c-3*b*d) % p, (a*d+b*c) % p)

    def power(x, n):
        result = (1, 0)
        while n:
            if n & 1:
                result = mul(result, x)
            x = mul(x, x)
            n >>= 1
        return result

    for a, b in points:
        assert power((a, b), p) == (a, -b % p)
        if a or b:
            assert power((a, b), p*p-1) == (1, 0)
    eta_roots = [x for x in points if x != (1, 0) and power(x, 5) == (1, 0)]
    assert len(eta_roots) == 4
    assert mul((0, 9), (0, 9)) == (-11 % p, 0)
    assert all(mul(x, (x[0], -x[1] % p)) == (1, 0) for x in eta_roots)
    z, nu = (14, 24), (25, 16)
    zz, nn = mul(z, z), mul(nu, nu)
    assert ((zz[0]+z[0]+pow(3, -1, p)) % p, (zz[1]+z[1]) % p) == (0, 0)
    assert ((nn[0]-5*pow(3, -1, p)*nu[0]+1) % p,
            (nn[1]-5*pow(3, -1, p)*nu[1]) % p) == (0, 0)

    prime_table = []
    for q in range(2, 98):
        if any(q % d == 0 for d in range(2, int(q**0.5)+1)):
            continue
        if q in (2, 3, 5, 11):
            continue  # The written decomposition proof treats these separately.
        roots = {x*x % q for x in range(q)}
        stable = q % 5 == 4 and (-3) % q not in roots and (-11) % q not in roots
        prime_table.append([q, stable, 2 % q in roots])
    assert [q for q, stable, _ in prime_table if stable] == [29]
    assert not [q for q, stable, two_square in prime_table if stable and two_square]

    # Every nonzero linear map F_29^2 -> F_29 is a nonzero scalar multiple
    # of one of these projective representatives. Scaling is a relabeling.
    projections = []
    for a, b in [(1, t) for t in range(p)]+[(0, 1)]:
        image = sorted({(a*x+b*y) % p for x, y in directions})
        if 0 in image:
            witness = next([x, y] for x, y in directions if (a*x+b*y) % p == 0)
            projections.append(dict(weight=[a, b], obstruction='loop', direction=witness))
            continue
        assert len(image) == 16
        forbidden = set(image)

        def independent(vertices):
            return all((v-u) % p not in forbidden for u, v in combinations(vertices, 2))

        # Translation moves any independent five-set so that it contains 0.
        # Thus this checks all five-sets up to a justified automorphism.
        tested = 0
        for rest in combinations(range(1, p), 4):
            assert not independent((0,)+rest)
            tested += 1
        witness = next((0,)+rest for rest in combinations(range(1, p), 3)
                       if independent((0,)+rest))
        assert tested == 20475
        projections.append(dict(weight=[a, b], obstruction='independence_bound',
                                alpha=4, lower_chromatic=8, independent_four=list(witness),
                                anchored_five_sets=tested))
    assert sum(x['obstruction'] == 'loop' for x in projections) == 15
    assert sum(x['obstruction'] == 'independence_bound' for x in projections) == 15

    searches = []
    for k in (6, 5):
        path = root/'certificates'/f'cofinal_residue29_k{k}_probe.json'
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        assert data['field_order'] == p and data['norm_form'] == [1, 3]
        assert data['vertices'] == p*p and data['edges'] == len(edges)
        assert data['edge_sha256'] == edge_sha
        assert data['directions'] == [list(x) for x in directions]
        record = data['result']
        assert record['k'] == k
        if record['status'] == 'SAT':
            word = record['coloring']
            assert len(word) == p*p
            assert all(type(c) is int and 0 <= c < k for c in word)
            assert all(word[i] != word[j] for i, j in edges)
            checked = 'POSITIVE_WORD_VERIFIED'
        else:
            assert record['status'] in ('UNKNOWN', 'UNSAT_SEARCH_ONLY')
            assert 'coloring' not in record
            checked = 'NO_NEGATIVE_CLAIM'
        searches.append(dict(k=k, reported_status=record['status'], checked=checked))
    return dict(status='FINITE_ARITHMETIC_AND_PROJECTION_CHECKS_PASS',
                vertices=p*p, pairs=p*p*(p*p-1)//2, edges=len(edges),
                edge_sha256=edge_sha, primitive_fifth_roots=eta_roots,
                stable_small_prime_table=prime_table, projections=projections,
                searches=searches,
                scope='No ordinary non-5 or non-6 witness; no global upper bound.')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
