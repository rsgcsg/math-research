"""Exact contacts of finite E043 with the entire first-bridge K plane.

Search uses quadratic-tower square extraction; negative answers are emitted
only with a finite-field nonsquare witness, not from the extraction algorithm.
"""
from fractions import Fraction as Q
from pathlib import Path
from functools import lru_cache
import json
import math
import argparse
import hashlib
from itertools import combinations
from quintic_core_probe import geometry
from quintic_mixed_congruence_probe import product2, conjugate2, subtract
from quintic_congruence_probe import sqrt_mod

DIMS = (3,11,5)


def km(a,b):
    out = [Q(0)]*len(a)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            factor = math.prod(d for k,d in enumerate(DIMS) if i&j&(1<<k))
            out[i^j] += x*y*factor
    return tuple(out)


def ki(a):
    if len(a)==1:
        return (1/a[0],)
    half=len(a)//2;d=DIMS[half.bit_length()-1]
    x,y=a[:half],a[half:]
    norm=tuple(u-d*v for u,v in zip(km(x,x),km(y,y)))
    inv=ki(norm)
    return km(x,inv)+tuple(-z for z in km(y,inv))


@lru_cache(None)
def square_roots(a):
    if not any(a):
        return ((Q(0),)*len(a),)
    if len(a)==1:
        x=a[0]
        if x<0: return ()
        n,d=math.isqrt(x.numerator),math.isqrt(x.denominator)
        return ((Q(n,d),),(-Q(n,d),)) if n*n==x.numerator and d*d==x.denominator else ()
    half=len(a)//2;d=DIMS[half.bit_length()-1]
    x,y=a[:half],a[half:];zero=(Q(0),)*half
    if not any(y):
        return tuple(r+zero for r in square_roots(x))+tuple(zero+r for r in square_roots(tuple(z/d for z in x)))
    norm=tuple(u-d*v for u,v in zip(km(x,x),km(y,y)))
    out=[]
    for n in square_roots(norm):
        for u in square_roots(tuple((v+w)/2 for v,w in zip(x,n))):
            if any(u):
                v=tuple(z/2 for z in km(y,ki(u)))
                r=u+v
                assert km(r,r)==a
                if r not in out: out.append(r)
    return tuple(out)


def coordinates(root):
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    old,_,_,_=geometry(core,[0,153,150],[1])
    old=[tuple(Q(x,96) for x in p) for p in old]
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    a,b=old[84],old[337];u,v=base[332],base[451]
    inv=[Q(0)]*32;inv[0]=Q(3,2);inv[4]=Q(3,10)
    r=tuple(Q(x)/8 for x in product2(product2(subtract(b,a),conjugate2(subtract(v,u))),inv))
    rc=tuple(Q(x)/2 for x in conjugate2(r))
    alpha=(Q(-1,4),Q(0),Q(0),Q(0),Q(1,4),Q(0),Q(0),Q(0))
    D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    out=[]
    for x in old:
        c=tuple(xx+Q(yy)/2 for xx,yy in zip(u,product2(rc,subtract(x,a))))
        ax=tuple(x+y for x,y in zip(c[:8],km(alpha,c[16:24])))
        ay=tuple(x+y for x,y in zip(c[8:16],km(alpha,c[24:])))
        bx=tuple(-x/4 for x in c[24:]);by=tuple(x/4 for x in c[16:24])
        e=tuple(x+y for x,y in zip(km(bx,bx),km(by,by)))
        q=tuple(x-y for x,y in zip(e,km(D,km(e,e))))
        out.append((ax,ay,bx,by,e,q))
    return out


