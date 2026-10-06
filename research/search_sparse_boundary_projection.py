#!/usr/bin/env python3
"""Discovery search for a sparse identity-sensitive separator on the T165 face.

This is a producer, not a proof checker.  It enumerates every canonical boundary
partition exactly as the independent T165 verifier does, records its 89-event
bit vector, then greedily deletes coefficients from the certified T165
separator while preserving strict separation of the C030 target.

If a candidate is found, the JSON output is intended to be independently
replayed by a separate verifier before any theorem claim.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research"))
from check_transport_projection import read, pair, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem

CERT = ROOT / "certificates/q_joint_boundary_gap.json"
OUT = ROOT / "sparse_boundary_projection_search.json"

def require(c,m):
    if not c: raise ValueError(m)

def enumerate_masks(problem, terms, expected=5648160):
    before, members, ends, tri, costs, rhs, sums = problem
    n=len(before); colors=[-1]*n; classes=[0]*5
    counts=[[0]*5 for _ in ends]; pairs=[0]*len(ends)
    tri_end=max(tri)
    # event bit is added when its later endpoint is colored
    event_at=[[] for _ in range(n)]
    # boundary_problem order is encoded in term pairs through cert outside;
    # rebuild using the same order supplied by caller in term entries.
    order = enumerate_masks.order
    ix={v:i for i,v in enumerate(order)}
    for bit,t in enumerate(terms):
        a,b=sorted((ix[t["pair"][0]],ix[t["pair"][1]]))
        event_at[b].append((a,bit))
    lo=np.empty(expected,dtype=np.uint64)
    hi=np.empty(expected,dtype=np.uint64)
    leaves=0
    def visit(i,top,mask_lo,mask_hi):
        nonlocal leaves
        if i==n:
            require(leaves<expected,"more leaves than pinned T165 count")
            lo[leaves]=mask_lo; hi[leaves]=mask_hi; leaves+=1
            return
        for color in range(min(5,top+2)):
            if before[i] & classes[color]: continue
            colors[i]=color
            if i==tri_end:
                a,o,b=tri
                if (colors[a]==colors[o])+(colors[b]==colors[o])-(colors[a]==colors[b]) != 1:
                    continue
            touched=members[i]
            if any(pairs[t]+counts[t][color] > 2 or
                   (ends[t]==i and pairs[t]+counts[t][color] != 2) for t in touched):
                continue
            for t in touched:
                pairs[t]+=counts[t][color]; counts[t][color]+=1
            classes[color] |= 1<<i
            nl=mask_lo; nh=mask_hi
            for a,bit in event_at[i]:
                if colors[a]==color:
                    if bit<64: nl |= 1<<bit
                    else: nh |= 1<<(bit-64)
            visit(i+1,max(top,color),nl,nh)
            classes[color] ^= 1<<i
            for t in touched:
                counts[t][color]-=1; pairs[t]-=counts[t][color]
    visit(0,-1,0,0)
    require(leaves==expected,"pinned boundary leaf count")
    # Deduplicate event patterns only; multiplicities do not affect separation.
    packed=np.empty(expected,dtype=[("lo","<u8"),("hi","<u8")])
    packed["lo"]=lo; packed["hi"]=hi
    uniq=np.unique(packed)
    return uniq["lo"].copy(), uniq["hi"].copy(), leaves

def bit_column(lo,hi,j):
    if j<64: return ((lo >> np.uint64(j)) & np.uint64(1)).astype(np.int64)
    return ((hi >> np.uint64(j-64)) & np.uint64(1)).astype(np.int64)

def greedy(lo,hi,coeff,target,order):
    bits=[bit_column(lo,hi,j) for j in range(len(coeff))]
    scores=np.zeros(len(lo),dtype=np.int64)
    for j,a in enumerate(coeff):
        if a: scores += a*bits[j]
    support={j for j,a in enumerate(coeff) if a}
    tscore=sum(F(a)*target[j] for j,a in enumerate(coeff))
    require(int(scores.max())==2 and tscore>2,"replay full separator")
    for j in order:
        if j not in support: continue
        a=coeff[j]
        trial=scores-a*bits[j]
        mt=int(trial.max())
        tt=tscore-F(a)*target[j]
        if tt>mt:
            scores=trial; tscore=tt; support.remove(j)
    return support, tscore, int(scores.max()), tscore-int(scores.max())

def main():
    cert=read(CERT)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    b=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    r=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,b,r)
    V=cert["boundary"]["vertices"]
    local=geometry(g,sets,V)
    problem=boundary_problem(cert["boundary"],local)
    terms=cert["boundary"]["terms"]
    enumerate_masks.order=cert["boundary"]["order"]
    lo,hi,leaves=enumerate_masks(problem,terms)
    coeff=[t["coefficient"] for t in terms]
    target=[F(1,27) if t["type"]=="P" else F(7,10) if t["type"]=="Q" else F(14,27)
            for t in terms]

    nonzero=[j for j,a in enumerate(coeff) if a]
    orders=[
      sorted(nonzero,key=lambda j:(abs(coeff[j]),j)),
      sorted(nonzero,key=lambda j:(coeff[j]>0,abs(coeff[j]),j)),
      sorted(nonzero,key=lambda j:(coeff[j]<0,abs(coeff[j]),j)),
      sorted(nonzero,key=lambda j:(abs(coeff[j])*float(target[j]),j)),
    ]
    results=[]
    for q,ordr in enumerate(orders):
        S,ts,rhs,margin=greedy(lo,hi,coeff,target,ordr)
        rows=[{"type":terms[j]["type"],"pair":terms[j]["pair"],"coefficient":coeff[j]}
              for j in sorted(S)]
        results.append({"order":q,"support_size":len(S),
                        "target_score":[ts.numerator,ts.denominator],
                        "rhs":rhs,"margin":[margin.numerator,margin.denominator],
                        "terms":rows})
    results.sort(key=lambda x:(x["support_size"],-F(*x["margin"])))
    out={"schema":"sparse-boundary-projection-search-v1","status":"SEARCH_OBSERVATION",
         "boundary_leaves":leaves,"unique_event_patterns":len(lo),
         "best":results[0],"all_runs":[{k:v for k,v in z.items() if k!="terms"} for z in results],
         "scope":"Producer observation only until independently replayed. Coefficients are a subset of the certified T165 separator with omitted coefficients set to zero; rhs is recomputed by exhaustive boundary enumeration."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()
