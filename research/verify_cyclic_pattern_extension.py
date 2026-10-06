"""T142/C025: exact fivefold orbit and a sharp 4/5 cyclic-extension cut.

No solver or producer is imported. Nine local pattern compatibilities, the
order-five physical rotation, all orbit points and all unit pairs are rebuilt.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice
from verify_motion_packet import read, require, pattern, BASE
from verify_localized_motion_packet import check as check_local, word_checks


def check(cert, local, local_raw, full_Y=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    require(cert['schema']=='cyclic-pattern-extension-v1' and cert['base_commit']==BASE,
            'cyclic provenance')
    require(cert['local_certificate_sha256']==hashlib.sha256(local_raw).hexdigest(), 'local certificate binding')
    require(cert['rotation_order']==5 and type(cert['rotation_order']) is int
            and cert['pattern_cycle_length']==3 and type(cert['pattern_cycle_length']) is int,
            'cyclic orders')
    # The full local checker is executed by this standalone entry's main and
    # the comprehensive test. Here we independently rebuild the orbit data.
    check_local(local)
    table = multiplication_twice()
    eta = tuple(int(i==16) for i in range(32))
    def mul(a,b):
        return tuple(Q(x)/2 for x in product_twice(a,b,table))
    point_layers = [[tuple(Q(x,local['coordinate_denominator']) for x in p) for p in local['points']]]
    for _ in range(4):
        point_layers.append([mul(eta,p) for p in point_layers[-1]])
    require([mul(eta,p) for p in point_layers[-1]]==point_layers[0], 'physical order-five identity')
    pts = sorted(set(p for layer in point_layers for p in layer))
    denominator = math.lcm(*(x.denominator for p in pts for x in p))
    points = [[int(x*denominator) for x in p] for p in pts]
    require(type(cert['coordinate_denominator']) is int and cert['coordinate_denominator']==denominator
            and cert['points']==points and all(type(x) is int for p in cert['points'] for x in p),
            'complete orbit coordinates')
    ids = {p:i for i,p in enumerate(pts)}
    copies = [[ids[p] for p in layer] for layer in point_layers]
    require(cert['copies']==copies and all(type(v) is int for row in cert['copies'] for v in row),
            'all five geometric copies')
    rotation = [ids[mul(eta,p)] for p in pts]
    require(sorted(rotation)==list(range(len(pts))), 'rotation permutation')
    edges = []
    target = [4*denominator*denominator]+[0]*31
    for a,b in combinations(range(len(pts)),2):
        delta = [x-y for x,y in zip(points[a],points[b])]
        if product_twice(delta,conjugate_twice(delta),table)==target:
            edges.append([a,b])
    require(cert['edges']==edges and all(type(v) is int for e in cert['edges'] for v in e), 'all orbit unit edges')
    patterns = local['three_word_extreme_law']['words']
    reference = [pattern(w,range(29)) for w in patterns]
    mm = local['mappings'][2]
    a = [pattern(w,[u for u,v in mm]) for w in patterns]
    b = [pattern(w,[v for u,v in mm]) for w in patterns]
    # Successor refers to physical samples c(eta^r x): image at r equals
    # source at r+1. This is the inverse of the support matching convention.
    compatible = [[int(b[i]==a[j]) for j in range(3)] for i in range(3)]
    require(all(sum(row)==1 for row in compatible) and
            all(sum(compatible[i][j] for i in range(3))==1 for j in range(3)) and
            all(compatible[i][i]==0 for i in range(3)), 'exact pattern three-cycle')
    cycles = sum(all(compatible[s[r]][s[(r+1)%5]] for r in range(5))
                 for s in product(range(3),repeat=5))
    require(cycles==0, 'closed five-walk in the pattern compatibility graph')
    w = cert['proper_five_coloring']
    word_checks(w,dict(points=points,edges=edges),5)
    hits = [pattern(w,copy) in reference for copy in copies]
    require(type(cert['expected_hits']) is int and sum(hits)==cert['expected_hits']==4
            and cert['bound']=='4/5', 'sharp cyclic probability bound')
    # Average the five exact rotations; actual edges remain edges and the
    # averaging distribution is invariant under their cyclic reindexing.
    orbit_words = []
    current = list(range(len(points)))
    for _ in range(5):
        orbit_words.append(''.join(w[v] for v in current))
        current = [rotation[v] for v in current]
    require(current==list(range(len(points))), 'orbit closes after five')
    for word in orbit_words:
        word_checks(word,dict(points=points,edges=edges),5)
    require(sum(pattern(word,copies[0]) in reference for word in orbit_words)==4,
            'orbit averaged event mass')
    inside = None
    if full_Y is not None:
        yids = {tuple(Q(x,full_Y['denominator']) for x in p):i for i,p in enumerate(full_Y['points'])}
        back = [yids.get(p) for p in pts]
        require(cert['vertices_in_Y_or_null']==back, 'orbit/Y intersection')
        inside = sum(x is not None for x in back)
    return dict(status='PASS',vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,
        induced_edges=len(edges),coordinate_denominator=denominator,rotation_order=5,
        pattern_cycle_length=3,compatibility_matrix=compatible,checked_label_cycles=3**5,
        admissible_five_label_cycles=0,maximum_membership_hits=4,sharp_invariant_mass='4/5',
        proper_five_edge_checks=5*len(edges),orbit_points_in_Y=inside,
        local_three_atom_mass=1,local_extreme_law_has_no_cyclic_extension=True,
        scope='Sharp inequality for the explicit 86-point geometric order-five extension. '
              'The local 29-point three-atom law is a valid full15 law but does not extend to '
              'an eta-invariant law on this orbit. Does not decide the full-Y15 problem.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root = Path(__file__).resolve().parents[1]
    path = root/'certificates/localized_motion_packet.json'
    local = read(path)
    cert = read(root/'certificates/cyclic_pattern_extension.json')
    print(json.dumps(check(cert,local,path.read_bytes()),indent=2))


if __name__=='__main__':
    main()
