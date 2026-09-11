"""Independent E055--E057 geometry and finite-interface checker for T092.

No producer or SAT imports. Positive contacts are reconstructed from the
unit shell and the exceptional center, not by the producer's square solver.
"""
from fractions import Fraction as Q
from itertools import combinations,combinations_with_replacement
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice,filter_map,digest
from verify_quintic_bridge_contacts import km,RAD


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_independent_center.json').read_text())
    assert data['schema']==1 and data['experiments']==['E055','E056','E057'] and data['center']==64
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);assert core['coordinate_denominator']==96
    table=multiplication_twice();prime,images,bars=filter_map(table)
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    assert base[0]==zero and base[153]==one
    def geometry(blocks):
        den=math.lcm(*(x.denominator for block in blocks for p in block for x in p));assert den%prime
        raw_blocks=[[tuple(int(x*den) for x in p) for p in block] for block in blocks]
        pts=sorted({p for block in raw_blocks for p in block});index={p:i for i,p in enumerate(pts)}
        ids=[[index[p] for p in block] for block in raw_blocks]
        residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in pts]
        edges=[]
        for i,j in combinations(range(len(pts)),2):
            if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
            d=sub(pts[i],pts[j])
            if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
        summary=dict(vertices=len(pts),actual_pairs=len(pts)*(len(pts)-1)//2,induced_edges=len(edges),
                     point_sha256=digest(pts),edge_sha256=digest(edges))
        return pts,ids,edges,den,summary
    target_edges=[(i,j) for i,j in combinations(range(121),2) if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
    f11=(1,5,0,0,4,9,0,0)
    def label(p):
        assert not any(p[16:]) and all(x.denominator%11 for x in p[:16])
        a,b=[sum(x.numerator*pow(x.denominator,-1,11)*y for x,y in zip(axis,f11))%11 for axis in (p[:8],p[8:16])]
        return 11*a+b
    def check_word(word,n,edges):
        assert isinstance(word,str) and len(word)==n and set(word)==set('01234')
        assert all(word[i]!=word[j] for i,j in edges)
    def check_extension(search,n,edges,inside,neighbors):
        assert search['status']=='SAT'
        word=search['right_word'];target=search['residue_word']
        check_word(word,n,edges);check_word(target,121,target_edges)
        assert all(word[i]==target[0] for i in inside)
        contacts={(i,label(p)) for i,pair in neighbors.items() for p in pair}
        assert all(word[i]!=target[j] for i,j in contacts)
        return len(contacts)
    contexts={};finite_cases=[];reports=[]
    assert [item['sign'] for item in data['cases']]==[1,-1]
    for item in data['cases']:
        sign=item['sign'];r=tuple(-x for x in (mul(eta,eta) if sign==1 else eta));assert mul(r,bar(r))==one
        A=add(r,bar(r));c=tuple(x/2 for x in A[:8]);assert not any(A[8:])
        assert A[:8]==(Q(1,2),0,0,0,Q(sign,2),0,0,0)
        left=[base,[add(A,p) for p in base]];right=[[mul(r,p) for p in block] for block in left]
        fifth=[add(base[64],p) for p in base]
        pts,ids,edges,den,summary=geometry(left+right+[fifth])
        old=set(sum(ids[:4],[]));new=set(ids[4]);left_ids=set(ids[0]+ids[1]);right_ids=set(ids[2]+ids[3])
        summary.update(fifth_overlap=len(old&new),fifth_cross_edges=sum(not(set(e)<=old or set(e)<=new) for e in edges),
                       new_fifth_to_right_edges=sum((i in new-old and j in right_ids-left_ids) or (j in new-old and i in right_ids-left_ids) for i,j in edges))
        assert den==item['coordinate_denominator'] and summary==item['finite_geometry']
        assert (len(pts),len(edges),summary['fifth_overlap'],summary['new_fifth_to_right_edges'])==(2344,11532 if sign==1 else 11554,200,0)
        assert item['finite_search']['status']=='SAT';check_word(item['finite_search']['five_coloring'],len(pts),edges)
        finite_cases.append((pts,edges,den));reports.append(summary)
        qpoints=sorted(set(left[0]+left[1]));_,_,qedges,_,qsummary=geometry([qpoints]);contacts=item['contacts']
        assert qsummary==contacts['q_geometry'] and len(qpoints)==1018 and len(qedges)==4886
        norms=[mul(p,bar(p))[:8] for p in qpoints]
        h=tuple(x-y for x,y in zip(one[:8],km(c,c)))
        deltas=[km(n,tuple(x-y for x,y in zip(one[:8],km(h,n)))) for n in norms]
        maps=contacts['maps']
        for p,f in maps:
            assert type(p) is int and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
            assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
            for i,j in combinations_with_replacement(range(8),2):
                g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
                assert f[i]*f[j]%p==g*f[k]%p
        inside=contacts['inside'];negative=contacts['nonsquare'];roots=contacts['roots']
        assert inside==[qpoints.index(zero)] and len(negative)==980 and len(roots)==37
        assert sorted(inside+[i for i,m in negative]+[i for i,r in roots])==list(range(1018))
        for i,m in negative:
            assert 0<=m<len(maps);p,f=maps[m];d=deltas[i]
            assert all(x.denominator%p for x in d)
            value=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(d,f))%p
            assert pow(value,(p-1)//2,p)==p-1
        for i,rr in roots:
            rr=tuple(Q(x) for x in rr);assert len(rr)==8 and km(rr,rr)==deltas[i]
        unit_ids={i for i,n in enumerate(norms) if n==one[:8]};assert len(unit_ids)==36
        a_id=qpoints.index(A);assert {i for i,rr in roots}==unit_ids|{a_id}
        neighbors={i:[zero,mul(A,qpoints[i])] for i in unit_ids}
        neighbors[a_id]=[one,A]
        for i,pair in neighbors.items():
            assert len(set(pair))==2
            for p in pair:
                d=sub(p,mul(r,qpoints[i]));assert mul(d,bar(d))==one
        interface={zero}|{p for pair in neighbors.values() for p in pair}
        assert len(interface)==contacts['interface_points']==38
        assert check_extension(contacts['search'],1018,qedges,inside,neighbors)==contacts['contact_edges']==74
        contexts[sign]=(qpoints,inside,neighbors)
    orb=data['orbit'];assert orb['experiment']=='E057'
    rpower=one;blocks=[];block_neighbors=[];block_inside=[]
    for power in (1,2,3,4):
        rpower=mul(rpower,eta);r=tuple(-x for x in rpower)
        qpoints,inside,neighbors=contexts[1 if power in (2,3) else -1]
        blocks.append([mul(r,p) for p in qpoints]);block_inside.append(inside);block_neighbors.append(neighbors)
    pts,ids,edges,den,summary=geometry(blocks)
    assert den==orb['coordinate_denominator'] and summary==orb['geometry']
    assert (len(pts),len(edges))==(4069,19560)
    inside=sorted({ids[j][i] for j,part in enumerate(block_inside) for i in part});assert len(inside)==1
    neighbors={ids[j][i]:pair for j,part in enumerate(block_neighbors) for i,pair in part.items()}
    assert len(neighbors)==148 and check_extension(orb['search'],4069,edges,inside,neighbors)==orb['contact_edges']==296
    assert len({zero}|{p for pair in neighbors.values() for p in pair})==74
    right_index={tuple(Q(x,den) for x in p):i for i,p in enumerate(pts)}
    for finite,finite_edges,finite_den in finite_cases:
        word=[]
        for p in finite:
            physical=tuple(Q(x,finite_den) for x in p)
            word.append(orb['search']['right_word'][right_index[physical]] if any(physical[16:]) else orb['search']['residue_word'][label(physical)])
        check_word(''.join(word),len(finite),finite_edges)
    return dict(status='PASS',theorem='T092',experiments=data['experiments'],finite_cases=reports,
                exclusions_per_angle=980,positive_contacts_per_angle=37,orbit=summary,
                F_interface_points=74,F_contact_edges=296,infinite_host_chromatic_number=5,
                scope='F plus four fixed exceptional rotated blocks; not entire E, all two-host points or full joint feasibility')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
