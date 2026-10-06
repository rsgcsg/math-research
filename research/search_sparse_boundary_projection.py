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
    pbits=[i for i,t in enumerate(terms) if t["type"]=="P"]
    qbits=[i for i,t in enumerate(terms) if t["type"]=="Q"]
    p_lo_mask=sum(1<<i for i in pbits if i<64)
    p_hi_mask=sum(1<<(i-64) for i in pbits if i>=64)
    p0_q_witness={}
    leaves=0
    def visit(i,top,mask_lo,mask_hi):
        nonlocal leaves
        if i==n:
            require(leaves<expected,"more leaves than pinned T165 count")
            lo[leaves]=mask_lo; hi[leaves]=mask_hi
            if (mask_lo & p_lo_mask)==0 and (mask_hi & p_hi_mask)==0:
                for bit in qbits:
                    on=((mask_lo>>bit)&1) if bit<64 else ((mask_hi>>(bit-64))&1)
                    if on and bit not in p0_q_witness:
                        p0_q_witness[bit]=colors.copy()
            leaves+=1
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
    return uniq["lo"].copy(), uniq["hi"].copy(), leaves, p0_q_witness

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


def greedy_q_by_p_covers(lo,hi,terms):
    """Discovery: try q_e <= sum_{p in S} p with |S|<=18."""
    cols=[bit_column(lo,hi,j).astype(bool) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    found=[]
    for qj in qidx:
        uncovered=cols[qj].copy()
        chosen=[]
        available=set(pidx)
        while uncovered.any() and len(chosen)<19:
            best=None; bestgain=0
            for j in available:
                gain=int(np.count_nonzero(uncovered & cols[j]))
                if gain>bestgain:
                    bestgain=gain; best=j
            if best is None or bestgain==0:
                break
            chosen.append(best); available.remove(best)
            uncovered &= ~cols[best]
        if not uncovered.any() and len(chosen)<=18:
            # Exact validity replay over every unique event pattern.
            lhs=cols[qj].astype(np.int16)
            rhs=np.zeros(len(lo),dtype=np.int16)
            for j in chosen: rhs += cols[j]
            require(np.all(lhs<=rhs),"greedy Q-by-P cover validity")
            found.append({
                "Q_pair":terms[qj]["pair"],
                "P_count":len(chosen),
                "target_rhs":[len(chosen),27],
                "strict_against_q_7_10": F(len(chosen),27) < F(7,10),
                "P_pairs":[terms[j]["pair"] for j in chosen],
            })
    found.sort(key=lambda z:(z["P_count"],z["Q_pair"]))
    return found


def exact_q_by_p_cover_milp(lo,hi,terms):
    """Exact minimum-cardinality P cover of every boundary pattern with Q_e=1.

    Discovery uses scipy.milp.  A later proof checker must independently certify
    any claimed optimum before promotion to a theorem.
    """
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import csr_matrix
    cols=[bit_column(lo,hi,j).astype(bool) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    # Pack the 47 P coordinates into uint64 once.
    pcode=np.zeros(len(lo),dtype=np.uint64)
    for pos,j in enumerate(pidx):
        pcode |= cols[j].astype(np.uint64) << np.uint64(pos)
    ans=[]
    for qj in qidx:
        masks=np.unique(pcode[cols[qj]])
        if np.any(masks==0):
            ans.append({"Q_pair":terms[qj]["pair"],"cover_exists":False,
                        "reason":"Q=1 boundary pattern with all 47 P events zero"})
            continue
        # Inclusion-minimal row masks suffice: hitting a subset also hits every superset.
        ints=sorted((int(x) for x in masks),key=lambda z:(z.bit_count(),z))
        minimal=[]
        for m in ints:
            if not any((s & m)==s for s in minimal):
                minimal.append(m)
        rows=[]; cols_ix=[]
        for i,m in enumerate(minimal):
            z=m
            while z:
                bit=z & -z; cols_ix.append(bit.bit_length()-1); rows.append(i); z^=bit
        A=csr_matrix((np.ones(len(rows),dtype=float),(rows,cols_ix)),
                     shape=(len(minimal),len(pidx)))
        res=milp(c=np.ones(len(pidx)),integrality=np.ones(len(pidx)),
                 bounds=Bounds(np.zeros(len(pidx)),np.ones(len(pidx))),
                 constraints=LinearConstraint(A,np.ones(len(minimal)),
                                               np.full(len(minimal),np.inf)),
                 options={"time_limit":120.0})
        require(res.success and res.x is not None,"exact P-cover MILP failed")
        chosen=[pidx[i] for i,x in enumerate(res.x) if x>0.5]
        # Direct integer replay against every Q=1 pattern.
        hit=np.zeros(len(lo),dtype=bool)
        for j in chosen: hit |= cols[j]
        require(np.all(hit[cols[qj]]),"MILP P-cover candidate misses Q=1 pattern")
        ans.append({"Q_pair":terms[qj]["pair"],"cover_exists":True,
                    "minimum_P_count":len(chosen),
                    "violates_C030":F(len(chosen),27)<F(7,10),
                    "P_pairs":[terms[j]["pair"] for j in chosen],
                    "unique_Q1_P_patterns":int(len(masks)),
                    "minimal_hitting_constraints":len(minimal),
                    "solver_status":int(res.status),
                    "solver_message":str(res.message)})
    return ans


def small_p_cover_from_masks(mask_values, max_depth=4):
    """Exact branch search for a hitting set of at most max_depth P bits."""
    masks=sorted(set(int(x) for x in mask_values),key=lambda z:(z.bit_count(),z))
    if not masks:
        return []
    if masks[0]==0:
        return None
    def rec(active,depth,chosen):
        if not active:
            return chosen
        if depth==0:
            return None
        pivot=min(active,key=lambda z:z.bit_count())
        z=pivot
        while z:
            bit=z & -z
            nxt=[m for m in active if not (m & bit)]
            ans=rec(nxt,depth-1,chosen+[bit.bit_length()-1])
            if ans is not None:
                return ans
            z^=bit
        return None
    for d in range(max_depth+1):
        ans=rec(masks,d,[])
        if ans is not None:
            return ans
    return None

def exact_q_by_one_r_four_p(lo,hi,terms):
    """Exhaust Q <= R + up to four P candidates exactly over boundary patterns."""
    cols=[bit_column(lo,hi,j).astype(bool) for j in range(len(terms))]
    pidx=[j for j,t in enumerate(terms) if t["type"]=="P"]
    qidx=[j for j,t in enumerate(terms) if t["type"]=="Q"]
    ridx=[j for j,t in enumerate(terms) if t["type"]=="R"]
    pcode=np.zeros(len(lo),dtype=np.uint64)
    for pos,j in enumerate(pidx):
        pcode |= cols[j].astype(np.uint64) << np.uint64(pos)
    found=[]
    audited=0
    eligible_summary=[]
    for qj in qidx:
        p0rows=cols[qj] & (pcode==0)
        require(np.any(p0rows),"expected Q=1,P=0 witness")
        eligible=[rj for rj in ridx if np.all(cols[rj][p0rows])]
        eligible_summary.append({"Q_pair":terms[qj]["pair"],
                                 "P0_pattern_count":int(np.count_nonzero(p0rows)),
                                 "eligible_R_count":len(eligible),
                                 "eligible_R_pairs":[terms[rj]["pair"] for rj in eligible]})
        for rj in eligible:
            rows=cols[qj] & ~cols[rj]
            masks=np.unique(pcode[rows])
            audited+=1
            chosen_pos=small_p_cover_from_masks(masks,4)
            if chosen_pos is None:
                continue
            chosen=[pidx[pos] for pos in chosen_pos]
            lhs=cols[qj].astype(np.int16)
            rhs=cols[rj].astype(np.int16)
            for j in chosen: rhs += cols[j]
            require(np.all(lhs<=rhs),"one-R/four-P cover validity")
            cost=14+len(chosen)
            found.append({
                "Q_pair":terms[qj]["pair"],"R_pair":terms[rj]["pair"],
                "P_count":len(chosen),"integer_target_cost_over_27":cost,
                "violates_C030":cost*10 < 7*27,
                "P_pairs":[terms[j]["pair"] for j in chosen],
            })
    found.sort(key=lambda z:(z["integer_target_cost_over_27"],z["Q_pair"],z["R_pair"]))
    return {"audited_QR_pairs_after_P0_filter":audited,
            "P0_R_eligibility":eligible_summary,"found":found}

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
    lo,hi,leaves,p0_q_witness=enumerate_masks(problem,terms)
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
    q_by_p=greedy_q_by_p_covers(lo,hi,terms)
    exact_q_by_p=exact_q_by_p_cover_milp(lo,hi,terms)
    one_r_four_p=exact_q_by_one_r_four_p(lo,hi,terms)
    out={"schema":"sparse-boundary-projection-search-v1","status":"SEARCH_OBSERVATION",
         "boundary_leaves":leaves,"unique_event_patterns":len(lo),
         "best":results[0],"all_runs":[{k:v for k,v in z.items() if k!="terms"} for z in results],
         "q_P0_witnesses":[{"Q_pair":terms[j]["pair"],"partition":p0_q_witness[j]}
                            for j in sorted(p0_q_witness)],
         "q_by_p_covers":q_by_p,
         "exact_q_by_p_covers":exact_q_by_p,
         "q_by_one_r_four_p":one_r_four_p,
         "scope":"Producer observation only until independently replayed. Coefficients are a subset of the certified T165 separator with omitted coefficients set to zero; rhs is recomputed by exhaustive boundary enumeration."}
    OUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    main()