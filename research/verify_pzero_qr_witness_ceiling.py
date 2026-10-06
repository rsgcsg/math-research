#!/usr/bin/env python3
"""Independent replay of the T165 P-zero Q/R witness ceiling.

For every one of the 11 certified Q events and every one of the 31 certified R
events on the T165 saturated boundary face, find a proper <=5-block partition
with Q=R=1 and all 47 P events equal to zero.

This checker is independent of search_sparse_boundary_projection.py and the
NumPy/SciPy producers. It uses only the standard library plus the already
certified geometry/transport reconstruction helpers.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

if not __debug__:
    raise RuntimeError("Verification requires assertions; run without -O")

from check_transport_projection import read, digest, require, verify_geometry_and_components
from verify_q_defect_lifting import geometry
from verify_q_joint_boundary_gap import boundary_problem

ROOT=Path(__file__).resolve().parents[1]
CERT=ROOT/"certificates/q_joint_boundary_gap.json"
OUT=ROOT/"certificates/pzero_qr_witness_ceiling.json"
RECEIPT=ROOT/"certificates/pzero_qr_witness_ceiling_validation.json"

def enumerate_witnesses(cert, local):
    b=cert["boundary"]
    problem=boundary_problem(b,local)
    before,members,ends,tri,costs,rhs,sums=problem
    V=b["vertices"]; order=b["order"]; ix={v:i for i,v in enumerate(order)}
    terms=b["terms"]
    P=[tuple(t["pair"]) for t in terms if t["type"]=="P"]
    Q=[tuple(t["pair"]) for t in terms if t["type"]=="Q"]
    R=[tuple(t["pair"]) for t in terms if t["type"]=="R"]
    require((len(P),len(Q),len(R))==(47,11,31),"event counts")

    # Event lists keyed by later endpoint. P-zero is enforced immediately.
    p_at=[[] for _ in order]; q_at=[[] for _ in order]; r_at=[[] for _ in order]
    for typ,pairs,store in (("P",P,p_at),("Q",Q,q_at),("R",R,r_at)):
        for j,(a,bp) in enumerate(pairs):
            u,v=sorted((ix[a],ix[bp]))
            store[v].append((u,j))

    target={(qi,ri) for qi in range(len(Q)) for ri in range(len(R))}
    found={}
    colors=[-1]*len(order); classes=[0]*5
    counts=[[0]*5 for _ in ends]; pairs_count=[0]*len(ends)
    tri_end=max(tri)
    nodes=leaves=pzero_leaves=0
    qmask=rmask=0

    def visit(i,top,qm,rm):
        nonlocal nodes,leaves,pzero_leaves
        nodes+=1
        if len(found)==len(target):
            return
        if i==len(order):
            leaves+=1; pzero_leaves+=1
            # Record all newly covered Q/R pairs at this leaf.
            qbits=[q for q in range(len(Q)) if qm>>q & 1]
            rbits=[r for r in range(len(R)) if rm>>r & 1]
            for q in qbits:
                for r in rbits:
                    key=(q,r)
                    if key not in found:
                        found[key]=colors.copy()
            return
        for color in range(min(5,top+2)):
            if before[i] & classes[color]:
                continue
            colors[i]=color
            # Enforce all P events unequal: if a P earlier endpoint has this
            # color, the branch can never be a P-zero witness.
            if any(colors[a]==color for a,_ in p_at[i]):
                continue
            if i==tri_end:
                a,o,bp=tri
                if (colors[a]==colors[o])+(colors[bp]==colors[o])-(colors[a]==colors[bp]) != 1:
                    continue
            touched=members[i]
            if any(pairs_count[t]+counts[t][color] > 2 or
                   (ends[t]==i and pairs_count[t]+counts[t][color] != 2)
                   for t in touched):
                continue
            for t in touched:
                pairs_count[t]+=counts[t][color]; counts[t][color]+=1
            classes[color] |= 1<<i
            nqm=qm; nrm=rm
            for a,j in q_at[i]:
                if colors[a]==color: nqm |= 1<<j
            for a,j in r_at[i]:
                if colors[a]==color: nrm |= 1<<j
            visit(i+1,max(top,color),nqm,nrm)
            classes[color] ^= 1<<i
            for t in touched:
                counts[t][color]-=1; pairs_count[t]-=counts[t][color]
            if len(found)==len(target):
                break

    visit(0,-1,0,0)
    require(len(found)==341,"all 11x31 Q/R pairs have P-zero witness")

    # Directly replay every stored witness from scratch.
    unit=set(local["E"]); windows=b["saturated_windows"]; tri_vs=b["PRR_triple"]
    witnesses=[]
    for qi in range(len(Q)):
        for ri in range(len(R)):
            c=found[(qi,ri)]
            require(len(c)==len(order) and max(c)<5 and min(c)>=0,"five colors")
            col={v:c[ix[v]] for v in order}
            require(all(col[a]!=col[bp] for a,bp in unit),"proper actual unit graph")
            require(all(col[a]!=col[bp] for a,bp in P),"all P zero")
            require(col[Q[qi][0]]==col[Q[qi][1]],"chosen Q one")
            require(col[R[ri][0]]==col[R[ri][1]],"chosen R one")
            for w in windows:
                h=sum(col[a]==col[bp] for x,a in enumerate(w) for bp in w[x+1:])
                require(h==2,"saturated window")
            a,o,bp=tri_vs
            require((col[a]==col[o])+(col[bp]==col[o])-(col[a]==col[bp])==1,
                    "PRR equality")
            witnesses.append({"Q_pair":list(Q[qi]),"R_pair":list(R[ri]),"partition":c})
    witness_bytes=json.dumps(witnesses,sort_keys=True,separators=(",",":")).encode()
    return {
        "schema":"pzero-qr-witness-ceiling-v1",
        "research_id":"T174",
        "source_certificate_sha256":digest(cert),
        "event_counts":{"P":47,"Q":11,"R":31},
        "pair_witnesses":len(witnesses),
        "enumeration_nodes_until_complete":nodes,
        "complete_Pzero_leaves_visited_until_complete":pzero_leaves,
        "canonical_witness_list_sha256":hashlib.sha256(witness_bytes).hexdigest(),
        "example_witness":witnesses[0],
        "scope":"For every named Q and named R event on the exact T165 saturated boundary face, there is an actual proper <=5-block W22 partition with that Q=R=1 and all 47 named P events zero. Hence no pointwise inequality Q+R<=1+sum a_P P with nonnegative coefficients can hold on this face, regardless of support size or weights. This does not rule out inequalities using multiple R events, negative coefficients, off-face lifting, full-Y constraints, or full15."
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write",action="store_true")
    args=ap.parse_args()
    cert=read(CERT)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,sizes=verify_geometry_and_components(g,pb,rb)
    V=cert["boundary"]["vertices"]
    local=geometry(g,sets,V)
    report=enumerate_witnesses(cert,local)
    validation={"schema":"pzero-qr-witness-ceiling-validation-v1","status":"PASS",
                "certificate_sha256":digest(report),"transport_components":sizes,
                "pair_witnesses":report["pair_witnesses"],
                "enumeration_nodes_until_complete":report["enumeration_nodes_until_complete"],
                "complete_Pzero_leaves_visited_until_complete":report["complete_Pzero_leaves_visited_until_complete"],
                "scope":report["scope"]}
    if args.write:
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        RECEIPT.write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n")
    else:
        require(read(OUT)==report,"deterministic witness certificate")
        require(read(RECEIPT)==validation,"deterministic validation receipt")
    print(json.dumps(validation,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()