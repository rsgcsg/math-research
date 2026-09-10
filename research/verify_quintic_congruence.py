"""Independent exact C017/T085/E045 verifier; no search or SAT imports.

Use the existing checker-side gcd/32-basis multiplication, not the producer's
separated norm formula. Negative claims concern explicitly restricted laws.
"""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
from verify_quintic_core_probe import geometry, multiplication_twice, product_twice, conjugate_twice


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in mathematical verification')
    data = json.loads((certificate or root/'certificates/quintic_congruence_gap.json').read_text())
    assert data['schema'] == 1 and data['results'] == ['C017','T085','E045']
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == data['core_sha256']
    assert hashlib.sha256((root/'certificates/quintic_core_probe.json').read_bytes()).hexdigest() == data['source_sha256']
    core = json.loads(raw)
    assert core['coordinate_denominator'] == 96
    table = multiplication_twice()
    points, copies, owners, edges, summary, _, _ = geometry(core,[0,153,150],table)
    assert (len(points),len(edges)) == (2033,10169)
    assert all(len(set(owner.values())) == 1 for owner in owners)
    h = [next(iter(owner.values())) for owner in owners]
    base = [tuple(x+y+[0]*16) for x,y in core['points']]
    def norm(a,b):
        difference = tuple(x-y for x,y in zip(a,b))
        return tuple(Fraction(x,4*96**2) for x in
                     product_twice(difference,conjugate_twice(difference),table))
    def scalar(a,b=0):
        result = [Fraction(0)]*32
        result[0],result[4] = Fraction(a),Fraction(b)
        return tuple(result)
    pairs = data['first_congruence']
    assert pairs == [[0,337],[15,242]]
    assert [[h[a],h[b]] for a,b in pairs] == data['first_projected_pairs'] == [[322,64],[211,409]]
    common = scalar(Fraction(23,6),Fraction(-1,2))
    assert all(norm(points[a],points[b]) == common for a,b in pairs)
    assert norm(base[322],base[64]) == scalar(Fraction(4,3)) != common
    assert norm(base[211],base[409]) == common

    records = data['fiber_congruences']
    expected_pairs = [(332,451),(133,377),(379,129),(330,449),(447,328),(381,131)]
    assert len(records) == 6
    fiber_length = scalar(Fraction(5,6),Fraction(-1,6))
    for record, pair in zip(records,expected_pairs):
        a,b = record['pair']
        u,v = record['collapsed_pair']
        assert tuple(record['owners']) == pair == (h[a],h[b])
        assert record['collapsed_owners'] == [64,64] == [h[u],h[v]]
        assert norm(points[a],points[b]) == norm(points[u],points[v]) == fiber_length
        assert norm(base[h[u]],base[h[v]]) == scalar(0)
        assert norm(base[h[a]],base[h[b]]) == fiber_length

    # Exhaust all possible third-point images using distances to both anchors.
    # This differs from the rigid-motion formula used during exploration.
    # Only the two prescribed anchor pairs survive, in either orientation.
    assert data['fiber_anchor_candidates'] == [2]*6
    for record in records:
        a,b = record['collapsed_pair']
        u,v = record['pair']
        target_signatures = {}
        for j,p in enumerate(points):
            target_signatures.setdefault((norm(p,points[u]),norm(p,points[v])),[]).append(j)
        candidates = [(i,j) for i,p in enumerate(points)
                      for j in target_signatures.get((norm(p,points[a]),norm(p,points[b])),())]
        assert sorted(candidates) == sorted([(a,u),(b,v)])

    # Four real scalar residue maps: verify the complete basis multiplication
    # and the nonzero quadrances of the collapsed-fiber congruence.
    rad = (1,3,11,33,5,15,55,165)
    reductions = []
    for r3,r5 in product((5,6),(4,7)):
        images = (1,r3,0,0,r5,r3*r5 % 11,0,0)
        for i,j in product(range(8),repeat=2):
            import math
            g = math.gcd(rad[i],rad[j])
            k = rad.index(rad[i]*rad[j]//(g*g))
            assert images[i]*images[j] % 11 == g*images[k] % 11
        reduced = [tuple(sum(a*b for a,b in zip(axis,images))*pow(96,-1,11) % 11
                         for axis in p) for p in core['points']]
        q = sum((x-y)**2 for x,y in zip(reduced[332],reduced[451])) % 11
        assert q == (2 if r5 == 4 else 7)
        assert q == (5-r5)*pow(6,-1,11) % 11
        reductions.append((r3,r5,q))

    plane = list(product(range(11),repeat=2))
    def quadrance(a,b):
        return sum((x-y)**2 for x,y in zip(a,b)) % 11
    matrices = [(a,-s*b % 11,b,s*a % 11)
                for a,b in plane if (a*a+b*b)%11 == 1 for s in (-1,1)]
    assert len(set(matrices)) == 24
    for a,b,c,d in matrices:
        assert (a*a+c*c)%11 == (b*b+d*d)%11 == 1 and (a*b+c*d)%11 == 0
    walk_lengths = {}
    for q in (2,7):
        walk = data['quadrance_walks'][str(q)]
        assert walk[0] == [0,0] and walk[-1] == [1,0]
        assert all(quadrance(a,b) == q for a,b in zip(walk,walk[1:]))
        assert len(walk)-1 == (3 if q == 2 else 2)
        # Check ordered-pair transitivity, the hypothesis making all walk-edge
        # equality probabilities the same. No coloring enumeration is assumed.
        vx,vy = walk[1]
        orbit = {(u,v,(u+a*vx+b*vy)%11,(v+c*vx+d*vy)%11)
                 for a,b,c,d in matrices for u,v in plane}
        all_pairs = {(x,y,u,v) for x,y in plane for u,v in plane if quadrance((x,y),(u,v)) == q}
        assert orbit == all_pairs and len(orbit) == 1452
        walk_lengths[q] = len(walk)-1

    # E045: a genuinely proper whole induced-graph coloring. Averaging only
    # its global color names satisfies the seven selected FULL two-point laws.
    word = data['repairing_core_word']
    assert isinstance(word,str) and len(word) == 509 and set(word) == set('01234')
    assert all(word[a] != word[b] for a,b in core['induced_edges'])
    assert all(word[a] == word[b] for a,b in expected_pairs)
    pulled = [word[i] for i in h]
    assert all(pulled[a] != pulled[b] for a,b in edges)
    tests = [pairs]+[[r['pair'],r['collapsed_pair']] for r in records]
    assert all((pulled[a] == pulled[b]) == (pulled[u] == pulled[v])
               for (a,b),(u,v) in tests)
    return dict(status='PASS',counterexample='C017',restricted_law_theorem='T085',experiment='E045',
                actual_vertices=len(points),actual_pairs=summary['actual_pairs'],induced_edges=len(edges),
                congruences_checked=len(tests),residue_maps=reductions,
                maximal_fiber_congruence_sizes=data['fiber_anchor_candidates'],
                quadrance_walk_lengths=walk_lengths,minimum_restricted_law_defect='1/3',
                repaired_core_colors=5,scope='No full joint feasibility or HN lower bound claim; see written proof')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],args.certificate),indent=2))
