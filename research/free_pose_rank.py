"""Exact calibration of seven-coordinate free planar-motion contact equations.

Generator only. The arbitrary-field and rank-six conclusions require the proof.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
import math

ROOT=Path(__file__).resolve().parents[1]


def contact_row(p,q):
    x,y=p;a,b=q
    return [F(1),-2*x,-2*y,2*a,2*b,-2*(x*a+y*b),2*(x*b-y*a)]


def row_basis(rows):
    basis={};selected=[]
    for i,row in enumerate(rows):
        work=list(row)
        for col,pivot in sorted(basis.items()):
            factor=work[col];work=[a-factor*b for a,b in zip(work,pivot)]
        col=next((j for j,a in enumerate(work) if a),None)
        if col is not None:
            factor=work[col];basis[col]=[a/factor for a in work];selected.append(i)
    return selected,sorted(basis)


def case(name,old,moving,c,s,translation,lift,nullvector=None,particular=None):
    # Translation axes have coefficients in 1,sqrt(2); all template points are rational.
    actual=[((c*x-s*y+translation[0][0],translation[0][1]),
             (s*x+c*y+translation[1][0],translation[1][1])) for x,y in moving]
    base=[((x,F(0)),(y,F(0))) for x,y in old]
    points=base+actual
    assert len(set(points))==len(points)
    den=math.lcm(*(a.denominator for p in points for ax in p for a in ax))
    points=[[[int(a*den) for a in ax] for ax in p] for p in points]
    def unit(p,q):
        a=b=0
        for ax,bx in zip(p,q):
            u,v=[x-y for x,y in zip(ax,bx)]
            a+=u*u+2*v*v;b+=2*u*v
        return (a,b)==(den*den,0)
    edges=[(i,j) for i,j in combinations(range(len(points)),2) if unit(points[i],points[j])]
    cross=[(i,j-len(old)) for i,j in edges if i<len(old)<=j]
    rows=[contact_row(old[i],moving[j]) for i,j in cross]
    rhs=[1-sum(a*a for a in old[i])-sum(a*a for a in moving[j]) for i,j in cross]
    chosen,cols=row_basis(rows)
    encode=lambda seq:[[a.numerator,a.denominator] for a in seq]
    result=dict(name=name,old_points=[encode(p) for p in old],template_points=[encode(p) for p in moving],
                coordinate_denominator=den,actual_points=points,induced_edges=edges,cross_edges=cross,
                rank=len(chosen),minor_rows=chosen,minor_columns=cols,
                rows=[encode(r) for r in rows],rhs=encode(rhs),lift=[encode(ax) for ax in lift])
    if nullvector is not None:
        result['nullvector']=encode(nullvector);result['particular']=encode(particular)
    return result


def build():
    moving=[tuple(map(F,p)) for p in ((0,0),(3,0),(0,4),(5,2))]
    c,s=F(3,5),F(4,5);tx,ty=F(2,7),F(-1,7)
    old=[(c*x-s*y+tx+u,s*x+c*y+ty+v) for x,y in moving
         for u,v in ((F(1),F(0)),(F(0),F(1)),(F(3,5),F(4,5)))]
    rational=[tx*tx+ty*ty,tx,ty,c*tx+s*ty,-s*tx+c*ty,c,s]
    full=case('rank_seven_rational_pose',old,moving,c,s,((tx,F(0)),(ty,F(0))),[(a,F(0)) for a in rational])
    assert full['rank']==7
    moving=[tuple(map(F,p)) for p in ((0,0),(1,0),(0,1),(1,1),(2,1))]
    old=[(x,y+h) for x,y in moving for h in (F(-1,3),F(1,3))]
    lift=[(F(8,9),F(0)),(F(0),F(2,3)),(F(0),F(0)),(F(0),F(2,3)),
          (F(0),F(0)),(F(1),F(0)),(F(0),F(0))]
    sharp=case('rank_six_no_common_K_point',old,moving,F(1),F(0),((F(0),F(2,3)),(F(0),F(0))),lift,
               list(map(F,(0,1,0,1,0,0,0))),list(map(F,(F(8,9),0,0,0,0,1,0))))
    assert sharp['rank']==6
    return dict(schema=1,variables=['T','tx','ty','ux','uy','c','s'],cases=[full,sharp],
                scope='Rank thresholds for arbitrary free rigid motions; calibration graphs are not high-chromatic claims')


if __name__=='__main__':
    data=build();(ROOT/'certificates/free_pose_rank.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps([dict(name=r['name'],rank=r['rank'],vertices=len(r['actual_points']),cross_edges=len(r['cross_edges'])) for r in data['cases']]))
