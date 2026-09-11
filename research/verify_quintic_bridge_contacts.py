"""Independent T086/E048 checker: all contacts with an infinite K plane.

No producer, square-extraction, or SAT imports. Negative square claims use
verified split-prime maps. Positive roots and the finite interface are exact.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_core_probe import geometry,multiplication_twice,product_twice,conjugate_twice

RAD=(1,3,11,33,5,15,55,165)


def km(a,b):
    out=[Q(0)]*8
    for i,x in enumerate(a):
        if not x: continue
        for j,y in enumerate(b):
            if y:
                g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
                out[k]+=g*x*y
    return tuple(out)


def divide(a,b):
    # Solve multiplication by b using rational Gaussian elimination, not
    # the producer's recursive conjugate-norm inverse.
    columns=[km(b,tuple(Q(i==j) for i in range(8))) for j in range(8)]
    matrix=[[columns[j][i] for j in range(8)]+[a[i]] for i in range(8)]
    for col in range(8):
        pivot=next(i for i in range(col,8) if matrix[i][col])
        matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
        factor=matrix[col][col];matrix[col]=[x/factor for x in matrix[col]]
        for i in range(8):
            if i!=col:
                factor=matrix[i][col]
                matrix[i]=[x-factor*y for x,y in zip(matrix[i],matrix[col])]
    result=tuple(row[-1] for row in matrix)
    assert km(result,b)==a
    return result


def context(root):
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    assert core['coordinate_denominator']==96
    table=multiplication_twice()
    old,copies,owners,edges,_,_,_=geometry(core,[0,153,150],table)
    old=[tuple(Q(x,96) for x in p) for p in old]
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    def multiply(a,b): return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def conjugate(a): return tuple(Q(x)/2 for x in conjugate_twice(a))
    def subtract(a,b): return tuple(x-y for x,y in zip(a,b))
    a,b=old[84],old[337];u,v=base[332],base[451]
    inverse=(Q(3,2),Q(0),Q(0),Q(0),Q(3,10))+(Q(0),)*27
    rotation=multiply(multiply(subtract(b,a),conjugate(subtract(v,u))),inverse)
    assert multiply(rotation,conjugate(rotation))==(Q(1),)+(Q(0),)*31
    records=[]
    alpha=(Q(-1,4),Q(0),Q(0),Q(0),Q(1,4),Q(0),Q(0),Q(0))
    D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    s=[Q(0)]*32;s[8]=-1;s[12]=1;s[24]=-4
    assert multiply(s,s)==D+(Q(0),)*24
    for x in old:
        c=tuple(xx+yy for xx,yy in zip(u,multiply(conjugate(rotation),subtract(x,a))))
        ax=tuple(x+y for x,y in zip(c[:8],km(alpha,c[16:24])))
        ay=tuple(x+y for x,y in zip(c[8:16],km(alpha,c[24:])))
        bx=tuple(-x/4 for x in c[24:]);by=tuple(x/4 for x in c[16:24])
        A=ax+ay+(Q(0),)*16;B=bx+by+(Q(0),)*16
        assert tuple(x+y for x,y in zip(A,multiply(s,B)))==c
        e=tuple(x+y for x,y in zip(km(bx,bx),km(by,by)))
        q=tuple(x-y for x,y in zip(e,km(D,km(e,e))))
        records.append((ax,ay,bx,by,e,q))
    return core,old,base,edges,records,rotation,multiply,conjugate


def verify(root,certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_bridge_contacts.json').read_text())
    assert data['schema']==1 and data['results']==['T086','E048']
    assert set(data['sources'])=={'parts509_core.json','quintic_core_probe.json'}
    for name,digest in data['sources'].items():
        assert hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()==digest
    core,old,base,edges,records,rotation,multiply,conjugate=context(root)
    assert len(old)==2033 and len(edges)==10169
    maps=data['maps']
    for p,f in maps:
        assert isinstance(p,int) and p>165 and all(p%d for d in range(2,math.isqrt(p)+1))
        assert len(f)==8 and f[0]==1 and all(type(x) is int and 0<=x<p for x in f)
        for i,j in combinations(range(8),2):
            g=math.gcd(RAD[i],RAD[j]);k=RAD.index(RAD[i]*RAD[j]//(g*g))
            assert f[i]*f[j]%p==g*f[k]%p
        assert all(f[i]*f[i]%p==RAD[i]%p for i in range(8))
    inside=data['inside'];negative=data['nonsquare'];roots=data['roots']
    ids=inside+[i for i,m in negative]+[i for i,r in roots]
    assert sorted(ids)==list(range(2033))
    assert inside==[84,337,1016,1592] and len(negative)==1941 and len(roots)==88
    for i in inside:
        assert not any(records[i][2]+records[i][3]) and not any(records[i][4])
    for i,m in negative:
        assert any(records[i][4]) and 0<=m<len(maps)
        q=records[i][5];p,f=maps[m]
        assert all(x.denominator%p for x in q)
        image=sum(x.numerator*pow(x.denominator,-1,p)*y for x,y in zip(q,f))%p
        assert pow(image,(p-1)//2,p)==p-1
    neighbors={};interface={(records[i][0],records[i][1]) for i in inside}
    one=(Q(1),)+(Q(0),)*7;D=(Q(10),Q(0),Q(0),Q(0),Q(2),Q(0),Q(0),Q(0))
    for i,raw_root in roots:
        r=tuple(Q(x) for x in raw_root)
        ax,ay,bx,by,e,q=records[i]
        assert len(r)==8 and any(e) and km(r,r)==q
        scale=divide(r,e);dx=km(scale,by);dy=km(scale,bx)
        neighbors[i]=[(tuple(x-sign*y for x,y in zip(ax,dx)),tuple(x+sign*y for x,y in zip(ay,dy))) for sign in (-1,1)]
        for x,y in neighbors[i]:
            wx=tuple(u-v for u,v in zip(x,ax));wy=tuple(u-v for u,v in zip(y,ay))
            assert not any(u+v for u,v in zip(km(wx,bx),km(wy,by)))
            assert tuple(u+v+w for u,v,w in zip(km(wx,wx),km(wy,wy),km(D,e)))==one
            interface.add((x,y))
    images=data['residue_images']
    assert images==[1,5,0,0,4,9,0,0]
    def reduced(point):
        assert all(x.denominator%11 for axis in point for x in axis)
        return tuple(sum(x.numerator*pow(x.denominator,-1,11)*v for x,v in zip(axis,images))%11 for axis in point)
    assert len(interface)==data['interface_points']==81
    reduced_points={p:reduced(p) for p in interface}
    target=data['residue_word'];word=data['old_word']
    assert len(target)==121 and set(target)==set('01234')
    assert len(word)==2033 and set(word)==set('01234')
    assert all(word[i]!=word[j] for i,j in edges)
    assert all(target[i]!=target[j] for i,j in combinations(range(121),2)
               if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1)
    def color(p):
        x,y=reduced_points[p];return target[11*x+y]
    assert all(word[i]==color((records[i][0],records[i][1])) for i in inside)
    assert all(word[i]!=color(p) for i,points in neighbors.items() for p in points)
    assert len({(i,reduced_points[p]) for i,points in neighbors.items() for p in points})==data['contact_edges']==176
    return dict(status='PASS',theorem='T086',experiment='E048',inside=4,nonsquare_exclusions=1941,
                outside_points_with_contacts=88,interface_points=81,contact_edges=176,
                infinite_host_chromatic_number=5,
                scope='X union Phi(K squared), not the whole plane or full congruence joint feasibility')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
