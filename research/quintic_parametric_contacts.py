"""Search-side finite split-prime cover for all angles in a four-copy family.

r=c+i sqrt(D)d, c,d in K, c^2+Dd^2=1, d != 0. For each
p+2kc and r(q+2lc), separate the K and sqrt(D) coefficients.
No root-finding failure is a negative certificate.
"""
from pathlib import Path
from itertools import product
import argparse
import hashlib
import json
from quintic_core_probe import mul
from quintic_shifted_spectrum import split_maps

ZERO=(0,)*8
ONE=(1,)+(0,)*7


def add(*vectors):return tuple(sum(items) for items in zip(*vectors))
def scale(a,n):return tuple(n*x for x in a)
def times(a,b):return tuple(mul(a,b)[:8])
def evaluate(poly,z):
    out=ZERO
    for a in reversed(poly):out=add(scale(out,z),a)
    return out


def remove_endpoints(poly):
    poly=list(poly)
    while len(poly)>1 and not any(poly[-1]):poly.pop()
    if not any(poly[0]) and len(poly)==1:return []
    for z in (-1,1):
        while len(poly)>1 and not any(evaluate(poly,z)):
            quotient=[poly[-1]]
            for a in reversed(poly[1:-1]):quotient.append(add(a,scale(quotient[-1],z)))
            poly=list(reversed(quotient))
    return poly


def certificate(root):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    points=[(tuple(a),tuple(b)) for a,b in core['points']]
    maps=split_maps();projections=[];square_sets=[]
    for p,f in maps:
        projections.append([(sum(x*y for x,y in zip(a,f))%p,sum(x*y for x,y in zip(b,f))%p) for a,b in points])
        square_sets.append({i*i%p for i in range(p)})
    Dinv=[pow(10+2*f[4],-1,p) for p,f in maps]
    universal=[];unresolved=[];counts={};used=set()
    norms=[add(times(x,x),times(y,y)) for x,y in points]
    for k,l in ((0,0),(1,0),(1,1)):
        stats=dict(linear_cover=0,constant_sine=0,endpoints=0,polynomial_cover=0,universal=0,unresolved=0)
        for i,j in product(range(509),repeat=2):
            # The common pivot belongs to both hosts, not a cross-interface point.
            # Retain it here: universal identities are explicitly classified.
            x,y=points[i];u,v=points[j]
            L1=scale(add(scale(y,l),scale(v,-k)),192)
            if any(L1):
                for mi,(p,f) in enumerate(maps):
                    xx,yy=projections[mi][i];uu,vv=projections[mi][j]
                    lead=192*(l*yy-k*vv)%p
                    if not lead:continue
                    c=(xx*vv-yy*uu)*pow(lead,-1,p)%p
                    a=(xx+192*k*c)%p;b=(uu+192*l*c)%p
                    val=(a*a+yy*yy+b*b+vv*vv-2*c*(a*b+yy*vv)-9216)%p
                    if val or (1-c*c)*Dinv[mi]%p not in square_sets[mi]:
                        stats['linear_cover']+=1;used.add(mi);break
                else:
                    L0=add(times(y,u),scale(times(x,v),-1))
                    if L0==L1 or L0==scale(L1,-1):stats['endpoints']+=1
                    else:unresolved.append([k,l,i,j]);stats['unresolved']+=1
                continue
            L0=add(times(y,u),scale(times(x,v),-1))
            if any(L0):stats['constant_sine']+=1;continue
            poly=[add(norms[i],norms[j],scale(ONE,-9216)),
                  add(scale(add(scale(x,k),scale(u,l)),384),scale(add(times(x,u),times(y,v)),-2)),
                  add(scale(ONE,36864*(k*k+l*l)),scale(add(scale(u,k),scale(x,l)),-384)),
                  scale(ONE,-73728*k*l)]
            poly=remove_endpoints(poly)
            if not poly:
                universal.append([k,l,i,j]);stats['universal']+=1;continue
            if len(poly)==1:stats['endpoints']+=1;continue
            for mi,(p,f) in enumerate(maps):
                coefficients=[sum(x*y for x,y in zip(a,f))%p for a in poly]
                if not coefficients[-1]:continue
                def possible(c):
                    value=0
                    for a in reversed(coefficients):value=(value*c+a)%p
                    return value==0 and (1-c*c)*Dinv[mi]%p in square_sets[mi]
                if not any(possible(c) for c in range(p)):
                    stats['polynomial_cover']+=1;used.add(mi);break
            else:unresolved.append([k,l,i,j]);stats['unresolved']+=1
        counts[f'{k},{l}']=stats
        print(json.dumps(dict(type=[k,l],**stats)),flush=True)
    # The only residual is 8c^2(1-c)=1. Its exact factorization, the
    # excluded c=1/2, and the two admitted cosines are checked separately.
    assert unresolved==[[1,1,0,0]],'Unclassified pairs remain; no family theorem'
    for value in counts.values():value['exact_exception']=value.pop('unresolved')
    cosines=[['1/4','0','0','0',s,'0','0','0'] for s in ('1/4','-1/4')]
    used=sorted(used)
    return dict(schema=1,experiment='E054',core_sha256=hashlib.sha256(raw).hexdigest(),
                maps=[maps[i] for i in used],universal=universal,exceptional_pairs=unresolved,
                exceptional_cosines=cosines,counts=counts,
                scope='Only r=c+i sqrt(D)d with c,d in K, d nonzero; not all rotations or hosts')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=certificate(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(universal=len(data['universal']),exceptional=data['exceptional_pairs'])))
