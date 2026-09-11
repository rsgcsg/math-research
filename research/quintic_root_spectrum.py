"""E051: certify all origin-rooted Parts radial discriminants in F(eta).

Zero discriminants and finite-field nonsquare witnesses, never a failed
square-extraction call, support the negative classification.
"""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import argparse
import hashlib
import json
import math
from quintic_core_probe import mul,bar
from quintic_bridge_contacts import km,ki,DIMS
from quintic_congruence_probe import sqrt_mod


def certificate(root):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    points=[tuple(Q(x,96) for x in a+b) for a,b in core['points']]
    radii={}
    for i,p in enumerate(points):
        n=tuple(mul(p,bar(p))[:8])
        if any(n):radii.setdefault(n,i)
    values=list(radii);assert len(values)==47
    maps=[];primes=0
    for p in range(1009,100000):
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)):continue
        if not all(pow(d,(p-1)//2,p)==1 for d in DIMS):continue
        roots=[sqrt_mod(d,p) for d in DIMS]
        f=[math.prod(r for k,r in enumerate(roots) if j&(1<<k))%p for j in range(8)]
        for signs in range(8):maps.append((p,[x*(-1 if bin(j&signs).count('1')%2 else 1)%p for j,x in enumerate(f)]))
        primes+=1
        if primes==32:break
    D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0));inverse=ki(D)
    negative=[];zeros=[]
    for i,j in combinations_with_replacement(range(len(values)),2):
        a,b=values[i],values[j]
        t=tuple(x+y-(1 if k==0 else 0) for k,(x,y) in enumerate(zip(a,b)))
        q=km(tuple(4*x-y for x,y in zip(km(a,b),km(t,t))),inverse)
        if not any(q):zeros.append([i,j]);continue
        for mi,(p,f) in enumerate(maps):
            if any(x.denominator%p==0 for x in q):continue
            image=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(q,f))%p
            if pow(image,(p-1)//2,p)==p-1:negative.append([i,j,mi]);break
        else:raise AssertionError(('Unresolved radial discriminant',i,j))
    used=sorted({m for i,j,m in negative});remap={m:i for i,m in enumerate(used)}
    return dict(schema=1,results=['T088','E051'],core_sha256=hashlib.sha256(raw).hexdigest(),
                pivot=0,radius_representatives=list(radii.values()),maps=[maps[m] for m in used],
                nonsquare=[[i,j,remap[m]] for i,j,m in negative],zero=zeros,
                scope='Origin-rooted P and r P for unit r in F(eta) outside F; not arbitrary roots or fields')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=certificate(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(radii=len(data['radius_representatives']),nonsquare=len(data['nonsquare']),zero=data['zero'],maps=len(data['maps']))))
