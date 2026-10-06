#!/usr/bin/env python3
"""Discovery: optimize nonuniform prices for the seven K7 defects plus PRR defect.

Find nonnegative k_1..k_7,t minimizing S=sum k_j subject to
  L'(c) <= 336 + sum_j k_j Z_j(c) + t T(c)
for every actual proper <=5-color W22 partition c, with optional
3S-2t>=0 so the existing r upper bound can eliminate r.

Uses scipy only for the 8-variable cutting-plane LP. The separation oracle is
an exact combinatorial DFS over actual unit-edge proper partitions, with
floating objective used only for discovery. Any publishable candidate must be
rechecked later by a standard-library exact verifier.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

from check_transport_projection import read, pair, verify_geometry_and_components
from verify_q_defect_lifting import geometry

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"
GAUGE=ROOT/"certificates/q_boundary_gauge_lift.json"

def transformed(source,gauge):
    windows=source["boundary"]["saturated_windows"]
    out={}
    for row in source["boundary"]["terms"]:
        p=pair(*row["pair"])
        add=sum(gauge[j] for j,W in enumerate(windows)
                if p[0] in W and p[1] in W)
        out[p]=row["coefficient"]+add
    return out

def actual_units(source):
    g=read(ROOT/"certificates/Y_full_geometry.json.gz")
    b=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    r=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(g,b,r)
    return geometry(g,sets,source["boundary"]["vertices"])["E"]

def defect_signature(source,order,colors):
    ix={v:i for i,v in enumerate(order)}
    eq=lambda a,b: colors[ix[a]]==colors[ix[b]]
    z=[]
    for W in source["boundary"]["saturated_windows"]:
        h=sum(eq(a,b) for i,a in enumerate(W) for b in W[i+1:])
        z.append(h-2)
    a,o,b=source["boundary"]["PRR_triple"]
    T=1-int(eq(a,o))-int(eq(b,o))+int(eq(a,b))
    return z,T

def evaluate_L(order,colors,base):
    ix={v:i for i,v in enumerate(order)}
    return sum(w for (a,b),w in base.items() if colors[ix[a]]==colors[ix[b]])

def oracle(source,base,units,x):
    ks=list(x[:7]); t=float(x[7])
    order=source["boundary"]["order"]; ix={v:i for i,v in enumerate(order)}
    windows=source["boundary"]["saturated_windows"]
    # pair coefficient of -sum k_j H_j - t*T plus L'
    pw=dict(base)
    for j,W in enumerate(windows):
        for i,a in enumerate(W):
            for b in W[i+1:]:
                p=pair(a,b); pw[p]=pw.get(p,0.0)-ks[j]
    a,o,b=source["boundary"]["PRR_triple"]
    for p,delta in ((pair(a,o),+t),(pair(b,o),+t),(pair(a,b),-t)):
        pw[p]=pw.get(p,0.0)+delta
    constant=2*sum(ks)-336-t

    unit_before=[0]*len(order)
    for a,b in units:
        i,j=sorted((ix[a],ix[b])); unit_before[j]|=1<<i
    before=[[] for _ in order]; poslater=[0.0]*len(order)
    for j in range(len(order)):
        for i in range(j):
            w=pw.get(pair(order[i],order[j]),0.0)
            if abs(w)>1e-12:
                before[j].append((i,w))
                if w>0: poslater[j]+=w
    tail=[0.0]*(len(order)+1)
    for i in range(len(order)-1,-1,-1): tail[i]=tail[i+1]+poslater[i]

    colors=[-1]*len(order); classes=[0]*5
    best=-1e100; witness=None; nodes=0
    def visit(pos,top,value):
        nonlocal best,witness,nodes
        nodes+=1
        if value+tail[pos] <= best+1e-10: return
        if pos==len(order):
            if value>best:
                best=value; witness=list(colors)
            return
        for color in range(min(5,top+2)):
            if unit_before[pos] & classes[color]: continue
            colors[pos]=color
            inc=sum(w for i,w in before[pos] if colors[i]==color)
            classes[color]|=1<<pos
            visit(pos+1,max(top,color),value+inc)
            classes[color]^=1<<pos
        colors[pos]=-1
    visit(0,-1,constant)
    z,T=defect_signature(source,order,witness)
    L=evaluate_L(order,witness,base)
    exact_excess=L-336-sum(ks[i]*z[i] for i in range(7))-t*T
    return best, witness, z, T, L, nodes, exact_excess

def solve_lp(rows):
    # rows are (z[7],T,excess); require z.k + T*t >= excess.
    A=[]; b=[]
    for z,T,e in rows:
        A.append([-float(v) for v in z]+[-float(T)])
        b.append(-float(e))
    # enforce 3S-2t >=0 -> -3S+2t <=0
    A.append([-3.0]*7+[2.0]); b.append(0.0)
    c=[1.0]*7+[0.0]
    res=linprog(c,A_ub=np.array(A),b_ub=np.array(b),
                bounds=[(0,None)]*8,method="highs")
    if not res.success: raise RuntimeError(res.message)
    return res.x,res.fun

def main():
    source=read(SOURCE); gc=read(GAUGE)
    base=transformed(source,gc["window_gauge"])
    units=actual_units(source)
    rows=[]
    seen=set()
    history=[]
    # seed with known sharp uniform witness
    sh=read(ROOT/"certificates/q_boundary_sharp_uniform_lift.json")["sharpness"]
    z,T=defect_signature(source,sh["order"],sh["partition"])
    rows.append((z,T,sh["Lprime"]-336)); seen.add((tuple(z),T,sh["Lprime"]-336))
    for it in range(80):
        x,S=solve_lp(rows)
        best,w,z,T,L,nodes,ex=oracle(source,base,units,x)
        history.append({"iteration":it,"S":S,"x":[float(v) for v in x],
                        "oracle":best,"z":z,"T":T,"Lprime":L,"nodes":nodes,"partition":w})
        print(json.dumps(history[-1],sort_keys=True),flush=True)
        if best<=1e-7:
            out={"status":"FOUND","S":S,"x":[float(v) for v in x],
                 "constraints":len(rows),"history":history}
            (ROOT/"certificates/nonuniform_defect_discovery.json").write_text(
                json.dumps(out,indent=2,sort_keys=True)+"\n")
            return
        key=(tuple(z),T,L-336)
        if key in seen:
            raise RuntimeError("repeated violated signature")
        seen.add(key); rows.append((z,T,L-336))
    raise RuntimeError("cutting plane did not converge")

if __name__=="__main__": main()
