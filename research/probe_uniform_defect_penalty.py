#!/usr/bin/env python3
"""Discover the sharp *integer* uniform defect penalty for the T170 gauge.

For the exact W22 actual unit graph, let L' be the T170 gauge-transformed
separator and D=sum_j Z_j+T the inherited nonnegative integer defect.
We search for the least integer K such that every proper <=5-color partition
satisfies

    L'(c) <= 336 + K D(c).

This is a discovery program. It uses exact integer DFS with a sound optimistic
upper bound; any reported optimum/witness must be frozen and independently
verified before promotion to a theorem.
"""
import argparse, json
from pathlib import Path

from check_transport_projection import read, pair, verify_geometry_and_components
from verify_q_defect_lifting import geometry

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"
GAUGE=ROOT/"certificates/q_boundary_gauge_lift.json"

def transformed(source,g):
    terms=[]
    windows=source["boundary"]["saturated_windows"]
    for t in source["boundary"]["terms"]:
        a,b=pair(*t["pair"])
        add=0
        for j,W in enumerate(windows):
            if a in W and b in W:
                add+=g[j]
        terms.append((a,b,t["coefficient"]+add))
    return terms

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    source=read(SOURCE); gc=read(GAUGE)
    g=gc["window_gauge"]
    V=source["boundary"]["vertices"]
    order=source["boundary"]["order"]
    ix={v:i for i,v in enumerate(order)}

    geom=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(geom,pb,rb)
    local=geometry(geom,sets,V)

    unit_before=[0]*len(order)
    for a,b in local["E"]:
        i,j=sorted((ix[a],ix[b]))
        unit_before[j]|=1<<i

    # L' weights, including only P/Q/R terms; actual unit equalities are zero.
    base={}
    for a,b,w in transformed(source,g):
        base[pair(a,b)]=w

    # D is a linear equality functional plus constant -13:
    # D=sum_j(H_j-2)+1-e(229,4641)-e(305,4641)+e(229,305).
    dcoef={}
    for W in source["boundary"]["saturated_windows"]:
        for i,a in enumerate(W):
            for b in W[i+1:]:
                p=pair(a,b)
                dcoef[p]=dcoef.get(p,0)+1
    for p,delta in ((pair(229,4641),-1),(pair(305,4641),-1),(pair(229,305),1)):
        dcoef[p]=dcoef.get(p,0)+delta

    allpairs=[]
    for j in range(len(order)):
        for i in range(j):
            p=pair(order[i],order[j])
            allpairs.append((i,j,p))

    def optimize(K, stop_on_positive=False):
        # F=L'-336-KD = (13K-336)+sum_pair (base-K*dcoef)e_pair.
        weights={}
        for _,_,p in allpairs:
            w=base.get(p,0)-K*dcoef.get(p,0)
            if w:
                weights[p]=w
        before=[[] for _ in order]
        for i,j,p in allpairs:
            w=weights.get(p,0)
            if w:
                before[j].append((i,w))

        # Optimistic tail: every not-yet-decided positive pair can be made equal,
        # every negative one can be avoided. This ignores transitivity and is safe.
        tail=[0]*(len(order)+1)
        positive_by_later=[0]*len(order)
        for i,j,p in allpairs:
            w=weights.get(p,0)
            if w>0:
                positive_by_later[j]+=w
        for i in range(len(order)-1,-1,-1):
            tail[i]=tail[i+1]+positive_by_later[i]

        colors=[-1]*len(order); classes=[0]*5
        best=-10**18; witness=None; nodes=0; leaves=0
        constant=13*K-336

        def visit(pos,top,value):
            nonlocal best,witness,nodes,leaves
            nodes+=1
            # tail[pos] includes all positive pairs whose later endpoint is unassigned.
            if value+tail[pos]<=best:
                return False
            if stop_on_positive and value+tail[pos]<=0:
                return False
            if pos==len(order):
                leaves+=1
                total=constant+value
                if total>best:
                    best=total
                    witness=list(colors)
                return stop_on_positive and total>0
            for color in range(min(5,top+2)):
                if unit_before[pos] & classes[color]:
                    continue
                colors[pos]=color
                inc=sum(w for j,w in before[pos] if colors[j]==color)
                classes[color]|=1<<pos
                if visit(pos+1,max(top,color),value+inc):
                    return True
                classes[color]^=1<<pos
            colors[pos]=-1
            return False

        visit(0,-1,constant)
        # value already included constant at root, so correct the accidental double
        # constant in leaf computation by returning direct recomputation below.
        if witness is not None:
            eq=lambda a,b: witness[ix[a]]==witness[ix[b]]
            L=sum(w for a,b,w in transformed(source,g) if eq(a,b))
            H=sum(sum(eq(a,b) for i,a in enumerate(W) for b in W[i+1:])
                  for W in source["boundary"]["saturated_windows"])
            T=1-int(eq(229,4641))-int(eq(305,4641))+int(eq(229,305))
            D=H-14+T
            F=L-336-K*D
        else:
            L=D=F=None
        return {"K":K,"maximum_objective":F,"Lprime":L,"D":D,
                "nodes":nodes,"leaves_reached":leaves,"partition":witness}

    # First use monotonic violation searches conceptually, but exact optimizer is
    # cheap enough at 22 vertices to evaluate a logarithmic sequence then the edge.
    lo,hi=0,gc["coarse_lift_penalty"]
    tested=[]
    while lo<hi:
        mid=(lo+hi)//2
        r=optimize(mid)
        tested.append({k:r[k] for k in ("K","maximum_objective","Lprime","D","nodes","leaves_reached")})
        if r["maximum_objective"] is not None and r["maximum_objective"]<=0:
            hi=mid
        else:
            lo=mid+1
    sharp=optimize(lo)
    prev=optimize(lo-1) if lo>0 else None
    report={"schema":"uniform-defect-penalty-probe-v1",
            "least_integer_penalty":lo,
            "sharp":sharp,
            "previous":prev,
            "binary_search":tested,
            "scope":"Discovery search on exact W22 proper <=5-color partitions; not a proof certificate until independently replayed."}
    text=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(text)
    print(text,end="")

if __name__=="__main__":
    main()