def run(root):
    records=coordinates(root)
    maps=[]
    primes=[]
    for p in range(1009,10000):
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)): continue
        if all(pow(d,(p-1)//2,p)==1 for d in DIMS): primes.append(p)
        if len(primes)==8: break
    for p in primes:
        roots=[sqrt_mod(d,p) for d in DIMS]
        f=[math.prod(r for k,r in enumerate(roots) if j&(1<<k))%p for j in range(8)]
        for signs in range(8):
            maps.append((p,tuple(x*(-1 if bin(j&signs).count('1')%2 else 1)%p for j,x in enumerate(f[:8]))))
    inside=[];negative=[];positive=[];unknown=[]
    for j,(ax,ay,bx,by,e,q) in enumerate(records):
        if not any(e): inside.append(j);continue
        for mi,(p,f) in enumerate(maps):
            if any(x.denominator%p==0 for x in q): continue
            image=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(q,f))%p
            if pow(image,(p-1)//2,p)==p-1:
                negative.append([j,mi]);break
        else:
            roots=square_roots(q)
            if roots:
                positive.append((j,roots[0]))
            else: unknown.append(j)
    print(json.dumps(dict(inside=inside,nonsquare=len(negative),square=len(positive),unknown=unknown,
                         positive_ids=[j for j,r in positive])),flush=True)
    return records,maps,inside,negative,positive,unknown


def certificate(root):
    from pysat.solvers import Solver
    records,maps,inside,negative,positive,unknown=run(root)
    assert not unknown
    neighbors={}
    for i,r in positive:
        ax,ay,bx,by,e,q=records[i]
        scale=km(r,ki(e));dx=km(scale,by);dy=km(scale,bx)
        neighbors[i]=[(tuple(x-s*y for x,y in zip(ax,dx)),
                       tuple(x+s*y for x,y in zip(ay,dy))) for s in (-1,1)]
    interface={(records[i][0],records[i][1]) for i in inside}
    interface.update(p for points in neighbors.values() for p in points)
    images=(1,5,0,0,4,9,0,0)
    def reduced(point):
        assert all(x.denominator%11 for axis in point for x in axis)
        return tuple(sum(x.numerator*pow(x.denominator,-1,11)*y for x,y in zip(axis,images))%11 for axis in point)
    def target(point):
        x,y=reduced(point)
        return 2033+11*x+y
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    old,_,edges,_=geometry(core,[0,153,150],[1])
    assert len(old)==2033
    target_edges=[(2033+i,2033+j) for i,j in combinations(range(121),2)
                  if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
    contact_edges=sorted({(i,target(p)) for i,points in neighbors.items() for p in points})
    equalities=[(i,target((records[i][0],records[i][1]))) for i in inside]
    clauses=[[5*v+c+1 for c in range(5)] for v in range(2154)]
    clauses += [[-5*v-a-1,-5*v-b-1] for v in range(2154) for a,b in combinations(range(5),2)]
    clauses += [[-5*a-c-1,-5*b-c-1] for a,b in edges+target_edges+contact_edges for c in range(5)]
    clauses += [[s*(5*a+c+1),-s*(5*b+c+1)] for a,b in equalities for c in range(5) for s in (-1,1)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(100000)
        answer=solver.solve_limited()
        assert answer is True,'No positive law obtained; do not claim an infinite upper bound'
        model=set(x for x in solver.get_model() if x>0)
        word=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(2154))
        stats=solver.accum_stats()
    used=sorted({m for i,m in negative}); remap={m:j for j,m in enumerate(used)}
    return dict(schema=1,results=['T086','E048'],
                sources={name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
                         for name in ('parts509_core.json','quintic_core_probe.json')},
                maps=[maps[i] for i in used],inside=inside,nonsquare=[[i,remap[m]] for i,m in negative],
                roots=[[i,[str(x) for x in r]] for i,r in positive],
                interface_points=len(interface),contact_edges=len(contact_edges),
                residue_images=images,old_word=word[:2033],residue_word=word[2033:],search_stats=stats,
                scope='The entire X union Phi(K squared) is five-colorable; no whole-plane or full-joint claim')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    if args.output:
        data=certificate(root)
        args.output.write_text(json.dumps(data,indent=2)+'\n')
        print(json.dumps({k:v for k,v in data.items() if k not in ('nonsquare','roots','old_word','residue_word')}))
    else:
        run(root)
