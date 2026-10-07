#!/usr/bin/env python3
"""Independent verifier for T171's sharp uniform defect penalty K=179."""
import argparse, json
from pathlib import Path
from copy import deepcopy

from check_transport_projection import read, require, pair, verify_geometry_and_components
from verify_q_defect_lifting import geometry

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"
GAUGE=ROOT/"certificates/q_boundary_gauge_lift.json"
CERT=ROOT/"certificates/q_boundary_sharp_uniform_lift.json"

def transformed(source,gauge):
    windows=source["boundary"]["saturated_windows"]
    out={}
    for t in source["boundary"]["terms"]:
        p=pair(*t["pair"])
        add=sum(gauge[j] for j,W in enumerate(windows)
                if p[0] in W and p[1] in W)
        out[p]=t["coefficient"]+add
    return out

def defect_coefficients(source):
    d={}
    for W in source["boundary"]["saturated_windows"]:
        for i,a in enumerate(W):
            for b in W[i+1:]:
                p=pair(a,b); d[p]=d.get(p,0)+1
    for p,delta in ((pair(229,4641),-1),
                    (pair(305,4641),-1),
                    (pair(229,305),1)):
        d[p]=d.get(p,0)+delta
    return d

def actual_unit_graph(source):
    geom=read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    _,sets,_=verify_geometry_and_components(geom,pb,rb)
    return geometry(geom,sets,source["boundary"]["vertices"])["E"]

def evaluate(order,colors,base,dcoef,units):
    ix={v:i for i,v in enumerate(order)}
    require(len(colors)==len(order) and all(type(c) is int and 0<=c<5 for c in colors),
            "five-color witness syntax")
    require(colors[0]==0 and all(colors[i] <= 1+max(colors[:i]) for i in range(1,len(colors))),
            "canonical color witness")
    for a,b in units:
        require(colors[ix[a]]!=colors[ix[b]],"witness is proper on all actual unit edges")
    eq=lambda a,b: colors[ix[a]]==colors[ix[b]]
    L=sum(w for (a,b),w in base.items() if eq(a,b))
    D=sum(w for (a,b),w in dcoef.items() if eq(a,b))-13
    require(D>=0,"defect nonnegative")
    return L,D

def verify_global_179(source,gauge,units):
    """Exhaustively maximize F=L'-336-179D by an independent DFS.

    Unlike the discovery producer, this verifier tests only K=179 and uses
    a separately reconstructed weighted equality functional. It never reads
    producer output, a frozen search trace, LP/SAT state, or floating point.
    """
    K=179
    order=source["boundary"]["order"]
    ix={v:i for i,v in enumerate(order)}
    base=transformed(source,gauge)
    dc=defect_coefficients(source)

    unit_before=[0]*len(order)
    for a,b in units:
        i,j=sorted((ix[a],ix[b]))
        unit_before[j]|=1<<i

    before=[[] for _ in order]
    positive_later=[0]*len(order)
    for j in range(len(order)):
        for i in range(j):
            p=pair(order[i],order[j])
            w=base.get(p,0)-K*dc.get(p,0)
            if w:
                before[j].append((i,w))
                if w>0: positive_later[j]+=w
    tail=[0]*(len(order)+1)
    for i in range(len(order)-1,-1,-1):
        tail[i]=tail[i+1]+positive_later[i]

    # F = 13*K - 336 + sum adjusted_pair_weight * equality.
    colors=[-1]*len(order)
    classes=[0]*5
    best=-10**18
    witness=None
    nodes=leaves=0

    def visit(pos,top,value):
        nonlocal best,witness,nodes,leaves
        nodes+=1
        require(value+tail[pos] >= best or best>-10**17,
                "internal optimistic bound arithmetic")
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

    visit(0,-1,13*K-336)
    require(best==0,"K=179 pointwise inequality")
    L,D=evaluate(order,witness,base,dc,units)
    require(L-336-K*D==0,"maximizer recomputation")
    return {"nodes":nodes,"leaves_reached":leaves,"maximum_objective":best,
            "maximizer_Lprime":L,"maximizer_D":D}

def verify(cert,source,gc):
    require(cert["schema"]=="q-boundary-sharp-uniform-lift-v1","schema")
    require(gc["schema"]=="q-boundary-gauge-lift-v1","gauge schema")
    require(cert["uniform_penalty"]==179 and cert["face_rhs"]==336,"fixed K/rhs")
    require(cert["transformed_aggregate"]=={"P":-263,"Q":500,"R":0},
            "inherited aggregate")
    units=actual_unit_graph(source)
    require(len(units)==34,"all actual W22 unit edges")
    base=transformed(source,gc["window_gauge"])
    dc=defect_coefficients(source)

    # Sharpness witness at K=178.
    sh=cert["sharpness"]
    L,D=evaluate(sh["order"],sh["partition"],base,dc,units)
    require((L,D)==(515,1),"sharpness witness values")
    require(L-336-178*D==1 and L-336-179*D==0,
            "178 fails by one and 179 is tight")

    exhaustive=verify_global_179(source,gc["window_gauge"],units)

    # Expectation lifting.
    K=179
    A=263+85*K
    B=19*K
    C=336-13*K
    require((A,B,C)==(15478,3401,-1991),"P/Q/R lifted coefficients")
    require(cert["unconditional_inequality"]["display"]==
            "500 q <= 15478 p + 3401 r - 1991","lift display")
    scalar_p=2*A+B
    scalar_c=2*C+B
    require((scalar_p,scalar_c)==(34357,-581),"transitivity elimination")
    require(cert["scalar_after_transitivity"]["display"]==
            "1000 q <= 34357 p - 581","scalar display")
    require(120163-34357==85806 and -3759-(-581)==-3178
            and 3178*27==85806,"strict comparison factorization")
    require(cert["consequence_if_q_at_least_7_10"]["p_lower"]==[1281,34357],
            "conditional q lower consequence")
    return {"status":"PASS","uniform_penalty":179,"sharpness":{"Lprime":L,"D":D},
            "exhaustive":exhaustive,
            "unconditional":"500q<=15478p+3401r-1991",
            "scalar":"1000q<=34357p-581","scope":cert["scope"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    source=read(SOURCE); gc=read(GAUGE); cert=read(CERT)
    report=verify(cert,source,gc)
    if args.self_test:
        bad=deepcopy(cert); bad["sharpness"]["partition"][0]=1
        try:
            base=transformed(source,gc["window_gauge"])
            dc=defect_coefficients(source)
            evaluate(bad["sharpness"]["order"],bad["sharpness"]["partition"],
                     base,dc,actual_unit_graph(source))
        except ValueError:
            pass
        else:
            raise ValueError("mutated sharpness witness accepted")
        print("self_tests_passed 1")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
