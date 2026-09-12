"""Exact 625-element residue ring, global linear coloring, and Parts inclusion.

No SAT or geometry producer. Infinite conclusions use the accompanying proof.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice


def verify(root,geometry_context=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    def times(a,b):
        out=[0]*4
        for i,x in enumerate(a):
            for j,y in enumerate(b):
                nu_i,z_i=divmod(i,2);nu_j,z_j=divmod(j,2)
                terms=[(z_i+z_j,1)] if z_i+z_j<2 else [(0,-2),(1,-1)]
                for k,c in terms:
                    out[2*((nu_i+nu_j)%2)+k]+=x*y*c*(-1 if nu_i+nu_j==2 else 1)
        return tuple(x%5 for x in out)
    def conjugate(v):
        a,b,c,d=v
        return ((a-b)%5,-b%5,(-c+d)%5,d%5)
    elements=list(product(range(5),repeat=4));one4=(1,0,0,0)
    units=[v for v in elements if times(v,conjugate(v))==one4]
    assert len(units)==24
    def dot(a,b):return sum(x*y for x,y in zip(a,b))%5
    chars=[c for c in elements if any(c) and next(x for x in c if x)==1
           and all(dot(c,u) for u in units)]
    assert len(chars)==12 and (1,0,1,2) in chars
    # Verify all 7500 undirected unit edges, independently of the character filter.
    edges=set()
    for x in elements:
        for u in units:
            y=tuple((a+b)%5 for a,b in zip(x,u));edges.add(tuple(sorted((x,y))))
            assert dot((1,0,1,2),x)!=dot((1,0,1,2),y)
    assert len(edges)==7500
    standard=[tuple(int(i==j) for i in range(4)) for j in range(4)]
    for r in units:
        for reflection in (False,True):
            transformed=[]
            for ch in chars:
                values=[dot(ch,times(r,conjugate(b) if reflection else b)) for b in standard]
                scale=next(x for x in values if x)
                transformed.append(tuple(x*pow(scale,-1,5)%5 for x in values))
            assert sorted(transformed)==chars
    table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    z=tuple(-Q(1,2) if i==0 else -Q(1,6) if i==9 else Q(0) for i in range(32))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    powers=[one]
    for _ in range(4):powers.append(mul(eta,powers[-1]))
    assert all(sum(v[i] for v in powers)==0 for i in range(32))
    assert mul(z,z)==tuple(-a-Q(1,3)*b for a,b in zip(z,one))
    assert mul(nu,nu)==tuple(Q(5,3)*a-b for a,b in zip(nu,one))
    basis=powers[:4]+[mul(z,p) for p in powers[:4]]
    basis += [mul(nu,p) for p in basis[:]]
    rows=[]
    for j,v in enumerate(basis):
        v=list(v);e=[Q(int(i==j)) for i in range(16)]
        for pivot,row,old in rows:
            factor=v[pivot];v=[x-factor*y for x,y in zip(v,row)];e=[x-factor*y for x,y in zip(e,old)]
        assert any(v);pivot=next(i for i,x in enumerate(v) if x);scale=v[pivot]
        rows.append((pivot,[x/scale for x in v],[x/scale for x in e]))
    def coordinates(p):
        v=list(p);coeff=[Q(0)]*16
        for pivot,row,e in rows:
            factor=v[pivot];v=[x-factor*y for x,y in zip(v,row)];coeff=[x+factor*y for x,y in zip(coeff,e)]
        assert not any(v)
        assert all(p[i]==sum(coeff[j]*basis[j][i] for j in range(16)) for i in range(32))
        return coeff
    def residue(p):
        coeff=coordinates(p);assert all(x.denominator%5 for x in coeff)
        return tuple(sum(x.numerator*pow(x.denominator,-1,5) for x in coeff[i:i+4])%5 for i in range(0,16,4))
    # Exact source-ring map, with all basis products and conjugates checked.
    images=[residue(b) for b in basis]
    for i,a in enumerate(basis):
        assert residue(bar(a))==conjugate(images[i])
        for j,b in enumerate(basis):assert residue(mul(a,b))==times(images[i],images[j])
    parts=json.loads((root/'certificates/parts509_core.json').read_text())['points']
    P=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in parts]
    for p in P:residue(p)
    # A concrete norm-one direction outside this localized order.
    tau=tuple(-Q(1,10) if i==0 else Q(3,10) if i==10 else Q(0) for i in range(32))
    assert mul(tau,bar(tau))==one
    assert tuple(a+b for a,b in zip(tau,bar(tau)))==tuple(-Q(1,5)*a for a in one)
    assert any(x.denominator%5==0 for x in coordinates(tau))
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def neg(a):return tuple(-x for x in a)
    blocks=[P]
    for power in powers[1:]:
        r=neg(power);A=add(r,bar(r))
        blocks.extend([[mul(r,p) for p in P],[mul(r,add(A,p)) for p in P]])
    blocks.append([add(one,mul(eta,add(z,neg(p)))) for p in P])
    points=sorted({p for block in blocks for p in block});assert len(points)==5084
    lookup={p:i for i,p in enumerate(points)};values=[residue(p) for p in points]
    words=[[dot(ch,p) for p in values] for ch in chars]
    def pattern(word,indices):
        labels={}
        return tuple(labels.setdefault(word[i],len(labels)) for i in indices)
    probes=[]
    for name,r in [('nu',nu),('tau',tau)]:
        mapping=[(i,lookup[q]) for i,p in enumerate(points) if (q:=mul(r,p)) in lookup]
        source=[i for i,j in mapping];target=[j for i,j in mapping]
        same=sorted(pattern(w,source) for w in words)==sorted(pattern(w,target) for w in words)
        mismatch=None
        for a,(i,j) in enumerate(mapping):
            for k,l in mapping[a+1:]:
                counts=[sum(w[i]==w[k] for w in words),sum(w[j]==w[l] for w in words)]
                if counts[0]!=counts[1]:mismatch=dict(pairs=[[i,j],[k,l]],equal_counts=counts);break
            if mismatch:break
        if name=='nu':assert len(mapping)==271 and same
        probes.append(dict(motion=name,domain=len(mapping),full_partition_law_equal=same,
                           pair_mismatch=mismatch,
                           source_cross_copy=not any(set(source)<={lookup[p] for p in b} for b in blocks),
                           image_cross_copy=not any(set(target)<={lookup[p] for p in b} for b in blocks)))
    report=dict(status='PASS',theorems=['T108','T109'],residue_vertices=625,residue_unit_directions=24,
                residue_edges=7500,projective_proper_characters=12,rational_rank=16,
                parts_points_in_ring=len(parts),basis_products_checked=256,
                explicit_color_character=[1,0,1,2],tau_outside_ring=True,probes=probes,
                scope='Five-color formula on Z_(5)[eta,z,nu] and invariant joint law for its integral norm-one motions; not the whole field or plane')
    return (report,dict(points=points,blocks=blocks,mul=mul,table=table,tau=tau,residue=residue,coordinates=coordinates,characters=chars)) if geometry_context else report


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
