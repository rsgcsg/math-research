#!/usr/bin/env python3
"""Exact finite forcing certificates for 5 frozen cosets of triangular T^2.

Proof of the infinite statement requires the explicit two-generator
translation argument. The weak-six consequences also use the prior exact
four-palette unit-triangle leaf certificate and majority-exclusion lemma.
No finite non-six-colorable unit-distance graph is claimed here.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
import json

S=(( -1, 0),(-1,1),(0,-1),(0,1),(1,-1))
COLORS={2,3,4,5,6}
DELTA=tuple((a,b) for a in range(-2,3) for b in range(-2,3)
            if a*a+a*b+b*b in (1,3,4))
GENS=((-3,1),(3,-1),(1,2),(-1,-2))
LEAF_TUPLES=(
    (-2,1),(1,-2),(-1,-1),(2,-1),
    (-1,3),(0,3),(3,0),(2,-1),
    (-2,1),(0,3),(-2,4),(-3,3),
)
LEAF_SET={ (m+3,n) for m,n in LEAF_TUPLES }
def check(x,msg):
    if not x:raise RuntimeError(msg)
def code(v):return (v[0]+3*v[1])%7
def graph_distance_sq(a,b):
    x=a[0]-b[0];y=a[1]-b[1]
    return x*x+x*y+y*y
def shifted(v,t):return(v[0]+t[0],v[1]+t[1])

def forced_cert(radius,targets):
    vertices={ (m,n) for m in range(-radius,radius+1)
               for n in range(-radius,radius+1) if code((m,n)) in COLORS}
    check(set(S)<=vertices,"five seed cells present")
    check({code(v) for v in S}==COLORS,"all five distinct seed colors")
    check(all(graph_distance_sq(a,b) in (1,3,4)
              for a,b in combinations(S,2)),"seed must be a T^2 K5")
    neighbors={v:tuple(sorted(shifted(v,t) for t in DELTA
                                if shifted(v,t) in vertices)) for v in vertices}
    known={v:code(v) for v in S}
    depth={v:0 for v in S}
    witness={}
    rounds=0
    while True:
        new={}
        for v in sorted(vertices-known.keys()):
            seen={}
            for u in neighbors[v]:
                if u in known:
                    seen[known[u]]=u
            if len(seen)==4:
                unused=COLORS-set(seen)
                check(len(unused)==1,"four distinct colors force exactly one")
                c=unused.pop()
                check(c==code(v),"all forced colors match the known 7-code")
                new[v]=c
                witness[v]=tuple(seen[k] for k in sorted(seen))
                depth[v]=rounds+1
            elif len(seen)==5:
                raise RuntimeError("all five colors forbidden at an unmarked site")
        if not new:break
        known.update(new)
        rounds+=1

    check(set(targets)<=known.keys(),"every requested target must be forced")
    footprint=set(S)|set(targets)
    pending=list(targets)
    while pending:
        v=pending.pop()
        for w in witness.get(v,()):
            if w not in footprint:
                footprint.add(w);pending.append(w)

    ordered=sorted(footprint-set(S),key=lambda v:(depth[v],v))
    proved={v:code(v) for v in S}
    certificate=[]
    for v in ordered:
        ww=witness[v]
        check(len(ww)==4 and all(w in proved for w in ww),
              "each compressed witness must depend on earlier stages")
        check({proved[w] for w in ww}==COLORS-{code(v)},
              "four predecessor colors exactly the other four")
        check(all(graph_distance_sq(v,w) in (1,3,4) for w in ww),
              "each forcing neighbor is an actual T-square edge")
        proved[v]=code(v)
        certificate.append({"site":list(v),"code":code(v),
                            "depth":depth[v],
                            "neighbors":[list(w) for w in ww]})
    check(set(targets)<=proved.keys(),"compressed certificate proves targets")
    return {"radius":radius,"rounds":rounds,
            "seed_size":len(S),"compressed_derived_steps":len(ordered),
            "compressed_footprint_sites":len(footprint),
            "max_depth":max(depth[v] for v in footprint),
            "residue_counts":{str(k):sum(code(v)==k for v in footprint)
                              for k in sorted(COLORS)},
            "target_size":len(set(targets)),"proof_steps":certificate}

def main():
    check(len(DELTA)==18,"T^2 must have 18 surrounding centers")
    check(len(LEAF_SET)==9,"12 unit leaves use 9 actual hex cells")
    check({code(v) for v in LEAF_SET}=={2,4,5,6},
          "after translation the unit-triangle leaves occupy only four nonmixed code classes")
    translations={shifted(v,t) for v in S for t in GENS}
    group=forced_cert(4,translations)
    leaves=forced_cert(6,LEAF_SET)
    check(group["compressed_footprint_sites"]==30
          and group["compressed_derived_steps"]==25
          and group["max_depth"]==7,"small five-color translation certificate")
    check(leaves["compressed_footprint_sites"]==38
          and leaves["compressed_derived_steps"]==33
          and leaves["max_depth"]==13,"five-color forcing to all triangle leaves")
    check(max(map(int,leaves["residue_counts"].values()))==8,
          "fixed six-label footprint multiplicity at most eight per code class")
    counts=Counter(code(v) for v in LEAF_SET)
    check(max(counts.values())==3 and sorted(counts.values())==[2,2,2,3],
          "translates of triangle leaves overlap each nonmixed cell at most three times")
    check(GENS[0][0]*GENS[2][1]-GENS[0][1]*GENS[2][0]==-7,
          "the two small translation generators span the index-seven kernel lattice")
    check(all(code(v)==0 for v in GENS),"translations preserve code classes")
    # Exact conservative bounds: pi>3, sqrt(3)<2, area=M=6sqrt(3)/25.
    eta=F(1,62500)
    lower_probe=F(3,140*140)
    upper_twelve_missing=12*eta*F(12,25)
    check(lower_probe>upper_twelve_missing,
          "even twelve cells at eta impurity cannot spoil all translated triangle leaves")
    return {
      "status":"PASS",
      "scope":"finite T-square forcing and rational majority deficit only; all-label geometry relies on prior triangle lemma",
      "removed_code_classes":[0,1],
      "remaining_code_classes":[2,3,4,5,6],
      "rigid_five_color_translation":group,
      "forced_triangle_leaves":leaves,
      "triangle_unique_leaf_count":len(LEAF_SET),
      "max_triangle_leaf_multiplicity":max(counts.values()),
      "per_color_majority_density_lower_conditional_exact_twofold":"1/56",
      "off_any_fixed_five_palette_density_lower_conditional_exact_twofold":"1/21",
      "triangle_common_translation_disk_area_gt":"3/19600",
      "all_twelve_eta_majority_leakage_lt":str(upper_twelve_missing),
      "global_scope":"all exact two-coset marked patterns by triangular lattice isometries, not every six-coloring",
      "hn_status":"chi in {6,7}; no proof of chi=7"
    }

if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,indent=2))
