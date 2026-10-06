"""Exact finite component of the sharp 9/10 three-column concentration bound.

This checks the complete 3x3 ternary vertex classification, not a sample.
The polyhedral reduction and its application to HN are in the written proof.
"""
from itertools import product
from fractions import Fraction


def determinant(a):
    if len(a)==1:return a[0][0]
    if len(a)==2:return a[0][0]*a[1][1]-a[0][1]*a[1][0]
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def enumerate_vertices(n):
    best=Fraction(0);count=invertible=nonnegative=0;witness=None
    for a in product(tuple(product((-1,0,1),repeat=n)),repeat=n):
        count+=1;d=determinant(a)
        if not d:continue
        invertible+=1
        x=tuple(Fraction(determinant([[1 if k==j else a[i][k] for k in range(n)] for i in range(n)]),d) for j in range(n))
        if min(x)<0:continue
        nonnegative+=1
        if sum(x)>best:best=sum(x);witness=(a,x)
    return dict(dimension=n,matrices=count,invertible=invertible,nonnegative_vertices=nonnegative,
                maximum_sum=str(best),witness_matrix=[list(r) for r in witness[0]],witness_x=list(map(str,witness[1])))


def check():
    result=[enumerate_vertices(n) for n in (1,2,3)]
    assert [x['maximum_sum'] for x in result]==['1','3','9']
    a=[[-1,0,1],[0,1,-1],[1,-1,1]]
    weights=[2,4,3,1]
    columns=[list(x) for x in zip(*a)]+[[-1,-1,-1]]
    assert all(sum(weights[j]*columns[j][i] for j in range(4))==0 for i in range(3))
    assert abs(determinant(a))==1
    # Rank three and strictly positive null vector give a unique four-atom
    # law; in particular no solution on at most three of these four columns.
    return dict(status='PASS',enumerations=result,sharp_abstract_columns=columns,
                sharp_abstract_weights=['1/5','2/5','3/10','1/10'],
                scope='Sharp abstract {-1,0,1} balance-system bound, not a claim of attainment by Y.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('verification requires assertions')
    import json
    print(json.dumps(check(),indent=2))
