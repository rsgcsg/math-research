"""Independent E053 full geometry, coloring, projection and identity audit."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice,filter_map,digest
from verify_quintic_bridge_contacts import km,divide


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_radial_escape.json').read_text())
    assert data['schema']==1 and data['experiment']=='E053'
    assert data['construction']=='P, 2c+P, rP, 2cr+rP; r from T087 and c=Re(r)'
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);assert core['coordinate_denominator']==96
    table=multiplication_twice();zero=(Q(0),)*32;one=(Q(1),)+zero[1:]
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    # Direct coefficients rather than the producer's conic construction.
    r=(Q(18,31),Q(0),Q(0),Q(0),Q(3,31))+zero[:11]+(Q(-49,62),Q(0),Q(0),Q(0),Q(-3,62))+zero[:11]
    assert len(r)==32 and mul(r,bar(r))==one
    two_c=add(r,bar(r));assert not any(two_c[8:])
    assert two_c[:8]==(Q(89,62),Q(0),Q(0),Q(0),Q(-11,62),Q(0),Q(0),Q(0))
    c=tuple(x/2 for x in two_c[:8]);b=r[16:24];m=km(two_c[:8],two_c[:8])
    D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    delta=divide(tuple(4*x-y for x,y in zip(m,km(m,m))),D)
    assert km(km(c,b),km(c,b))==delta and any(delta)
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    radii=set()
    for pivot in (0,64):
        for p in base:radii.add(mul(sub(p,base[pivot]),bar(sub(p,base[pivot])))[:8])
    assert m not in radii
    copies_q=[base,[add(two_c,p) for p in base],[mul(r,p) for p in base],
              [add(mul(r,two_c),mul(r,p)) for p in base]]
    den=data['coordinate_denominator'];assert type(den) is int and den>0
    def integer(p):
        assert all((x*den).denominator==1 for x in p)
        return tuple(int(x*den) for x in p)
    raw_copies=[[integer(p) for p in copy] for copy in copies_q]
    points=sorted({p for copy in raw_copies for p in copy});index={p:i for i,p in enumerate(points)}
    copies=[[index[p] for p in copy] for copy in raw_copies]
    prime,images,bars=filter_map(table);assert den%prime
    projected=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for i,j in combinations(range(len(points)),2):
        if ((projected[i][0]-projected[j][0])*(projected[i][1]-projected[j][1])-den*den)%prime:continue
        d=sub(points[i],points[j])
        if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
    internal={tuple(sorted((copy[i],copy[j]))) for copy in copies for i,j in core['induced_edges']}
    first=set(copies[0]+copies[1]);second=set(copies[2]+copies[3])
    extra=set(edges)-internal
    expected={tuple(sorted((copies[1][0],copies[2][153]))),tuple(sorted((copies[0][153],copies[3][0])))}
    assert extra==expected and first&second=={copies[0][0]}=={copies[2][0]}
    summary=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,induced_edges=len(edges),
                 copy_edges=len(internal),extra_edges=len(extra),host_intersection=sorted(first&second),
                 nonpivot_cross_edges=sum(not(set(e)<=first or set(e)<=second) for e in edges),
                 point_sha256=digest(points),edge_sha256=digest(edges))
    assert summary==data['geometry'] and (len(points),len(edges))==(2035,9770)
    word=data['search']['five_coloring'];assert data['search']['status']=='SAT'
    assert len(word)==len(points) and set(word)==set('01234') and all(word[i]!=word[j] for i,j in edges)
    projection={}
    for copy in copies:
        for i,p in enumerate(copy):
            assert p not in projection or projection[p]==i
            projection[p]=i
    core_edges=set(map(tuple,core['induced_edges']))
    assert all(tuple(sorted((projection[i],projection[j]))) in core_edges for i,j in edges)
    assert all(core['five_coloring'][projection[i]]!=core['five_coloring'][projection[j]] for i,j in edges)
    assert data['mechanism']['unit_graph_projection']=='Every occurrence maps to its original Parts vertex index'
    # The two added edges are the Laurent identities (Z+Z^-1)-Z=Z^-1
    # and Z*(Z+Z^-1)-1=Z^2. The only coincidence is identically zero.
    return dict(status='PASS',experiment='E053',**summary,new_radius=True,chromatic_number=5,
                identity_unit_edges=len(edges),exceptional_unit_edges=0,
                scope='Finite induced graph and its identity-edge classification, not a plane bound')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
