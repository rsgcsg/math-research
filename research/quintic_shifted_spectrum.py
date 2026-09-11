"""E052: exhaustive combined spectra of Parts rooted at 0 and 64.

Every negative entry has a split-prime witness. A failed square extraction
remains UNKNOWN and prevents a complete certificate from being emitted.
"""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import argparse
import hashlib
import json
import math
from quintic_core_probe import mul, bar
from quintic_bridge_contacts import ki, km, square_roots, DIMS
from quintic_congruence_probe import sqrt_mod


def split_maps():
    maps=[];count=0
    for p in range(1009,100000):
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)):continue
        if not all(pow(d,(p-1)//2,p)==1 for d in DIMS):continue
        roots=[sqrt_mod(d,p) for d in DIMS]
        f=[math.prod(r for k,r in enumerate(roots) if j&(1<<k))%p for j in range(8)]
        for signs in range(8):
            maps.append((p,[x*(-1 if bin(j&signs).count('1')%2 else 1)%p for j,x in enumerate(f)]))
        count+=1
        if count==32:return maps
    raise RuntimeError('Insufficient split primes')


def certificate(root):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    assert core['coordinate_denominator']==96
    points=[a+b for a,b in core['points']];radii={}
    counts=[]
    for pivot in (0,64):
        local=set()
        for i,p in enumerate(points):
            d=[x-y for x,y in zip(p,points[pivot])]
            n=tuple(mul(d,bar(d))[:8])
            if any(n):local.add(n);radii.setdefault(n,[pivot,i])
        counts.append(len(local))
    values=list(radii);maps=split_maps();D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    images=[[sum(x*y for x,y in zip(n,f))%p for n in values] for p,f in maps]
    invD=[pow(10+2*f[4],-1,p) for p,f in maps]
    negative=[];zero=[];positive=[];unknown=[];den=96**2
    for i,j in combinations_with_replacement(range(len(values)),2):
        for mi,(p,f) in enumerate(maps):
            a,b=images[mi][i],images[mi][j]
            n=(4*a*b-(a+b-den)**2)*invD[mi]%p
            if pow(n,(p-1)//2,p)==p-1:
                negative.append([i,j,mi]);break
        else:
            a,b=values[i],values[j]
            t=tuple(x+y-(den if k==0 else 0) for k,(x,y) in enumerate(zip(a,b)))
            numerator=tuple(4*x-y for x,y in zip(mul(a,b)[:8],mul(t,t)[:8]))
            if not any(numerator):zero.append([i,j]);continue
            q=km(tuple(Q(x) for x in numerator),ki(D));roots=square_roots(q)
            if roots:positive.append([i,j,[str(x/den) for x in roots[0]]])
            else:unknown.append([i,j])
    print(json.dumps(dict(radii=len(values),root_counts=counts,pairs=len(negative)+len(zero)+len(positive)+len(unknown),
                         nonsquare=len(negative),zero=len(zero),square=len(positive),unknown=unknown)),flush=True)
    assert not unknown,'Incomplete classification, not a negative theorem'
    used=sorted({m for i,j,m in negative});remap={m:i for i,m in enumerate(used)}
    return dict(schema=1,experiment='E052',core_sha256=hashlib.sha256(raw).hexdigest(),
                pivots=[0,64],root_counts=counts,radius_representatives=list(radii.values()),
                maps=[maps[m] for m in used],nonsquare=[[i,j,remap[m]] for i,j,m in negative],
                zero=zero,square=positive,
                scope='Combined two-root radial spectrum in the specified quadratic extension; not all roots or plane')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=certificate(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
