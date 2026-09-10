"""Independent E046 bridge, all-unit-pair and full-copy-law checker."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
from verify_quintic_core_probe import (
    geometry, multiplication_twice, product_twice, conjugate_twice, filter_map, digest)


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    data = json.loads((certificate or root/'certificates/quintic_anchor_bridge.json').read_text())
    assert data['schema'] == 1 and data['experiment'] == 'E046'
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == data['core_sha256']
    assert hashlib.sha256((root/'certificates/quintic_core_probe.json').read_bytes()).hexdigest() == data['source_sha256']
    core = json.loads(raw)
    assert core['coordinate_denominator'] == 96
    assert data['source_anchors'] == [332,451] and data['target_anchors'] == [84,337]
    table = multiplication_twice()
    old,copies,owners,old_edges,_,_,_ = geometry(core,[0,153,150],table)
    def subtract(a,b):
        return tuple(x-y for x,y in zip(a,b))
    def multiply(a,b):
        return tuple(Q(x,2) for x in product_twice(a,b,table))
    def conjugate(a):
        return tuple(Q(x,2) for x in conjugate_twice(a))
    base = [tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    old_q = [tuple(Q(x,96) for x in point) for point in old]
    a,b = old_q[84],old_q[337]
    u,v = base[332],base[451]
    inverse = (Q(3,2),Q(0),Q(0),Q(0),Q(3,10))+(Q(0),)*27
    norm_vu = multiply(subtract(v,u),conjugate(subtract(v,u)))
    one = (Q(1),)+(Q(0),)*31
    assert multiply(norm_vu,inverse) == one
    rotation = multiply(multiply(subtract(b,a),conjugate(subtract(v,u))),inverse)
    assert multiply(rotation,conjugate(rotation)) == one
    bridge = [tuple(x+y for x,y in zip(a,multiply(rotation,subtract(w,u)))) for w in base]
    assert bridge[332] == a and bridge[451] == b
    assert set(bridge)&set(old_q) == {a,b}
    denominator = data['coordinate_denominator']
    assert denominator == 1440
    def integer(point):
        values = [x*denominator for x in point]
        assert all(x.denominator == 1 for x in values)
        return tuple(int(x) for x in values)
    points = sorted({integer(point) for point in old_q+bridge})
    index = {point:i for i,point in enumerate(points)}
    old_ids = [index[integer(point)] for point in old_q]
    bridge_ids = [index[integer(point)] for point in bridge]
    prime,images,bars = filter_map(table)
    assert denominator % prime
    residues = [(sum(x*y for x,y in zip(point,images)) % prime,
                 sum(x*y for x,y in zip(point,bars)) % prime) for point in points]
    edges = []
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-denominator**2) % prime:
            continue
        delta = subtract(points[i],points[j])
        if product_twice(delta,conjugate_twice(delta),table) == [4*denominator**2]+[0]*31:
            edges.append((i,j))
    inherited = {tuple(sorted((old_ids[i],old_ids[j]))) for i,j in old_edges}
    inherited.update(tuple(sorted((bridge_ids[i],bridge_ids[j]))) for i,j in core['induced_edges'])
    assert set(edges) == inherited
    summary = dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,
                   induced_edges=len(edges),inherited_edges=len(inherited),extra_bridge_edges=0,
                   overlap=2,point_sha256=digest(points),edge_sha256=digest(edges))
    assert data['geometry'] == summary
    assert (len(points),len(edges)) == (2540,12611)
    assert data['search']['status'] == 'SAT'
    for word in (data['search']['five_coloring'],data['repair']['five_coloring']):
        assert isinstance(word,str) and len(word) == len(points) and set(word) == set('01234')
        assert all(word[i] != word[j] for i,j in edges)
    repair_raw = (root/'certificates/quintic_congruence_gap.json').read_bytes()
    assert hashlib.sha256(repair_raw).hexdigest() == data['repair']['source_sha256']
    prior = json.loads(repair_raw)
    core_word = prior['repairing_core_word']
    palette = data['repair']['bridge_palette']
    assert sorted(palette) == list(range(5))
    word = data['repair']['five_coloring']
    assert core_word[332] == core_word[451]
    for i,owner in enumerate(owners):
        assert len(set(owner.values())) == 1
        assert word[old_ids[i]] == core_word[next(iter(owner.values()))]
    for j,i in enumerate(bridge_ids):
        assert int(word[i]) == palette[int(core_word[j])]
    # Recheck all seven E045 two-point partitions on this larger word.
    tests = [prior['first_congruence']]+[[r['pair'],r['collapsed_pair']] for r in prior['fiber_congruences']]
    assert len(tests) == 7
    for (a,b),(u,v) in tests:
        assert (word[old_ids[a]] == word[old_ids[b]]) == (word[old_ids[u]] == word[old_ids[v]])
    return dict(status='PASS',experiment='E046',**summary,colors=5,
                complete_copy_laws=5,retained_two_point_laws=7,
                scope='Two-vertex amalgamation; selected full-copy laws only, not all partial congruences')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
