#!/usr/bin/env python3
"""Discovery LP: cover each Q_i by P, other-Q defects, and R defects.

For fixed Q_i, solve over the exact T165 boundary patterns with Q_i=1:

  Q_i <= sum a_P P + sum_{j!=i} b_j (1-Q_j) + sum c_R (1-R),

with nonnegative coefficients. At C030, in units of 1/270, the costs are
10 per unit P, 81 per unit (1-Q), and 130 per unit (1-R); Q_i costs 189.
Any optimum <189 is a strict identity-sensitive separator candidate.

Floating discovery only; candidates require rational exact replay.
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
OUT=ROOT/"fractional_q_p_notq_notr_cover_search.json"

def require(c,m):
    if not c: raise ValueError(m)

def main():
    cert=read(CERT)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,pb,rb)
    local=geometry(g,sets,cert["boundary"]["vertices"])
    problem=boundary_problem(cert["boundary"],local)
    terms=cert["boundary"]["terms"]
    enumerate_masks.order=cert["boundary"]["order"]
    lo,hi,leaves,_=enumerate_masks(problem,terms)
    cols=[bit_column(lo,hi,j).astype(np.uint8) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    ridx=[j for j,t in enumerate(terms) if t["type"]=="R"]
    results=[]
    for qi,qj in enumerate(qidx):
        rows=np.flatnonzero(cols[qj])
        varmeta=[]; arr=[]
        for j in pidx:
            arr.append(cols[j][rows]); varmeta.append(("P",j))
        for k,j in enumerate(qidx):
            if k==qi: continue
            arr.append(1-cols[j][rows]); varmeta.append(("notQ",j))
        for j in ridx:
            arr.append(1-cols[j][rows]); varmeta.append(("notR",j))
        raw=np.column_stack(arr).astype(np.uint8)
        raw=np.unique(raw,axis=0)
        if np.any(raw.sum(axis=1)==0):
            results.append({"Q_pair":terms[qj]["pair"],"cover_exists":False,
                            "reason":"Q_i=1 pattern with P=0 and every other Q=R=1",
                            "unique_constraints":int(len(raw))})
            continue
        costs=np.array([10.0 if typ=="P" else 81.0 if typ=="notQ" else 130.0
                        for typ,_ in varmeta])
        A=csc_matrix(raw,dtype=float)
        res=linprog(c=costs,A_ub=-A,b_ub=-np.ones(len(raw)),
                    bounds=(0,None),method="highs")
        require(res.success and res.x is not None,"LP failed "+str(res.message))
        require(float((A@res.x).min())>=1-1e-8,"LP violation")
        support=[]
        for k,x in enumerate(res.x):
            if x<=1e-9: continue
            typ,j=varmeta[k]
            support.append({"type":typ,"pair":terms[j]["pair"],"coefficient_float":float(x)})
        val=float(res.fun)
        results.append({"Q_pair":terms[qj]["pair"],"cover_exists":True,
                        "objective_units_over_270":val,
                        "strict_against_C030":val<189-1e-8,
                        "margin_units_over_270":189-val,
                        "support_size":len(support),
                        "unique_constraints":int(len(raw)),
                        "support":support})
    good=[z for z in results if z.get("strict_against_C030")]
    out={"schema":"fractional-q-p-notq-notr-cover-search-v1","status":"SEARCH_OBSERVATION",
         "boundary_leaves":leaves,"unique_event_patterns":int(len(lo)),
         "strict_candidates":len(good),
         "best":min(results,key=lambda z:z.get("objective_units_over_270",1e99)) if results else None,
         "results":results,
         "scope":"Floating HiGHS discovery over exact T165 boundary patterns. Literals: P, complements of the other ten Q events, complements of R. Any strict candidate needs independent exact replay."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
