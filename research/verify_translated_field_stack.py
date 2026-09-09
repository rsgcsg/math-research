"""Independent finite residue targets and explicit orthogonal transports.

The lift to all of K^2 and all integer sheets requires T063's proof.
"""
from itertools import combinations,product
from pathlib import Path
import hashlib
import json
import math


def verify(root,data_override=None):
    data=data_override if data_override is not None else json.loads((root/'certificates/translated_field_stack.json').read_text())
    assert data['schema']==1 and data['prime']==11
    vertices=list(product(range(2),range(11),range(11)));seen={};total_edges=0
    for case in data['cases']:
        u,v=case['offset'];norm=(u*u+v*v)%11
        assert norm==case['norm'] and norm not in seen
        assert case['status']=='SAT_CANDIDATE' and case['vertices']==242
        colors=list(map(int,case['word']));assert len(colors)==242 and set(colors)<=set(range(5))
        count=0
        for i,j in combinations(range(242),2):
            a,x,y=vertices[i];b,z,t=vertices[j]
            dx,dy=(x-z)%11,(y-t)%11
            same=a==b and (dx*dx+dy*dy)%11==1
            cross=a!=b and (dx,dy) in ((u,v),(-u%11,-v%11))
            if same or cross:assert colors[i]!=colors[j];count+=1
        assert count==case['edges'];total_edges+=count;seen[norm]=(u,v)
        if any(a['pinned'] for a in case['attempts']):
            triangle=((0,0),(1,0),(6,8))
            assert all(sum((x-y)**2 for x,y in zip(a,b))%11==1 for a,b in combinations(triangle,2))
    assert set(seen)==set(range(11)) and seen[0]==(0,0)
    transforms=0
    for x,y in product(range(11),repeat=2):
        norm=(x*x+y*y)%11
        if norm==0:assert (x,y)==(0,0);continue
        u,v=seen[norm];inv=pow(norm,-1,11)
        # M=[u,Ju][v,Jv]^T/n maps source (x,y) to representative (u,v).
        c=(u*x+v*y)*inv%11;s=(v*x-u*y)*inv%11
        assert (c*c+s*s)%11==1
        assert ((c*x-s*y)%11,(s*x+c*y)%11)==(u,v)
        transforms+=1
    result=dict(status='PASS',target_graphs=len(seen),target_vertices_each=242,
                all_target_pairs_checked=11*242*241//2,target_edges_checked=total_edges,
                nonzero_offset_orthogonal_transports=transforms,
                scope='All 121 residue offsets covered; arbitrary denominators and infinite sheets use T063')
    result['finite_probe']=verify_finite(root,data['finite_probe'])
    observation=json.loads((root/'certificates/translated_field_triangular.json').read_text())
    edges=set();index=lambda m,n,x,y:121*(2*(m%2)+n%2)+11*(x%11)+y%11
    center_steps=[(m,n) for m,n in product(range(-2,3),repeat=2) if m*m+m*n+n*n==1]
    assert len(center_steps)==6
    for m,n,x,y in product(range(2),range(2),range(11),range(11)):
        a=index(m,n,x,y)
        for u,v in product(range(11),repeat=2):
            if ((u-x)**2+(v-y)**2)%11==1:edges.add(tuple(sorted((a,index(m,n,u,v)))))
        for dm,dn in center_steps:
            # v=J(dm+dn/2,sqrt(3)dn/2)/3, sqrt(3)->5.
            dx=(-5*dn*pow(6,-1,11))%11;dy=((2*dm+dn)*pow(6,-1,11))%11
            for s in (-1,1):edges.add(tuple(sorted((a,index(m+dm,n+dn,x+s*dx,y+s*dy)))))
    assert observation['status']=='UNKNOWN' and observation['vertices']==484 and observation['edges']==len(edges)==4356
    assert observation['conflict_budget']==200000 and all(a!=b for a,b in edges)
    result['triangular_quotient']='UNKNOWN; only encoding counts checked'
    return result


def verify_finite(root,case):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    assert case['core_sha256']==hashlib.sha256(raw).hexdigest() and case['layers']==[-2,-1,0,1,2]
    radical=(1,3,11,33,5,15,55,165,2,6,22,66,10,30,110,330)
    points=[]
    for n in case['layers']:
        for p in core['points']:
            a=[list(ax)+[0]*8 for ax in p];a[0][9]=32*n
            points.append(tuple(map(tuple,a)))
    assert len(points)==len(set(points))==case['vertices']==2545
    prime=1000
    while True:
        prime+=1
        if not all(prime%d for d in range(2,math.isqrt(prime)+1)):continue
        roots={a*a%prime:a for a in range(prime)}
        if all(r in roots for r in (2,3,5,11)):break
    images=[]
    for r in radical:
        z=1
        for factor in (2,3,5,11):
            if r%factor==0:z=z*roots[factor]%prime
        images.append(z)
    products={}
    for i,r in enumerate(radical):
        for j,s in enumerate(radical):
            g=math.gcd(r,s);k=radical.index(r*s//(g*g));products[i,j]=(k,g)
            assert images[i]*images[j]%prime==g*images[k]%prime
    projected=[tuple(sum(a*b for a,b in zip(ax,images))%prime for ax in p) for p in points]
    colors=list(map(int,case['word']));assert len(colors)==len(points) and set(colors)<=set(range(5))
    edges=[];survivors=0;cross=[0]*4
    for i,j in combinations(range(len(points)),2):
        if sum((a-b)**2 for a,b in zip(projected[i],projected[j]))%prime!=96**2%prime:continue
        survivors+=1;norm=[0]*16
        for ax,bx in zip(points[i],points[j]):
            nz=[(k,a-b) for k,(a,b) in enumerate(zip(ax,bx)) if a!=b]
            for k,a in nz:
                for l,b in nz:
                    r,g=products[k,l];norm[r]+=a*b*g
        if norm==[96**2]+[0]*15:
            assert colors[i]!=colors[j];edges.append((i,j))
            if i//509!=j//509:
                assert j//509-i//509==1;cross[i//509]+=1
    assert len(edges)==case['edges'] and cross==[case['cross_edges_per_interface']]*4
    assert hashlib.sha256(json.dumps(edges,separators=(',',':')).encode()).hexdigest()==case['edge_sha256']
    return dict(vertices=len(points),edges=len(edges),cross_edges_per_interface=cross[0],
                all_pairs_checked=len(points)*(len(points)-1)//2,exact_radical_candidates=survivors)


if __name__=='__main__':
    if not __debug__:raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
