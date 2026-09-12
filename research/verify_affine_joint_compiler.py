"""Exact small calibration of T105; not a five-color obstruction."""
from fractions import Fraction as Q
from itertools import product,combinations


def verify():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    # Q(a,b), a^2=3 and b^2=a/2; basis 1,a,b,ab.
    def mul(x,y):
        out=[Q(0)]*4
        for i,u in enumerate(x):
            for j,v in enumerate(y):
                aa=(i%2)+(j%2);bb=(i//2)+(j//2);c=u*v
                if bb>=2:bb-=2;aa+=1;c/=2
                while aa>=2:aa-=2;c*=3
                out[aa+2*bb]+=c
        return tuple(out)
    zero=(Q(0),)*4;one=(Q(1),)+zero[1:]
    def scalar(x):return (Q(x),)+zero[1:]
    def add(x,y):return tuple(a+b for a,b in zip(x,y))
    def sub(x,y):return tuple(a-b for a,b in zip(x,y))
    def unit(p,q):
        a=sub(p[0],q[0]);b=sub(p[1],q[1]);return add(mul(a,a),mul(b,b))==one
    a=(Q(0),Q(1),Q(0),Q(0));b=(Q(0),Q(0),Q(1),Q(0))
    half_a=tuple(x/2 for x in a);ten=scalar(10)
    X=[(zero,zero),(half_a,scalar(Q(1,2))),(a,zero),
       (ten,zero),(scalar(11),zero),
       (add(ten,tuple(x/2 for x in add(a,one))),b),(add(ten,a),zero)]
    edges=[(i,j) for i,j in combinations(range(7),2) if unit(X[i],X[j])]
    assert edges==[(0,1),(1,2),(3,4),(4,5),(5,6)]
    proper=0
    for word in product(range(2),repeat=7):
        if any(word[i]==word[j] for i,j in edges):continue
        proper+=1;assert int(word[0]==word[2])-int(word[3]==word[6])==1
    assert proper==4
    Y=sorted({(add(p[0],scalar(10*(n+m))),tuple(sign*x for x in p[1]))
              for n,m in product(range(-1,2),repeat=2) for sign in (-1,1) for p in X})
    five=[(zero,zero),(half_a,scalar(Q(1,2))),(a,zero),
          (tuple(x/2 for x in add(a,one)),b),(one,zero)]
    assert all(p in Y for p in five)
    assert all(unit(five[i],five[(i+1)%5]) for i in range(5))
    y_edges=sum(unit(p,q) for p,q in combinations(Y,2))
    # A nontrivial orientation-box test: d=s=N=B=1, m=6.
    # Right composition adds (-1)^epsilon to the orientation exponent, toggles
    # reflection if requested, and adds the source orientation's basis vector.
    orientations=list(product(range(-1,2),range(2)));oid={u:i for i,u in enumerate(orientations)}
    indices=list(product(product(range(-1,2),repeat=6),orientations))
    for toggle in (0,1):
        targets=set();paired=0
        for n,(v,reflection) in indices:
            dest=(v+(-1)**reflection,reflection^toggle)
            if dest not in oid:continue
            new=list(n);new[oid[(v,reflection)]]+=1
            if max(new)>1:continue
            target=(tuple(new),dest);assert target not in targets;targets.add(target);paired+=1
        assert paired==1944 and len(indices)==4374
        assert Q(len(indices)-paired,len(indices))<=Q(1,3)+Q(1,3)
    return dict(status='PASS',theorem='T105',scope='Two-color exact compiler calibration; no HN lower bound',
                input_vertices=7,input_edges=5,proper_input_words=4,strict_margin=1,
                compiled_vertices=len(Y),compiled_unit_edges=y_edges,odd_cycle=5,
                indexed_pairing_total=4374,indexed_paired=1944)


if __name__=='__main__':
    import json
    print(json.dumps(verify(),indent=2))
