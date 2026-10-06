#!/usr/bin/env python3
"""Discovery LP for Q <= weighted P + weighted (1-R) on the T165 boundary face.

For each Q event, use the exact set of boundary event patterns and solve

    minimize  sum_P a_e + 13 sum_R b_e
    subject to sum_{P active} a_e + sum_{R inactive} b_e >= 27
               a_e,b_e >= 0.

After division by 27 the RHS target cost at C030 is
sum a_e*(1/27) + sum b_e*(1-14/27).
Thus objective < 189/10 (=18.9) strictly separates q=7/10.
This is discovery only. Any positive candidate must be rationalized and
independently replayed before theorem status.
"""
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
from check_transport_projection import read, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem
from search_sparse_boundary_projection import enumerate_masks, bit_column

CERT=ROOT/"certificates/q_joint_boundary_gap.json"
OUT=ROOT/"fractional_q_p_notr_cover_search.json"

def require(c,m):
    if not c: raise ValueError(m)

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
    cols=[bit_column(lo,hi,j).astype(np.uint8) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    ridx=[j for j,t in enumerate(terms) if t["type"]=="R"]
    results=[]
    for qj in qidx:
        rows=np.flatnonzero(cols[qj])
        # Matrix columns: P indicators, then complement-R indicators.
        raw=np.column_stack([c[rows] for c in [cols[j] for j in pidx]]+
                            [1-cols[j][rows] for j in ridx]).astype(np.uint8)
        # Deduplicate constraints; dominance is left to HiGHS presolve.
        raw=np.unique(raw,axis=0)
        if np.any(raw.sum(axis=1)==0):
            results.append({"Q_pair":terms[qj]["pair"],"cover_exists":False,
                            "reason":"Q=1 row with all P=0 and all R=1",
                            "unique_constraints":int(len(raw))})
            continue
        A=csc_matrix(raw,dtype=float)
        cost=np.array([1.0]*len(pidx)+[13.0]*len(ridx))
        res=linprog(c=cost,A_ub=-A,b_ub=-np.ones(len(raw)),
                    bounds=(0,None),method="highs")
        require(res.success and res.x is not None,"LP failed "+str(res.message))
        require(float((A@res.x).min())>=1-1e-8,"LP violation")
        support=[]
        for k,x in enumerate(res.x):
            if x<=1e-9: continue
            if k<len(pidx):
                j=pidx[k]; typ="P"
            else:
                j=ridx[k-len(pidx)]; typ="notR"
            support.append({"type":typ,"pair":terms[j]["pair"],"coefficient_float":float(x)})
        val=float(res.fun)
        results.append({"Q_pair":terms[qj]["pair"],"cover_exists":True,
                        "objective_units_over_27":val,
                        "strict_against_C030":val<18.9-1e-8,
                        "support_size":len(support),
                        "unique_constraints":int(len(raw)),
                        "support":support})
    good=[z for z in results if z.get("strict_against_C030")]
    out={"schema":"fractional-q-p-notr-cover-search-v1","status":"SEARCH_OBSERVATION",
         "boundary_leaves":leaves,"unique_event_patterns":int(len(lo)),
         "results":results,"strict_candidates":len(good),
         "best":min(results,key=lambda z:z.get("objective_units_over_27",1e99)) if results else None,
         "scope":"Floating HiGHS discovery on exact T165 boundary patterns. Variables are nonnegative P indicators and complements of R indicators. Any strict candidate requires exact rational replay."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
