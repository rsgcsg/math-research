"""Independent E047 exact six-bridge induced-graph certificate checker."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
from verify_quintic_bridge_contacts import context
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice,filter_map,digest


def verify(root,certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_bridge_family.json').read_text())
    assert data['schema']==1 and data['experiment']=='E047'
    assert set(data['sources'])=={'parts509_core.json','quintic_core_probe.json','quintic_congruence_gap.json'}
    for name,sha in data['sources'].items():
        assert hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()==sha
    pairs=[[332,451],[133,377],[379,129],[330,449],[447,328],[381,131]]
    assert data['source_anchors']==pairs and data['target_anchors']==[84,337]
    core,old,base,old_edges,records,r0,multiply,conjugate=context(root)
    a,b=old[84],old[337]
    inverse=(Q(3,2),Q(0),Q(0),Q(0),Q(3,10))+(Q(0),)*27
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    bridges=[]
    for ui,vi in pairs:
        u,v=base[ui],base[vi]
        r=multiply(multiply(sub(b,a),conjugate(sub(v,u))),inverse)
        assert multiply(r,conjugate(r))==(Q(1),)+(Q(0),)*31
        relative=multiply(conjugate(r0),r)
        assert not any(relative[16:])
        bridge=[tuple(x+y for x,y in zip(a,multiply(r,sub(w,u)))) for w in base]
        assert bridge[ui]==a and bridge[vi]==b
        assert set(bridge)&set(old)=={a,b}
        bridges.append(bridge)
    den=data['coordinate_denominator'];assert den==1440
    def integer(p):
        assert all((x*den).denominator==1 for x in p)
        return tuple(int(x*den) for x in p)
    points=sorted({integer(p) for p in old+[p for bridge in bridges for p in bridge]})
    index={p:i for i,p in enumerate(points)}
    old_ids=[index[integer(p)] for p in old]
    bridge_ids=[[index[integer(p)] for p in bridge] for bridge in bridges]
    table=multiplication_twice();prime,images,bars=filter_map(table)
    assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        delta=sub(points[i],points[j])
        if product_twice(delta,conjugate_twice(delta),table)==[4*den*den]+[0]*31:edges.append((i,j))
    old_set,bridge_set=set(old_ids),set().union(*map(set,bridge_ids))
    inherited={tuple(sorted((old_ids[i],old_ids[j]))) for i,j in old_edges}
    for copy in bridge_ids:
        inherited.update(tuple(sorted((copy[i],copy[j]))) for i,j in core['induced_edges'])
    assert inherited<=set(edges)
    cross=[e for e in edges if not(set(e)<=old_set or set(e)<=bridge_set)]
    summary=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,
                 induced_edges=len(edges),inherited_edges=len(inherited),extra_edges=len(set(edges)-inherited),
                 old_bridge_cross_edges=len(cross),bridge_union_vertices=len(bridge_set),
                 bridge_union_edges=sum(set(e)<=bridge_set for e in edges),old_bridge_overlap=len(old_set&bridge_set),
                 pair_overlaps=[[i,j,len(set(bridge_ids[i])&set(bridge_ids[j]))] for i,j in combinations(range(6),2)],
                 point_sha256=digest(points),edge_sha256=digest(edges))
    assert summary==data['geometry']
    assert (len(points),len(edges),len(cross))==(4125,20395,0)
    assert data['search']['status']=='SAT'
    word=data['search']['five_coloring']
    assert len(word)==len(points) and set(word)==set('01234')
    assert all(word[i]!=word[j] for i,j in edges)
    return dict(status='PASS',experiment='E047',**summary,chromatic_number=5,
                scope='Specified induced six-bridge graph; complete joint constraints not tested')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
