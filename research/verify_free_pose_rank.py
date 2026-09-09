"""Independent rational minors and all-pairs quadratic geometry for T062."""
from fractions import Fraction as F
from itertools import combinations,permutations
from pathlib import Path
import json


def determinant(matrix):
    # Leibniz expansion shares no elimination algorithm with the generator.
    n=len(matrix);answer=F(0)
    for p in permutations(range(n)):
        term=F((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))
        for i,j in enumerate(p):term*=matrix[i][j]
        answer+=term
    return answer


def verify(root):
    data=json.loads((root/'certificates/free_pose_rank.json').read_text())
    assert data['schema']==1 and data['variables']==['T','tx','ty','ux','uy','c','s']
    decode=lambda seq:[F(*a) for a in seq]
    mul=lambda a,b:(a[0]*b[0]+2*a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    add=lambda a,b:tuple(x+y for x,y in zip(a,b))
    sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
    results=[]
    for case in data['cases']:
        old=list(map(decode,case['old_points']));template=list(map(decode,case['template_points']))
        lift=list(map(decode,case['lift']));T,tx,ty,ux,uy,c,s=lift
        assert add(mul(c,c),mul(s,s))==(1,0)
        assert tuple(T)==add(mul(tx,tx),mul(ty,ty))
        assert tuple(ux)==add(mul(c,tx),mul(s,ty))
        assert tuple(uy)==sub(mul(c,ty),mul(s,tx))
        points=[((x,F(0)),(y,F(0))) for x,y in old]
        for x,y in template:
            points.append((add(sub(mul(c,(x,0)),mul(s,(y,0))),tx),
                           add(add(mul(s,(x,0)),mul(c,(y,0))),ty)))
        den=case['coordinate_denominator']
        assert points==[tuple(tuple(F(a,den) for a in ax) for ax in p) for p in case['actual_points']]
        assert len(points)==len(set(points))
        edges=[]
        for i,j in combinations(range(len(points)),2):
            dx,dy=[sub(a,b) for a,b in zip(points[i],points[j])]
            if add(mul(dx,dx),mul(dy,dy))==(1,0):edges.append([i,j])
        assert edges==case['induced_edges']
        cross=[[i,j-len(old)] for i,j in edges if i<len(old)<=j]
        assert cross==case['cross_edges']
        rows=[];rhs=[]
        for i,j in cross:
            x,y=old[i];a,b=template[j]
            rows.append([1,-2*x,-2*y,2*a,2*b,-2*x*a-2*y*b,2*x*b-2*y*a])
            rhs.append(1-x*x-y*y-a*a-b*b)
        assert rows==list(map(decode,case['rows'])) and rhs==decode(case['rhs'])
        for row,target in zip(rows,rhs):
            result=(F(0),F(0))
            for coefficient,value in zip(row,lift):result=add(result,mul((coefficient,0),value))
            assert result==(target,0)
        chosen=case['minor_rows'];cols=case['minor_columns'];rank=case['rank']
        assert len(chosen)==len(cols)==rank and len(set(chosen))==rank and len(set(cols))==rank
        minor=determinant([[rows[i][j] for j in cols] for i in chosen]);assert minor
        if rank==6:
            null=decode(case['nullvector']);particular=decode(case['particular'])
            assert null==[0,1,0,1,0,0,0] and particular==[F(8,9),0,0,0,0,1,0]
            assert all(sum(a*b for a,b in zip(row,null))==0 for row in rows)
            assert all(sum(a*b for a,b in zip(row,particular))==t for row,t in zip(rows,rhs))
            assert lift==[[a,F(2,3)*b] for a,b in zip(particular,null)]
            assert 2 not in {1,3,5,11,15,33,55,165} # K's rational square-root classes, proved in T060.
        else:assert rank==7 and all(value[1]==0 for value in lift)
        results.append(dict(rank=rank,vertices=len(points),all_pairs=len(points)*(len(points)-1)//2,
                            induced_edges=len(edges),cross_edges=len(cross),minor=str(minor)))
    assert [r['rank'] for r in results]==[7,6]
    return dict(status='PASS',cases=results,scope='General rank-six/seven theorem uses the written arbitrary-field proof')


if __name__=='__main__':
    if not __debug__:raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
