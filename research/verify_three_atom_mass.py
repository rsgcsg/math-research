"""Exact, exhaustive ternary-matrix step in the sharp three-atom mass bound."""
from fractions import Fraction
from itertools import combinations, product
import json


def determinant(a):
    # Explicit 3x3 integer formula, no numerical linear algebra.
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def verify():
    rows=[r for r in product((-1,0,1),repeat=3) if any(r)]
    checked=0;positive=0;maximum=Fraction(0);attainers=[]
    for matrix in combinations(rows,3):
        checked+=1;den=determinant(matrix)
        if not den:continue
        solution=[]
        for j in range(3):
            replaced=[[1 if col==j else row[col] for col in range(3)] for row in matrix]
            solution.append(Fraction(determinant(replaced),den))
        if not all(x>0 for x in solution):continue
        if any(sum(a*x for a,x in zip(row,solution))!=1 for row in matrix):
            raise ValueError('Cramer solution failed direct multiplication')
        positive+=1;total=sum(solution)
        if total>maximum:maximum=total;attainers=[]
        if total==maximum:attainers.append([list(r) for r in matrix])
    if (checked,positive,maximum,len(attainers))!=(2600,108,9,6):
        raise ValueError('exhaustive bound mismatch')
    sharp=[[-1,0,1,-1],[0,1,-1,-1],[1,-1,1,-1]]
    weights=[2,4,3,1]
    if determinant([r[:3] for r in sharp])==0 or any(sum(x*y for x,y in zip(r,weights)) for r in sharp):
        raise ValueError('sharp example rank/kernel')
    return dict(status='PASS',row_triples=checked,positive_solutions=positive,
                maximum_inverse_ones_sum=str(maximum),attainers=attainers,
                sharp_weights=['1/5','2/5','3/10','1/10'],mass_bound='9/10',
                scope='Ternary balance systems with no law on at most three columns; no geometric realization claimed.')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Verification requires assertions')
    print(json.dumps(verify(),sort_keys=True))
