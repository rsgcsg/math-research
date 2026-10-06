#!/usr/bin/env python3
"""Discovery LP: minimum C030-cost P/R cover of each Q=1 boundary event.

For each certified Q event on the T165 boundary face, solve

    minimize  sum_P a_e + 14 sum_R a_e
    subject to sum_{e active in c} a_e >= 27   for every boundary partition c with Q=1
               a_e >= 0.

Dividing by 27, any solution proves pointwise Q <= sum a_e/27 * event_e.
A value < 189/10 (= 18.9 in the unscaled objective) strictly separates the
C030 target q=7/10 from P=1/27,R=14/27.  This is discovery only: floating LP
output must be rationalized and independently replayed before theorem use.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"research"))
from check_transport_projection import read, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem
from search_sparse_boundary_projection import enumerate_masks, bit_column

CERT = ROOT/"certificates/q_joint_boundary_gap.json"
OUT = ROOT/"fractional_q_pr_cover_search.json"

def require(c,m):
    if not c:
        raise ValueError(m)

def pr_columns(lo,hi,terms):
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    ridx=[j for j,t in enumerate(terms) if t["type"]=="R"]
    pridx=pidx+ridx
    cols=[bit_column(lo,hi,j).astype(np.uint8) for j in pridx]
    return pidx,qidx,ridx,pridx,cols

def unique_pr_rows_for_q(cols,qcol):
    rows=np.flatnonzero(qcol)
    # Pack 78 P/R bits into two uint64 words and deduplicate exact patterns.
    n=len(rows)
    a=np.zeros(n,dtype=np.uint64)
    b=np.zeros(n,dtype=np.uint64)
    for k,col in enumerate(cols):
        vals=col[rows].astype(np.uint64)
        if k<64:
            a |= vals << np.uint64(k)
        else:
            b |= vals << np.uint64(k-64)
    packed=np.empty(n,dtype=[("a","<u8"),("b","<u8")])
    packed["a"]=a; packed["b"]=b
    uniq=np.unique(packed)
    require(len(uniq)>0,"Q has no active boundary row")
    return uniq["a"].copy(),uniq["b"].copy()

def sparse_from_masks(a,b,nvars):
    rr=[]; cc=[]
    for i,(x,y) in enumerate(zip(a.tolist(),b.tolist())):
        z=x
        while z:
            bit=z & -z; cc.append(bit.bit_length()-1); rr.append(i); z^=bit
        z=y
        while z:
            bit=z & -z; cc.append(64+bit.bit_length()-1); rr.append(i); z^=bit
    data=np.ones(len(rr),dtype=np.float64)
    return csc_matrix((data,(rr,cc)),shape=(len(a),nvars))

def solve_one(a,b,cost):
    A=sparse_from_masks(a,b,len(cost))
    # Need A x >= 1. Scale objective in "units of 1/27 target cost":
    # P costs 1, R costs 14.
    res=linprog(c=cost,A_ub=-A,b_ub=-np.ones(A.shape[0]),
                bounds=(0,None),method="highs",
                options={"presolve":True})
    require(res.success and res.x is not None,"HiGHS LP failed: "+str(res.message))
    x=res.x
    slack=A@x
    require(float(slack.min()) >= 1-1e-8,"LP candidate violates a row")
    return res,x,float(slack.min()),A.shape[0],A.nnz

def main():
    cert=read(CERT)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,pb,rb)
    V=cert["boundary"]["vertices"]
    local=geometry(g,sets,V)
    problem=boundary_problem(cert["boundary"],local)
    terms=cert["boundary"]["terms"]
    enumerate_masks.order=cert["boundary"]["order"]
    lo,hi,leaves,_=enumerate_masks(problem,terms)
    pidx,qidx,ridx,pridx,cols=pr_columns(lo,hi,terms)
    cost=np.array([1.0]*len(pidx)+[14.0]*len(ridx))
    results=[]
    for qj in qidx:
        qcol=bit_column(lo,hi,qj).astype(bool)
        a,b=unique_pr_rows_for_q(cols,qcol)
        # A zero P/R mask would prove no positive cover of any cost.
        zero=bool(np.any((a==0)&(b==0)))
        if zero:
            results.append({"Q_pair":terms[qj]["pair"],"cover_exists":False,
                            "unique_Q1_PR_patterns":int(len(a)),
                            "reason":"Q=1 boundary pattern with all P/R events zero"})
            continue
        res,x,mincover,nrows,nnz=solve_one(a,b,cost)
        support=[]
        for k,val in enumerate(x):
            if val>1e-9:
                j=pridx[k]
                support.append({"type":terms[j]["type"],"pair":terms[j]["pair"],
                                "coefficient_float":float(val)})
        objective=float(res.fun)
        results.append({
            "Q_pair":terms[qj]["pair"],"cover_exists":True,
            "objective_units_over_27":objective,
            "target_Q_units_over_27":18.9,
            "strict_against_C030":objective < 18.9-1e-8,
            "support_size":len(support),
            "minimum_row_cover_float":mincover,
            "unique_Q1_PR_patterns":nrows,"matrix_nnz":int(nnz),
            "support":support,
            "solver_status":int(res.status),"solver_message":str(res.message)
        })
    out={"schema":"fractional-q-pr-cover-search-v1","status":"SEARCH_OBSERVATION",
         "boundary_leaves":leaves,"unique_event_patterns":int(len(lo)),
         "results":results,
         "best_objective_units_over_27":min((z["objective_units_over_27"] for z in results if z.get("cover_exists")),default=None),
         "strict_candidates":sum(bool(z.get("strict_against_C030")) for z in results),
         "scope":"Floating HiGHS discovery over all deduplicated T165 boundary P/R patterns for each Q=1 event. Any candidate requires rationalization and an independent exact checker before theorem promotion."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
