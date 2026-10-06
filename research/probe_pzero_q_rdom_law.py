#!/usr/bin/env python3
"""Discover exact P=0 boundary laws with Q=1 and all R marginals >=14/27.

If such a law exists for a fixed Q, then every nonnegative pointwise cover
  Q <= sum a_P P + sum b_R (1-R)
has C030 target cost at least 1, since its expectation under the law is at
least 1 while E[P]=0 and E[1-R]<=13/27.

This producer fully enumerates P-zero T165 boundary partitions, uses SciPy only
to locate sparse feasible laws, rationalizes them, and exact-checks the candidate.
A separate standard-library verifier must replay published certificates.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
from check_transport_projection import read, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem

CERT=ROOT/"certificates/q_joint_boundary_gap.json"
OUT=ROOT/"pzero_q_rdom_search.json"

def require(c,m):
    if not c: raise ValueError(m)

def enumerate_pzero(cert,local):
    b=cert["boundary"]; problem=boundary_problem(b,local)
    before,members,ends,tri,costs,rhs,sums=problem
    order=b["order"]; ix={v:i for i,v in enumerate(order)}
    terms=b["terms"]
    P=[tuple(t["pair"]) for t in terms if t["type"]=="P"]
    Q=[tuple(t["pair"]) for t in terms if t["type"]=="Q"]
    R=[tuple(t["pair"]) for t in terms if t["type"]=="R"]
    p_at=[[] for _ in order]; q_at=[[] for _ in order]; r_at=[[] for _ in order]
    for pairs,store in ((P,p_at),(Q,q_at),(R,r_at)):
        for j,(a,bp) in enumerate(pairs):
            u,v=sorted((ix[a],ix[bp])); store[v].append((u,j))
    colors=[-1]*len(order); classes=[0]*5
    counts=[[0]*5 for _ in ends]; pc=[0]*len(ends); tri_end=max(tri)
    leaves=[]; nodes=0
    def rec(i,top,qm,rm):
        nonlocal nodes
        nodes+=1
        if i==len(order):
            leaves.append((qm,rm,tuple(colors))); return
        for color in range(min(5,top+2)):
            if before[i]&classes[color]: continue
            colors[i]=color
            if any(colors[a]==color for a,_ in p_at[i]): continue
            if i==tri_end:
                a,o,bp=tri
                if (colors[a]==colors[o])+(colors[bp]==colors[o])-(colors[a]==colors[bp]) != 1:
                    continue
            touched=members[i]
            if any(pc[t]+counts[t][color]>2 or
                   (ends[t]==i and pc[t]+counts[t][color]!=2) for t in touched):
                continue
            for t in touched: pc[t]+=counts[t][color]; counts[t][color]+=1
            classes[color]|=1<<i
            nqm=qm; nrm=rm
            for a,j in q_at[i]:
                if colors[a]==color: nqm|=1<<j
            for a,j in r_at[i]:
                if colors[a]==color: nrm|=1<<j
            rec(i+1,max(top,color),nqm,nrm)
            classes[color]^=1<<i
            for t in touched: counts[t][color]-=1; pc[t]-=counts[t][color]
    rec(0,-1,0,0)
    return P,Q,R,leaves,nodes

def rationalize(xs,den=100000):
    return [F(float(x)).limit_denominator(den) for x in xs]

def solve_q(qi,R,leaves):
    rows=[z for z in leaves if z[0]>>qi&1]
    require(rows,"Q has no P-zero leaf")
    n=len(rows); nr=len(R)
    # weights w: sum w=1, sum w*r_j >=14/27.
    A=np.empty((nr,n),dtype=float)
    for j in range(nr):
        A[j]=[-float((rm>>j)&1) for _,rm,_ in rows]
    res=linprog(c=np.zeros(n),A_ub=A,b_ub=np.full(nr,-14/27),
                A_eq=np.ones((1,n)),b_eq=np.ones(1),bounds=(0,None),method="highs")
    if not res.success:
        return {"feasible":False,"message":str(res.message),"Q1_P0_leaves":n}
    support=[k for k,x in enumerate(res.x) if x>1e-10]
    fr=rationalize([res.x[k] for k in support])
    # Renormalization should be exact already for simple BFS; if not, record discovery failure.
    ok=sum(fr,F(0))==1
    marg=[]
    if ok:
        for j in range(nr):
            v=sum((w for k,w in zip(support,fr) if rows[k][1]>>j&1),F(0))
            marg.append(v)
            if v<F(14,27): ok=False
    atoms=[]
    if ok:
        for k,w in zip(support,fr):
            atoms.append({"weight":[w.numerator,w.denominator],
                          "partition":list(rows[k][2])})
    return {"feasible":True,"exact_rationalized":ok,"Q1_P0_leaves":n,
            "atom_count":len(support),
            "min_R_marginal":[min(marg).numerator,min(marg).denominator] if ok else None,
            "atoms":atoms if ok else [],
            "float_min_R":float(min(sum(res.x[k] for k,z in enumerate(rows) if z[1]>>j&1)
                                      for j in range(nr)))}

def main():
    cert=read(CERT)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,pb,rb)
    local=geometry(g,sets,cert["boundary"]["vertices"])
    P,Q,R,leaves,nodes=enumerate_pzero(cert,local)
    results=[]
    for qi,q in enumerate(Q):
        z=solve_q(qi,R,leaves); z["Q_pair"]=list(q); results.append(z)
    out={"schema":"pzero-q-rdom-search-v1","status":"SEARCH_OBSERVATION",
         "Pzero_boundary_leaves":len(leaves),"enumeration_nodes":nodes,
         "results":results,
         "all_exact_feasible":all(z.get("exact_rationalized") for z in results),
         "scope":"Discovery of exact rational probability laws on actual T165 boundary partitions with all 47 P=0, one named Q=1 almost surely, and every named R marginal >=14/27. Requires independent replay before theorem status."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
