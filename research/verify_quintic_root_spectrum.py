"""Independent T088/E051 exhaustive radial-discriminant checker."""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_bridge_contacts import km,divide,RAD


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_root_spectrum.json').read_text())
    assert data['schema']==1 and data['results']==['T088','E051'] and data['pivot']==0
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);assert core['coordinate_denominator']==96
    assert not any(core['points'][0][0]+core['points'][0][1])
    radii={}
    for i,(x,y) in enumerate(core['points']):
        x=tuple(Q(a,96) for a in x);y=tuple(Q(a,96) for a in y)
        n=tuple(a+b for a,b in zip(km(x,x),km(y,y)))
        if any(n):radii.setdefault(n,i)
    assert len(radii)==47 and list(radii.values())==data['radius_representatives']
    values=list(radii);maps=data['maps']
    for p,f in maps:
        assert type(p) is int and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
        assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
        for i,j in combinations_with_replacement(range(8),2):
            g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
            assert f[i]*f[j]%p==g*f[k]%p
    records={}
    for i,j,m in data['nonsquare']:
        assert (i,j) not in records and 0<=m<len(maps);records[i,j]=m
    for i,j in data['zero']:
        assert (i,j) not in records;records[i,j]=None
    assert set(records)==set(combinations_with_replacement(range(47),2))
    assert len(data['nonsquare'])==1126 and len(data['zero'])==2
    D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    for (i,j),m in records.items():
        a,b=values[i],values[j]
        t=tuple(x+y-(1 if k==0 else 0) for k,(x,y) in enumerate(zip(a,b)))
        numerator=tuple(4*x-y for x,y in zip(km(a,b),km(t,t)))
        if m is None:assert not any(numerator);continue
        # Gaussian solve differs from producer's tower inversion.
        q=divide(numerator,D);p,f=maps[m]
        assert all(x.denominator%p for x in q)
        image=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(q,f))%p
        assert pow(image,(p-1)//2,p)==p-1
    return dict(status='PASS',theorem='T088',experiment='E051',nonzero_radii=47,
                radius_pairs=1128,nonsquare_discriminants=1126,zero_discriminants=2,
                scope='No non-pivot unit edges for origin-rooted escaped rotations in this quadratic field; not all roots')


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
