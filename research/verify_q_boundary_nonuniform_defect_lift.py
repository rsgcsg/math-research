#!/usr/bin/env python3
"""Exact verifier for T172: optimal nonuniform seven-window defect penalties."""
import argparse, json
from copy import deepcopy
from pathlib import Path

from check_transport_projection import read, require, pair, verify_geometry_and_components
from verify_q_defect_lifting import geometry

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"
GAUGE=ROOT/"certificates/q_boundary_gauge_lift.json"
CERT=ROOT/"certificates/q_boundary_nonuniform_defect_lift.json"

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

def evaluate(source,order,colors,base,units):
    ix={v:i for i,v in enumerate(order)}
    require(len(colors)==len(order) and all(type(c) is int and 0<=c<5 for c in colors),
            "five-color witness syntax")
    require(colors[0]==0 and all(colors[i] <= 1+max(colors[:i]) for i in range(1,len(colors))),
            "canonical color witness")
    for a,b in units:
        require(colors[ix[a]]!=colors[ix[b]],"witness proper on every actual unit edge")
    eq=lambda a,b: colors[ix[a]]==colors[ix[b]]
    L=sum(w for (a,b),w in base.items() if eq(a,b))
    z=[]
    for W in source["boundary"]["saturated_windows"]:
        H=sum(eq(a,b) for i,a in enumerate(W) for b in W[i+1:])
        z.append(H-2)
    a,o,b=source["boundary"]["PRR_triple"]
    T=1-int(eq(a,o))-int(eq(b,o))+int(eq(a,b))
    require(all(v>=0 for v in z) and T>=0,"nonnegative defects")
    return L,z,T

def verify_global(source,base,units,K):
    """Exhaustively maximize L'-336-sum_j K_j Z_j using integer DFS."""
    order=source["boundary"]["order"]; ix={v:i for i,v in enumerate(order)}
    pair_weight=dict(base)
    for j,W in enumerate(source["boundary"]["saturated_windows"]):
        for a_i,a in enumerate(W):
            for b in W[a_i+1:]:
                p=pair(a,b)
                pair_weight[p]=pair_weight.get(p,0)-K[j]
    constant=2*sum(K)-336

    unit_before=[0]*len(order)
    for a,b in units:
        i,j=sorted((ix[a],ix[b])); unit_before[j]|=1<<i
    before=[[] for _ in order]; positive_later=[0]*len(order)
    for j in range(len(order)):
        for i in range(j):
            w=pair_weight.get(pair(order[i],order[j]),0)
            if w:
                before[j].append((i,w))
                if w>0: positive_later[j]+=w
    tail=[0]*(len(order)+1)
    for i in range(len(order)-1,-1,-1):
        tail[i]=tail[i+1]+positive_later[i]

    colors=[-1]*len(order); classes=[0]*5
    best=-10**18; witness=None; nodes=leaves=0
    def visit(pos,top,value):
        nonlocal best,witness,nodes,leaves
        nodes+=1
        if value+tail[pos] <= best:
            return
        if pos==len(order):
            leaves+=1
            if value>best:
                best=value; witness=list(colors)
            return
        for color in range(min(5,top+2)):
            if unit_before[pos] & classes[color]:
                continue
            colors[pos]=color
            inc=sum(w for i,w in before[pos] if colors[i]==color)
            classes[color]|=1<<pos
            visit(pos+1,max(top,color),value+inc)
            classes[color]^=1<<pos
        colors[pos]=-1
    visit(0,-1,constant)
    require(best==0,"nonuniform pointwise inequality")
    L,z,T=evaluate(source,order,witness,base,units)
    require(L-336-sum(k*d for k,d in zip(K,z))==0,"maximizer recomputation")
    return {"nodes":nodes,"leaves_reached":leaves,"maximum_objective":best,
            "maximizer_Lprime":L,"maximizer_defects":z,"maximizer_T":T}

def verify(cert,source,gc):
    require(cert["schema"]=="q-boundary-nonuniform-defect-lift-v1","schema")
    require(gc["schema"]=="q-boundary-gauge-lift-v1","gauge schema")
    K=cert["window_penalties"]
    require(K==[88,126,43,94,179,138,124] and cert["prr_penalty"]==0,
            "fixed nonuniform penalties")
    require(sum(K)==cert["window_penalty_sum"]==792,"penalty sum")
    require(cert["face_rhs"]==336 and
            cert["transformed_aggregate"]=={"P":-263,"Q":500,"R":0},
            "inherited T170 data")
    require(cert["order"]==source["boundary"]["order"],"fixed vertex order")
    units=actual_units(source)
    require(len(units)==34,"all actual W22 unit edges")
    base=transformed(source,gc["window_gauge"])

    # Seven isolated-defect witnesses force each coefficient separately.
    require(len(cert["sharp_witnesses"])==7,"seven sharp witnesses")
    sharp=[]
    for j,row in enumerate(cert["sharp_witnesses"]):
        require(row["window"]==j+1 and row["penalty"]==K[j],"witness metadata")
        L,z,T=evaluate(source,cert["order"],row["partition"],base,units)
        target=[0]*7; target[j]=1
        require(z==target and T==0,"isolated window defect")
        require(L==row["Lprime"]==336+K[j],"isolated sharp excess")
        sharp.append({"window":j+1,"Lprime":L,"defects":z,"T":T})
    # Therefore any real penalties a_j,t satisfying the pointwise inequality
    # must obey a_j >= K_j for every j, independent of t.
    lower_sum=sum(row["Lprime"]-336 for row in cert["sharp_witnesses"])
    require(lower_sum==792,"global lower bound on seven-window price sum")

    exhaustive=verify_global(source,base,units,K)

    ew=cert["equality_witness"]
    L,z,T=evaluate(source,cert["order"],ew["partition"],base,units)
    require((L,z,T)==(ew["Lprime"],ew["defects"],ew["T"]) and
            L-336-sum(k*d for k,d in zip(K,z))==0,"stored equality witness")

    # Exact expectation arithmetic.
    S=sum(K)
    A=263+12*S
    B=3*S
    C=336-2*S
    require((A,B,C)==(9767,2376,-1248),"unconditional coefficients")
    require(cert["unconditional_inequality"]==
            "500 q <= 9767 p + 2376 r - 1248","unconditional display")
    scalar_p=2*A+B
    scalar_c=2*C+B
    require((scalar_p,scalar_c)==(21910,-120),"transitivity elimination")
    require(cert["scalar_after_transitivity"]==
            "1000 q <= 21910 p - 120","scalar display")
    require(34357-21910==12447 and -581-(-120)==-461 and 461*27==12447,
            "strict improvement factorization")
    require(cert["consequence_if_q_at_least_7_10"]["p_lower"]==[82,2191],
            "conditional q consequence")
    return {"status":"PASS","window_penalties":K,"window_penalty_sum":S,
            "sharp_witnesses":sharp,"exhaustive":exhaustive,
            "unconditional":"500q<=9767p+2376r-1248",
            "scalar":"1000q<=21910p-120","scope":cert["scope"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    source=read(SOURCE); gc=read(GAUGE); cert=read(CERT)
    report=verify(cert,source,gc)
    if args.self_test:
        bad=deepcopy(cert); bad["sharp_witnesses"][0]["partition"][0]=1
        try:
            verify(bad,source,gc)
        except ValueError:
            pass
        else:
            raise ValueError("mutated witness accepted")
        print("self_tests_passed 1")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__": main()
