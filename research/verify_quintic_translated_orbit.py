"""Independent stdlib E058--E060 checker; no producer, square solver or SAT."""
from fractions import Fraction as Q
from itertools import combinations,combinations_with_replacement
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice,filter_map,digest
from verify_quintic_bridge_contacts import km,RAD
from verify_quintic_independent_center import verify as predecessor


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_translated_orbit.json').read_text())
    assert data['schema']==1 and data['experiments']==['E058','E059','E060'] and data['center']==64
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    assert hashlib.sha256((root/'certificates/quintic_independent_center.json').read_bytes()).hexdigest()==data['predecessor_sha256']
    predecessor(root)
    core=json.loads(raw);assert core['coordinate_denominator']==96
    table=multiplication_twice();prime,images,bars=filter_map(table)
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    P=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    assert P[0]==zero and P[153]==one
    shifted=[sub(p,P[64]) for p in P];norms=[mul(p,bar(p))[:8] for p in shifted]
    units={i for i,n in enumerate(norms) if n==one[:8]};assert len(units)==22
    rpower=one;rotations=[];centers=[];blocks=[];neighbors=[]
    for j in range(1,5):
        rpower=mul(rpower,eta);r=tuple(-x for x in rpower);assert mul(r,bar(r))==one
        A=add(r,bar(r));rotations.append(r);centers.append(A)
        qpoints=P+[add(A,p) for p in P];blocks.append([mul(r,p) for p in qpoints])
        nn={i:[zero,mul(A,p)] for i,p in enumerate(P) if mul(p,bar(p))==one};assert len(nn)==36
        nn[509]=[one,A];neighbors.append(nn)
    assert [row['power'] for row in data['classifications']]==[1,2]
    for row in data['classifications']:
        c=tuple(x/2 for x in centers[row['power']-1][:8]);h=sub(one[:8],km(c,c))
        deltas=[km(n,sub(one[:8],km(h,n))) for n in norms]
        maps=row['maps']
        for p,f in maps:
            assert type(p) is int and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
            assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
            for i,j in combinations_with_replacement(range(8),2):
                g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
                assert f[i]*f[j]%p==g*f[k]%p
        negative=row['nonsquare'];roots=row['roots'];inside=row['inside']
        assert inside==[64] and len(negative)==486 and len(roots)==22
        assert sorted(inside+[i for i,m in negative]+[i for i,r in roots])==list(range(509))
        for i,m in negative:
            assert 0<=m<len(maps);p,f=maps[m];d=deltas[i]
            assert all(x.denominator%p for x in d)
            v=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(d,f))%p
            assert pow(v,(p-1)//2,p)==p-1
        for i,rr in roots:
            rr=tuple(Q(x) for x in rr);assert len(rr)==8 and km(rr,rr)==deltas[i]
        assert {i for i,rr in roots}==units
    f11=(1,5,0,0,4,9,0,0)
    def label(p):
        assert not any(p[16:]) and all(x.denominator%11 for x in p[:16])
        a,b=[sum(x.numerator*pow(x.denominator,-1,11)*y for x,y in zip(axis,f11))%11 for axis in (p[:8],p[8:16])]
        return 11*a+b
    target_edges=[(i,j) for i,j in combinations(range(121),2) if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
    reports=[];assert [(row['extra_powers'],row['offset']) for row in data['cases']]==[([1],0),([1,2,3,4],0),([1],1)]
    for row in data['cases']:
        extra=row['extra_powers'];offset=row['offset'];anchor=one if offset else zero
        bs=blocks+[[add(anchor,mul(rotations[j-1],p)) for p in shifted] for j in extra]
        ns=neighbors+[{i:[anchor,add(anchor,mul(centers[j-1],shifted[i]))] for i in units} for j in extra]
        den=math.lcm(*(x.denominator for b in bs for p in b for x in p));assert den==row['denominator']==96
        ibs=[[tuple(int(x*den) for x in p) for p in b] for b in bs]
        pts=sorted({p for b in ibs for p in b});index={p:i for i,p in enumerate(pts)};ids=[[index[p] for p in b] for b in ibs]
        residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in pts]
        edges=[]
        for i,j in combinations(range(len(pts)),2):
            if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
            d=sub(pts[i],pts[j])
            if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
        old=set(sum(ids[:4],[]));new=set(sum(ids[4:],[]))-old;origin=index[(0,)*32]
        outside={i for i in new if any(pts[i][16:])}
        boundaries=[((set(ids[4+k])-old)&outside,set(sum([ids[h] for h in range(4) if h!=j-1],[]))-{origin}) for k,j in enumerate(extra)]
        cross=sum(any((i in a and j in b) or (j in a and i in b) for a,b in boundaries) for i,j in edges)
        summary=dict(vertices=len(pts),actual_pairs=len(pts)*(len(pts)-1)//2,induced_edges=len(edges),point_sha256=digest(pts),edge_sha256=digest(edges),
                     new_vertices=len(new),new_outside_H=len(outside),overlap=len(set(sum(ids[4:],[]))&old),new_to_other_old_blocks=cross)
        assert summary==row['geometry'] and cross==(7 if offset else 0)
        expected=(4577,22403,508) if offset else (4378,21316,309) if len(extra)==1 else (5305,26588,1236)
        assert (len(pts),len(edges),len(new))==expected
        contacts=set();interface={zero,anchor}
        for b,nn in enumerate(ns):
            for i,pp in nn.items():
                for p in pp:
                    d=sub(bs[b][i],p);assert mul(d,bar(d))==one
                    contacts.add((ids[b][i],label(p)));interface.add(p)
        assert len(contacts)==row['contact_edges']
        assert len(interface)==row['interface_points']
        if not offset:
            assert len(contacts)==(300 if len(extra)==1 else 312)
            assert len(interface)==(76 if len(extra)==1 else 78)
        search=row['search'];assert search['status']=='SAT'
        word=search['right_word'];target=search['residue_word']
        assert isinstance(word,str) and len(word)==len(pts) and set(word)==set('01234')
        assert isinstance(target,str) and len(target)==121 and set(target)==set('01234')
        assert all(word[i]!=word[j] for i,j in edges)
        assert all(target[i]!=target[j] for i,j in target_edges)
        assert word[origin]==target[0] and all(word[i]!=target[j] for i,j in contacts)
        inside=[i for i,p in enumerate(pts) if not any(p[16:])]
        assert len(inside)==(2 if offset else 1)
        assert all(word[i]==target[label(tuple(Q(x,den) for x in pts[i]))] for i in inside)
        # Orientation groups are vertex sets, not disjoint affine lines when
        # offset=1. Their overlap can reclassify old edges; do not interpret
        # that case's count as the number of newly created geometric contacts.
        same_direction=[set(ids[j]+ids[4+extra.index(j+1)]) if j+1 in extra else set(ids[j]) for j in range(4)]
        cross_all=[(i,j) for i,j in edges if not any(i in b and j in b for b in same_direction)]
        if not offset:assert len(cross_all)==16
        reports.append(dict(**summary,interface_points=len(interface),contact_edges=len(contacts),edges_outside_orientation_groups=len(cross_all)))
    return dict(status='PASS',theorem='T093',experiments=data['experiments'],cases=reports,
                scope='Specified finite additions to the entire F; moved-pivot case is separate from the four-root case; not E or full joint')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
