"""Independent E054 map-cover checker for the entire parametric family.

Uses gcd-based integer arithmetic and polynomial convolution rather than
the producer's expanded contact polynomial. No search modules are imported.
"""
from fractions import Fraction as Q
from itertools import product,combinations_with_replacement,permutations,combinations
from pathlib import Path
import hashlib
import json
import math

RAD=(1,3,11,33,5,15,55,165)
ZERO=(0,)*8
ONE=(1,)+(0,)*7
TABLE={(i,j):(RAD.index(RAD[i]*RAD[j]//math.gcd(RAD[i],RAD[j])**2),math.gcd(RAD[i],RAD[j]))
       for i in range(8) for j in range(8)}


def times(a,b):
    out=[0]*8
    for i,x in enumerate(a):
        if not x:continue
        for j,y in enumerate(b):
            if y:
                k,g=TABLE[i,j];out[k]+=g*x*y
    return tuple(out)


def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def scaled(a,n):return tuple(n*x for x in a)
def trim(a):
    while a and not any(a[-1]):a.pop()
    return a
def psum(*polys):
    out=[ZERO]*max(map(len,polys))
    for poly in polys:
        for i,a in enumerate(poly):out[i]=plus(out[i],a)
    return trim(out)
def pmul(a,b):
    out=[ZERO]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]=plus(out[i+j],times(x,y))
    return trim(out)
def deflate(poly):
    for z in (-1,1):
        while len(poly)>1:
            remainder=list(poly);quotient=[ZERO]*(len(poly)-1)
            for j in range(len(poly)-1,0,-1):
                a=remainder[j];quotient[j-1]=a;remainder[j]=ZERO
                remainder[j-1]=plus(remainder[j-1],scaled(a,z))
            if any(remainder[0]):break
            poly=trim(quotient)
    return poly


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_parametric_contacts.json').read_text())
    assert data['schema']==1 and data['experiment']=='E054'
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);assert len(core['points'])==509 and core['coordinate_denominator']==96
    points=[(tuple(x),tuple(y)) for x,y in core['points']]
    maps=data['maps'];projected=[];squares=[];dinv=[]
    for p,f in maps:
        assert type(p) is int and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
        assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
        for i,j in combinations_with_replacement(range(8),2):
            k,g=TABLE[i,j];assert f[i]*f[j]%p==g*f[k]%p
        assert (10+2*f[4])%p
        inv=pow(96,-1,p)
        projected.append([(sum(x*y for x,y in zip(a,f))*inv%p,sum(x*y for x,y in zip(b,f))*inv%p) for a,b in points])
        squares.append({x*x%p for x in range(p)});dinv.append(pow(10+2*f[4],-1,p))
    universal=[];residual=[];counts={}
    for k,l in ((0,0),(1,0),(1,1)):
        stats=dict(linear_cover=0,constant_sine=0,endpoints=0,polynomial_cover=0,universal=0,exact_exception=0)
        for i,j in product(range(509),repeat=2):
            x,y=points[i];u,v=points[j]
            L1=scaled(plus(scaled(y,l),scaled(v,-k)),192)
            if any(L1):
                for mi,(p,f) in enumerate(maps):
                    a,b=projected[mi][i];h,t=projected[mi][j]
                    lead=2*(l*b-k*t)%p
                    if not lead:continue
                    c=(a*t-b*h)*pow(lead,-1,p)%p
                    a=(a+2*k*c)%p;h=(h+2*l*c)%p
                    norm=(a*a+b*b+h*h+t*t-2*c*(a*h+b*t))%p
                    if norm!=1 or (1-c*c)*dinv[mi]%p not in squares[mi]:
                        stats['linear_cover']+=1;break
                else:
                    L0=plus(times(y,u),scaled(times(x,v),-1))
                    if L0==L1 or L0==scaled(L1,-1):stats['endpoints']+=1
                    else:residual.append([k,l,i,j]);stats['exact_exception']+=1
                continue
            L0=plus(times(y,u),scaled(times(x,v),-1))
            if any(L0):stats['constant_sine']+=1;continue
            a=[x,scaled(ONE,192*k)];b=[y];h=[u,scaled(ONE,192*l)];t=[v]
            dot=psum(pmul(a,h),pmul(b,t))
            poly=psum(pmul(a,a),pmul(b,b),pmul(h,h),pmul(t,t),
                      [ZERO]+[scaled(z,-2) for z in dot],[scaled(ONE,-9216)])
            if not poly:universal.append([k,l,i,j]);stats['universal']+=1;continue
            poly=deflate(poly)
            if len(poly)==1:stats['endpoints']+=1;continue
            for mi,(p,f) in enumerate(maps):
                cs=[sum(x*y for x,y in zip(z,f))%p for z in poly]
                if not cs[-1]:continue
                roots=[]
                for c in range(p):
                    val=sum(a*pow(c,n,p) for n,a in enumerate(cs))%p
                    if val==0:roots.append(c)
                if all((1-c*c)*dinv[mi]%p not in squares[mi] for c in roots):
                    stats['polynomial_cover']+=1;break
            else:residual.append([k,l,i,j]);stats['exact_exception']+=1
        counts[f'{k},{l}']=stats
    assert counts==data['counts'] and universal==data['universal']
    assert residual==data['exceptional_pairs']==[[1,1,0,0]]
    # 8c^2(1-c)-1 = -(2c-1)(4c^2-2c-1).
    factors=pmul([scaled(ONE,-1),scaled(ONE,2)],
                 [scaled(ONE,-1),scaled(ONE,-2),scaled(ONE,4)])
    assert factors==[ONE,ZERO,scaled(ONE,-8),scaled(ONE,8)]
    cosines=[tuple(Q(x) for x in row) for row in data['exceptional_cosines']]
    assert cosines==[(Q(1,4),0,0,0,Q(s,4),0,0,0) for s in (1,-1)]
    ds=[(Q(-1,8),0,0,0,Q(1,8),0,0,0),(Q(1,4),0,0,0,0,0,0,0)]
    D=(10,0,0,0,2,0,0,0)
    for c,d in zip(cosines,ds):
        assert plus(times(c,c),times(D,times(d,d)))==ONE
        assert plus(scaled(times(c,c),4),plus(scaled(c,-2),scaled(ONE,-1)))==ZERO
    # Every other universal edge of type (0,0) is incident with the pivot.
    unit_ids=[i for i,(x,y) in enumerate(points) if plus(times(x,x),times(y,y))==scaled(ONE,9216)]
    assert len(unit_ids)==36
    assert universal==[[0,0,i,j] for i,j in product(range(509),repeat=2)
                       if (i==0 and j in unit_ids) or (j==0 and i in unit_ids)]+[[1,0,0,153]]
    # Calibrate every abstract interface pattern, not just an old fixed word.
    perms=[p for p in permutations(range(5)) if p[0]==0]
    for a in range(5):
        assert any(a!=p[1] and 1!=p[a] for p in perms)
        assert any(a!=p[1] and 1!=p[a] and a!=p[a] for p in perms)==(a!=0)
    # A translated residue coloring separates 0 and A=2c at both exceptions.
    rows=json.loads((root/'certificates/residue11_coloring.json').read_text())['rows']
    word=''.join(rows);assert len(word)==121 and set(word)==set('01234')
    for i,j in combinations(range(121),2):
        if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1:assert word[i]!=word[j]
    separations=[]
    for A in (8,4):
        choices=[(x,y) for x,y in product(range(11),repeat=2) if rows[x][y]!=rows[(x+A)%11][y]]
        assert choices;separations.append([A,*choices[0]])
    return dict(status='PASS',experiment='E054',theorem='T091',ordered_pairs=3*509**2,
                universal_pairs=73,exceptional_pairs=1,exceptional_cosines=2,unresolved=0,
                residue_separations=separations,scope='Entire stated four-copy angle family is five-colorable; not arbitrary angles/templates')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
