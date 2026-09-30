#!/usr/bin/env python3
"""Solver-free calibration of cyclic-interval kernels and chorded-cycle cuts."""
import argparse
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')


def partitions(n):
    def rec(a,top):
        if len(a)==n:
            yield tuple(a)
            return
        for c in range(top+2):
            yield from rec(a+[c],max(c,top))
    yield from rec([0],0)


def check_case(n,q):
    assert 2<=q and 2*q<=n
    intervals=[{(a+j)%n for j in range(q)} for a in range(n)]
    Q=[[F(sum(i in a and j in a for a in intervals),q)
        for j in range(n)] for i in range(n)]
    k=(n+q-1)//q
    weights=[F(1,k*q)]*n+[1-F(n,k*q)]
    atoms=intervals+[set()]
    assert all(w>=0 for w in weights) and sum(weights)==1
    edges={(i,j) for i,j in combinations(range(n),2) if q<=j-i<=n-q}
    assert all(not any(i in a and j in a for i,j in edges) for a in atoms)
    means=[sum(w*(i in a) for w,a in zip(weights,atoms)) for i in range(n)]
    assert means==[F(1,k)]*n
    for i in range(n):
        assert Q[i][i]==1 and sum(Q[i])==q
        for j in range(n):
            assert 0<=Q[i][j]<=1
            assert Q[i][j]==k*sum(w*(i in a)*(j in a) for w,a in zip(weights,atoms))
            # Exact covariance Gram factorization proves PSD, without numerical eigenvalues.
            covariance=k*sum(w*(F(i in a)-F(1,k))*(F(j in a)-F(1,k))
                             for w,a in zip(weights,atoms))
            assert Q[i][j]-F(1,k)==covariance
            cut_distance=F(k,2)*sum(w*abs(int(i in a)-int(j in a)) for w,a in zip(weights,atoms))
            assert 1-Q[i][j]==cut_distance
    assert all(Q[i][j]==0 for i,j in edges)
    for i,j,h in combinations(range(n),3):
        assert Q[i][j]+Q[j][h]-Q[i][h]<=1
        assert Q[i][j]+Q[i][h]-Q[j][h]<=1
        assert Q[i][h]+Q[j][h]-Q[i][j]<=1
    lhs=sum(Q[i][(i+1)%n]-Q[i][(i+q)%n] for i in range(n))
    rhs=n-(n+q-1)//q
    assert lhs==F(n*(q-1),q)
    assert (lhs>rhs)==(n%q!=0)
    if n%q==0:
        laws=[]
        for shift in range(q):
            labels=[None]*n
            for j in range(n//q):
                for s in range(q):labels[(shift+j*q+s)%n]=j
            laws.append(labels)
        assert all(len(set(z))==n//q for z in laws)
        for i in range(n):
            for j in range(n):
                assert Q[i][j]==F(sum(z[i]==z[j] for z in laws),q)
    # Ordinary graph coloring exists even when its specified Q has no partition law.
    coloring=[i//q for i in range(n)]
    assert len(set(coloring))==k and all(coloring[i]!=coloring[j] for i,j in edges)
    subset_checks=0
    if n<=9:
        for mask in range(1<<n):
            S=[i for i in range(n) if mask>>i&1]
            a,b=divmod(len(S),k)
            lower=k*a*(a-1)//2+b*a
            assert sum(Q[i][j] for i,j in combinations(S,2))>=lower
            subset_checks+=1
    return dict(n=n,q=q,k=k,partition_kernel=(n%q==0),
                chorded_cycle_lhs=str(lhs),chorded_cycle_bound=rhs,
                fractional_gap=str(lhs-rhs),subset_checks=subset_checks)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true')
    args=ap.parse_args()
    cases=[check_case(n,q) for n in range(4,21) for q in range(2,n//2+1)]
    exhaustive=[]
    for n in range(4,10):
        parts=list(partitions(n))
        for q in range(2,n//2+1):
            scores=[sum(int(z[i]==z[(i+1)%n])-int(z[i]==z[(i+q)%n])
                        for i in range(n)) for z in parts]
            bound=n-(n+q-1)//q
            assert max(scores)==bound
            exhaustive.append(dict(n=n,q=q,partitions=len(parts),maximum=max(scores),bound=bound))
    report=dict(schema='cyclic-interval-kernel-v1',status='PASS_EXACT_SMALL_CASE_CALIBRATION',
                cases=cases,exhaustive_partition_checks=exhaustive,
                scope='Finite calibration only. The arbitrary-n,q theorem follows from the written chorded-cycle proof and explicit offset partition construction. No plane realization except the separately certified C027 case is asserted.')
    path=Path(__file__).resolve().parents[1]/'certificates/cyclic_interval_kernel.json'
    if args.write_receipt:path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    else:assert json.loads(path.read_text())==report,'Saved receipt differs from exact replay'
    print(json.dumps(dict(status=report['status'],kernel_cases=len(cases),
                         positive_cases=sum(c['partition_kernel'] for c in cases),
                         strict_counterexamples=sum(not c['partition_kernel'] for c in cases),
                         exhaustive_partition_evaluations=sum(c['partitions'] for c in exhaustive))))


if __name__=='__main__':
    main()
