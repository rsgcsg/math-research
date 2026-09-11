"""Independent E052 checker; no search-side arithmetic or square extraction."""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_bridge_contacts import km,RAD


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_shifted_spectrum.json').read_text())
    assert data['schema']==1 and data['experiment']=='E052' and data['pivots']==[0,64]
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);assert core['coordinate_denominator']==96
    radii={};counts=[]
    for pivot in data['pivots']:
        local=set()
        for i,(x,y) in enumerate(core['points']):
            dx=tuple(Q(a-b) for a,b in zip(x,core['points'][pivot][0]))
            dy=tuple(Q(a-b) for a,b in zip(y,core['points'][pivot][1]))
            n=tuple(a+b for a,b in zip(km(dx,dx),km(dy,dy)))
            if any(n):local.add(n);radii.setdefault(n,[pivot,i])
        counts.append(len(local))
    assert counts==data['root_counts']==[47,214]
    assert len(radii)==217 and list(radii.values())==data['radius_representatives']
    values=list(radii);maps=data['maps'];images=[]
    for p,f in maps:
        assert type(p) is int and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
        assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
        for i,j in combinations_with_replacement(range(8),2):
            g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
            assert f[i]*f[j]%p==g*f[k]%p
        assert (10+2*f[4])%p and 96%p
        images.append([sum(int(x)*y for x,y in zip(n,f))%p for n in values])
    records={}
    for i,j,m in data['nonsquare']:
        assert (i,j) not in records and 0<=m<len(maps);records[i,j]=m
    for i,j in data['zero']:
        assert (i,j) not in records;records[i,j]=None
    assert not data['square']
    assert len(data['nonsquare'])==23649 and len(data['zero'])==4
    assert set(records)==set(combinations_with_replacement(range(217),2))
    for (i,j),mi in records.items():
        if mi is None:
            a,b=values[i],values[j]
            t=tuple(x+y-(9216 if k==0 else 0) for k,(x,y) in enumerate(zip(a,b)))
            assert km(t,t)==tuple(4*x for x in km(a,b))
        else:
            p,f=maps[mi];a,b=images[mi][i],images[mi][j]
            # Delta=(4ab-(a+b-den)^2)/(den^2 D). den^2 is a square.
            residue=(4*a*b-(a+b-9216)**2)*pow(10+2*f[4],-1,p)%p
            assert pow(residue,(p-1)//2,p)==p-1
    return dict(status='PASS',experiment='E052',theorem='T089',radii=217,pairs=23653,
                nonsquare=23649,zero=4,scope='Two-root shell host only; no bound for the plane')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
