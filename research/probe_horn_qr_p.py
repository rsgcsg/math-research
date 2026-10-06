#!/usr/bin/env python3
"""Discovery: exact Horn separators Q+R <= 1 + sum_{P in S} P on T165 face.

For each of 11 Q and 31 R events, enumerate every certified boundary event
pattern with Q=R=1 and find a minimum P hitting set up to size 5.  A hit set S
proves the pointwise Boolean inequality

    x_Q + x_R <= 1 + sum_{P in S} x_P.

At the C030 target (p,q,r)=(1/27,7/10,14/27), every k<=5 is a strict
separator because (13+k)/27 < 7/10.  This producer is exact on the enumerated
T165 boundary patterns but remains a search observation until a separate
checker re-enumerates the claimed candidate.
"""
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
from check_transport_projection import read, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem
from search_sparse_boundary_projection import enumerate_masks, bit_column, small_p_cover_from_masks

CERT=ROOT/"certificates/q_joint_boundary_gap.json"
OUT=ROOT/"horn_qr_p_search.json"

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
    cols=[bit_column(lo,hi,j).astype(bool) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    ridx=[j for j,t in enumerate(terms) if t["type"]=="R"]
    pcode=np.zeros(len(lo),dtype=np.uint64)
    for pos,j in enumerate(pidx):
        pcode |= cols[j].astype(np.uint64) << np.uint64(pos)
    candidates=[]; impossible=[]; audited=0
    for qj in qidx:
        for rj in ridx:
            rows=cols[qj] & cols[rj]
            masks=np.unique(pcode[rows])
            audited+=1
            if len(masks)==0:
                # antecedent never occurs: Q+R<=1 already valid, k=0.
                chosen_pos=[]
            elif np.any(masks==0):
                impossible.append({"Q_pair":terms[qj]["pair"],"R_pair":terms[rj]["pair"],
                                   "reason":"Q=R=1 pattern with all P=0",
                                   "antecedent_patterns":int(np.count_nonzero(rows))})
                continue
            else:
                chosen_pos=small_p_cover_from_masks(masks,5)
                if chosen_pos is None:
                    continue
            chosen=[pidx[pos] for pos in chosen_pos]
            # Independent replay on every unique 89-event pattern.
            lhs=cols[qj].astype(np.int16)+cols[rj].astype(np.int16)
            rhs=np.ones(len(lo),dtype=np.int16)
            for j in chosen: rhs += cols[j]
            require(np.all(lhs<=rhs),"candidate Horn inequality invalid")
            k=len(chosen)
            candidates.append({
                "Q_pair":terms[qj]["pair"],"R_pair":terms[rj]["pair"],
                "P_count":k,
                "P_pairs":[terms[j]["pair"] for j in chosen],
                "antecedent_unique_P_patterns":int(len(masks)),
                "antecedent_event_patterns":int(np.count_nonzero(rows)),
                "C030_rhs":[13+k,27],
                "C030_q":[7,10],
                "strict_against_C030":10*(13+k)<189
            })
    candidates.sort(key=lambda z:(z["P_count"],z["Q_pair"],z["R_pair"],z["P_pairs"]))
    out={
      "schema":"horn-qr-p-search-v1","status":"SEARCH_OBSERVATION",
      "boundary_leaves":leaves,"unique_event_patterns":int(len(lo)),
      "audited_QR_pairs":audited,
      "candidates":candidates,
      "strict_candidates":sum(z["strict_against_C030"] for z in candidates),
      "best_P_count":candidates[0]["P_count"] if candidates else None,
      "P0_impossible_pairs":len(impossible),
      "sample_impossible":impossible[:20],
      "scope":"Exact exhaustive discovery on all unique T165 boundary event patterns. Candidate inequalities require an independent checker before theorem promotion."
    }
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
