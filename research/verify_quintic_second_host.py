"""Independent E049/E050 geometry and T087 direction-invariant checker."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
from verify_quintic_bridge_contacts import context,km,divide
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice,filter_map,digest


def verify(root,certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_second_host.json').read_text())
    assert data['schema']==1 and data['experiment'] in ('E049','E050')
    assert set(data['sources'])=={'parts509_core.json','quintic_core_probe.json','quintic_bridge_contacts.json'}
    for name,sha in data['sources'].items():
        assert hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()==sha
    core,old,base,old_edges,records,r0,mul,bar=context(root)
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def sub(a,b):return tuple(x-y for x,y in zip(a,b))
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    z=base[64];origin=sub(z,mul(r0,base[332]))
    inverse=(Q(3,2),Q(0),Q(0),Q(0),Q(3,10))+(Q(0),)*27
    points_q=set(old)
    for ui,vi in [(332,451),(133,377),(379,129),(330,449),(447,328),(381,131)]:
        r=mul(mul(sub(old[337],z),bar(sub(base[vi],base[ui]))),inverse)
        assert mul(r,bar(r))==one
        points_q.update(add(z,mul(r,sub(p,base[ui]))) for p in base)
    assert len(points_q)==4125
    contacts=json.loads((root/'certificates/quintic_bridge_contacts.json').read_text())
    interface={records[i][0]+records[i][1]+zero[:16] for i in contacts['inside']}
    neighbors={}
    for i,raw_r in contacts['roots']:
        ax,ay,bx,by,e,q=records[i];root_r=tuple(Q(x) for x in raw_r)
        assert km(root_r,root_r)==q
        scale=divide(root_r,e);dx=km(scale,by);dy=km(scale,bx)
        for sign in (-1,1):
            p=tuple(x-sign*y for x,y in zip(ax,dx))+tuple(x+sign*y for x,y in zip(ay,dy))+zero[:16]
            interface.add(p);neighbors[i,sign]=add(origin,mul(r0,p))
    assert len(interface)==81
    points_q.update(add(origin,mul(r0,p)) for p in interface)
    assert len(points_q)==4202

    # The entire old contact catalog comes from four images of the same
    # 22-neighbor wheel. Verify the geometric switch, not just host counts.
    core_neighbors=[j for j,p in enumerate(base) if mul(sub(p,z),bar(sub(p,z)))==one]
    assert len(core_neighbors)==22
    index_old={p:i for i,p in enumerate(old)}
    copies=[base]+[[add(base[c],mul(eta,sub(p,base[c]))) for p in base] for c in (0,153,150)]
    known_keys={('F',zero[:16]),('eta',zero[:16]),('eta',base[153][:16]),('eta',base[150][:16])}
    novel_keys=set();expected=set()
    for k,copy in enumerate(copies):
        pivot=copy[64]
        for j in core_neighbors:
            x=copy[j];i=index_old[x];expected.add(i)
            other=sub(x,mul(eta if k==0 else bar(eta),sub(x,pivot)))
            assert {neighbors[i,-1],neighbors[i,1]}=={pivot,other}
            for y in (pivot,other):
                r=sub(y,x);assert mul(r,bar(r))==one
                if not any(r[16:]): key=('F',x[16:])
                else:
                    assert not any(r[:16]);key=('eta',x[:16])
                if key not in known_keys:novel_keys.add(key)
    assert expected=={i for i,r in contacts['roots']} and len(expected)==88
    assert len(novel_keys)==82 and {k for k,c in novel_keys}=={'F','eta'}

    if data['experiment']=='E049':
        assert data['construction']=='contact_bridge' and data['selected_contact']==[1,-1]
        c=old[1];r=sub(neighbors[1,-1],c)
        added=[add(c,mul(r,p)) for p in base]
        # The new affine plane is distinct from every previously used one.
        known=[(zero,one)]+[(sub(base[i],mul(eta,base[i])),eta) for i in (0,153,150)]+[(origin,r0)]
        for t,d in known:
            assert any(mul(r,bar(d))[16:]) or any(mul(sub(c,t),bar(d))[16:])
        target_counts=(4709,22920,2)
        field_trace=None
    else:
        assert data['construction']=='non_torsion_conic'
        aa=(Q(13,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
        bb=(Q(-49,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
        t=(Q(-1,2),Q(0),Q(0),Q(0),Q(1,2),Q(0),Q(0),Q(0))
        h=tuple((2 if i==0 else 0)-x for i,x in enumerate(t))
        assert tuple(x+y+z for x,y,z in zip(km(aa,aa),km(h,km(aa,bb)),km(h,km(bb,bb))))==(Q(1),)+(Q(0),)*7
        c=add(z,aa+zero[8:]);r=tuple(-x-y for x,y in zip(aa,bb))+zero[:8]+bb+zero[:8]
        assert mul(r,bar(r))==one
        y=add(c,r)
        assert y==add(z,mul(sub(eta,one),bb+zero[8:]))
        points_q.add(y)
        added=[add(c,p) for p in base]+[add(c,mul(r,p)) for p in base]
        # sigma fixes F and sends eta to eta^-1. For this real-coefficient
        # rotation sigma(r)=bar(r), hence its direction invariant is r^2.
        sigma=add(r[:16]+zero[:16],mul(bar(eta),r[16:]+zero[:16]))
        assert sigma==bar(r)
        invariant=mul(r,bar(sigma));trace=add(invariant,bar(invariant))
        expected_trace=(Q(419,1922),Q(0),Q(0),Q(0),Q(-979,1922))+(Q(0),)*27
        assert trace==expected_trace
        field_trace=8*trace[0]
        assert field_trace==Q(1676,961) and field_trace.denominator!=1
        # Vieta composition preserves a^2+b^2-2 Re(r) ab; its trace is
        # invariant+invariant^-1 and determinant is one.
        twice_real=add(r,bar(r));assert not any(twice_real[8:])
        s=twice_real[:8];ss=km(s,s)
        assert tuple(x-(2 if i==0 else 0) for i,x in enumerate(ss))==trace[:8]
        target_counts=(5219,25361,0)
    den=data['coordinate_denominator'];assert type(den) is int and den>0
    def integer(p):
        assert all((x*den).denominator==1 for x in p)
        return tuple(int(x*den) for x in p)
    baseline=points_q
    points=sorted({integer(p) for p in baseline|set(added)});index={p:i for i,p in enumerate(points)}
    old_set={index[integer(p)] for p in baseline};new_set={index[integer(p)] for p in added}
    table=multiplication_twice();prime,images,bars=filter_map(table);assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        d=sub(points[i],points[j])
        if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
    summary=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,induced_edges=len(edges),
                 baseline_vertices=len(old_set),overlap=len(old_set&new_set),
                 nonshared_cross_edges=sum(not(set(e)<=old_set or set(e)<=new_set) for e in edges),
                 point_sha256=digest(points),edge_sha256=digest(edges))
    assert summary==data['geometry']
    if target_counts:assert (len(points),len(edges),summary['nonshared_cross_edges'])==target_counts
    word=data['search']['five_coloring'];assert data['search']['status']=='SAT'
    assert isinstance(word,str) and len(word)==len(points) and set(word)==set('01234')
    assert all(word[i]!=word[j] for i,j in edges)
    if data['experiment']=='E050':
        first={index[integer(p)] for p in added[:509]}
        second={index[integer(p)] for p in added[509:]}
        assert not (first&old_set) and second&old_set=={index[integer(y)]}
        assert first&second=={index[integer(c)]}
        assert all(set(e)<=old_set or set(e)<=first or set(e)<=second for e in edges)
        assert sum(set(e)<=old_set for e in edges)==20477
        assert sum(set(e)<=first for e in edges)==sum(set(e)<=second for e in edges)==2442
    return dict(status='PASS',experiment=data['experiment'],**summary,chromatic_number=5,
                contact_planes=82,contact_direction_classes=2,invariant_field_trace=str(field_trace),
                one_vertex_amalgamation=data['experiment']=='E050',
                scope='Finite induced coloring and stated direction invariant only; no plane bound or full joint claim')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificate',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],args.certificate),indent=2))
