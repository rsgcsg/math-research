"""Exact manuscript coordinates for the external Ducz-Varga G29 certificate.

Real tower basis: sqrt(3)^a sqrt(11)^b sqrt(5)^c t^d, a,b,c,d in {0,1},
t^2=(415+79 sqrt(33))/8. The tower has degree 16: its first three radicals
are independent square classes, and t^2 has a negative real conjugate, so
cannot be a square in the totally real multiquadratic base. No floating point
or unpickling of the external SymPy-object array is used.
"""
from fractions import Fraction as F
from itertools import combinations


def scalar(x=0):
    return (F(x),)+(F(0),)*15


def radical(bit):
    return tuple(F(i==bit) for i in range(16))


def add(a,b):
    return tuple(x+y for x,y in zip(a,b))


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def mul(a,b):
    out=[F(0)]*16
    for i,x in enumerate(a):
        if not x:
            continue
        for j,y in enumerate(b):
            if not y:
                continue
            common=i&j
            factor=(3 if common&1 else 1)*(11 if common&2 else 1)*(5 if common&4 else 1)
            value=x*y*factor
            index=i^j
            if common&8:
                out[index]+=value*F(415,8)
                factor33=(3 if index&1 else 1)*(11 if index&2 else 1)
                out[index^3]+=value*F(79,8)*factor33
            else:
                out[index]+=value
    return tuple(out)


ZERO=scalar()
ONE=scalar(1)


def cmul(a,b):
    return sub(mul(a[0],b[0]),mul(a[1],b[1])),add(mul(a[0],b[1]),mul(a[1],b[0]))


def cadd(*points):
    x=y=ZERO
    for a,b in points:
        x,y=add(x,a),add(y,b)
    return x,y


def scale(point,x):
    return tuple(v*F(x) for v in point[0]),tuple(v*F(x) for v in point[1])


def vertices():
    w=(scalar(F(1,2)),tuple(x*F(1,2) for x in radical(1)))
    rho=(scalar(F(5,6)),tuple(x*F(1,6) for x in radical(2)))
    wr=cmul(w,rho)
    one=(ONE,ZERO)
    # The coordinate matrix printed in Ducz 2606.12325v1, Theorem 3.2 proof.
    rows=[
        [1,0,2,2,1,2,1,1,1,0,3,3,1,2,2,1,0,0,0,3,2,3,1,2,1,2,3],
        [4,4,3,3,3,3,4,2,3,4,3,2,3,3,2,3,2,3,2,0,1,1,1,1,2,2,1],
        [2,3,0,1,2,2,2,3,3,3,0,1,1,1,2,2,3,3,4,1,1,1,2,2,2,2,0],
        [0,0,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,4]]
    base=[cadd(scale(one,a),scale(w,b),scale(rho,c),scale(wr,d)) for a,b,c,d in zip(*rows)]
    p=cadd(scale(one,3),scale(w,F(17,8)),scale(rho,F(-7,8)),scale(wr,2),
           cmul((radical(4),ZERO),cadd(scale(one,F(-1,4)),scale(w,F(1,8)),
                                     scale(rho,F(-1,8)),scale(wr,F(1,4)))))
    q=cadd(scale(one,F(11,4)),scale(w,F(13,8)),scale(rho,F(-1,8)),scale(wr,2),
           scale(cmul((ZERO,radical(8)),cadd(scale(w,-1),rho,wr)),F(1,8)))
    # The supplementary archive puts p,q before the 27 base vertices.
    return [p,q]+base


def geometry():
    assert mul(radical(8),radical(8))==add(scalar(F(415,8)),tuple(x*F(79,8) for x in radical(3)))
    assert F(415,8)**2-33*F(79,8)**2 == -527
    pts=vertices()
    assert len(pts)==len(set(pts))==29
    distances={}
    edges=[]
    for i,j in combinations(range(29),2):
        dx,dy=sub(pts[i][0],pts[j][0]),sub(pts[i][1],pts[j][1])
        distances[i,j]=add(mul(dx,dx),mul(dy,dy))
        if distances[i,j]==ONE:
            edges.append((i,j))
    return pts,distances,edges
