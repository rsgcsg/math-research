#!/usr/bin/env python3
"""Probe the exact T165 zero-defect face for matching/Q synchronization.

This is a discovery probe, not a theorem verifier. It reconstructs the actual
W22 unit graph and P/Q/R transport classes from pinned certificates, then
enumerates all canonical proper <=5-color partitions satisfying the seven
saturated-window equalities and the PRR triangle equality.

It records:
  * all actual unit edges, separating the 31 window edges from the 3 external ones;
  * the exact Q-count histogram and feasible 11-bit Q masks;
  * the exact joint signatures of Q masks with the two same-color pairs selected
    in each saturated K7 window.

No optimizer is used in this probe.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from check_transport_projection import read, verify_geometry_and_components, pair
from verify_q_defect_lifting import geometry

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()

    cert=read(SOURCE)
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    b=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    r=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,b,r)
    V=cert["boundary"]["vertices"]
    local=geometry(g,sets,V)

    order=cert["boundary"]["order"]
    ix={v:i for i,v in enumerate(order)}
    windows=cert["boundary"]["saturated_windows"]
    cores=[sorted(ix[v] for v in w) for w in windows]
    memberships=[[t for t,w in enumerate(cores) if i in w] for i in range(len(V))]
    ends=[w[-1] for w in cores]
    tri=[ix[v] for v in cert["boundary"]["PRR_triple"]]

    unit_before=[0]*len(V)
    for a,b in local["E"]:
        i,j=sorted((ix[a],ix[b]))
        unit_before[j] |= 1<<i

    window_pairs=set()
    for W in windows:
        for i,a in enumerate(W):
            for bb in W[i+1:]:
                window_pairs.add(pair(a,bb))
    external_unit=sorted(e for e in local["E"] if e not in window_pairs)

    q_index={pair(a,b):i for i,(a,b) in enumerate(local["Q"])}
    q_before=[[] for _ in V]
    for e,qi in q_index.items():
        a,b=e; i,j=sorted((ix[a],ix[b]))
        q_before[j].append((i,qi))

    colors=[-1]*len(V)
    classes=[0]*5
    counts=[[0]*5 for _ in windows]
    paircounts=[0]*len(windows)
    nodes=leaves=0
    q_hist=Counter()
    q_masks=Counter()
    signatures=Counter()
    matching_edge_counts=Counter()

    def visit(i,top,qmask):
        nonlocal nodes,leaves
        nodes += 1
        if i==len(V):
            leaves += 1
            q_hist[qmask.bit_count()] += 1
            q_masks[qmask] += 1
            selected=[]
            for wi,W in enumerate(windows):
                eq=[]
                for aidx,a in enumerate(W):
                    for bb in W[aidx+1:]:
                        if colors[ix[a]]==colors[ix[bb]]:
                            eq.append(pair(a,bb))
                if len(eq)!=2:
                    raise ValueError("saturated K7 did not select exactly two pairs")
                eq=tuple(sorted(eq))
                selected.append(eq)
                for e in eq:
                    matching_edge_counts[e]+=1
            signatures[(qmask,tuple(selected))]+=1
            return

        for color in range(min(5,top+2)):
            if unit_before[i] & classes[color]:
                continue
            colors[i]=color

            if i==max(tri):
                a,o,b=tri
                if ((colors[a]==colors[o])+(colors[b]==colors[o])
                    -(colors[a]==colors[b])) != 1:
                    continue

            touched=memberships[i]
            bad=False
            for t in touched:
                newp=paircounts[t]+counts[t][color]
                if newp>2 or (ends[t]==i and newp!=2):
                    bad=True
                    break
            if bad:
                continue

            for t in touched:
                paircounts[t]+=counts[t][color]
                counts[t][color]+=1
            classes[color] |= 1<<i

            newmask=qmask
            for j,qi in q_before[i]:
                if colors[j]==color:
                    newmask |= 1<<qi

            visit(i+1,max(top,color),newmask)

            classes[color] ^= 1<<i
            for t in touched:
                counts[t][color]-=1
                paircounts[t]-=counts[t][color]

    visit(0,-1,0)

    def mask_bits(m):
        return [i for i in range(len(local["Q"])) if (m>>i)&1]

    report={
        "schema":"matching-synchronization-probe-v1",
        "vertices":V,
        "actual_unit_edges":len(local["E"]),
        "window_unit_edges":len([e for e in local["E"] if e in window_pairs]),
        "external_unit_edges":[list(e) for e in external_unit],
        "nodes":nodes,
        "boundary_partitions":leaves,
        "q_histogram":{str(k):q_hist[k] for k in sorted(q_hist)},
        "feasible_q_masks":len(q_masks),
        "max_q_count":max(q_hist),
        "max_q_masks":[mask_bits(m) for m in sorted(q_masks) if m.bit_count()==max(q_hist)],
        "joint_q_matching_signatures":len(signatures),
        "q_pairs":[list(e) for e in local["Q"]],
        "matching_edges_seen":len(matching_edge_counts),
        "scope":"Discovery probe on the exact T165 zero-defect face. No full15 or HN conclusion."
    }
    text=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(text)
    print(text,end="")

if __name__=="__main__":
    main()
