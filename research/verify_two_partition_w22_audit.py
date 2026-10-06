#!/usr/bin/env python3
"""Exact W22 audit of all currently evaluable 2-partition inequalities."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "certificates/q_joint_boundary_gap.json"
CERT = ROOT / "certificates/two_partition_w22_audit.json"
SCALE = 270
WEIGHT = {"P": 10, "Q": 189, "R": 140, "E": 0}

def pair(a,b):
    return (a,b) if a < b else (b,a)

def build_tags(source):
    tags = {}
    for term in source["boundary"]["terms"]:
        p = pair(*term["pair"])
        if p in tags:
            raise ValueError("duplicate P/Q/R pair")
        tags[p] = term["type"]
    for window in source["boundary"]["saturated_windows"]:
        if len(window) != 7 or len(set(window)) != 7:
            raise ValueError("bad saturated window")
        for i,a in enumerate(window):
            for b in window[i+1:]:
                tags.setdefault(pair(a,b),"E")
    counts = {t:0 for t in WEIGHT}
    for t in tags.values():
        if t not in counts:
            raise ValueError("unexpected pair type")
        counts[t] += 1
    if counts != {"P":47,"Q":11,"R":31,"E":31}:
        raise ValueError("unexpected certified pair counts")
    return tags

def score(C,mask,tags):
    A=[C[i] for i in range(len(C)) if mask>>i & 1]
    B=[C[i] for i in range(len(C)) if not (mask>>i & 1)]
    def w(a,b): return WEIGHT[tags[pair(a,b)]]
    lhs=sum(w(a,b) for a in A for b in B)
    lhs-=sum(w(A[i],A[j]) for i in range(len(A)) for j in range(i+1,len(A)))
    lhs-=sum(w(B[i],B[j]) for i in range(len(B)) for j in range(i+1,len(B)))
    rhs=SCALE*min(len(A),len(B))
    return A,B,lhs,rhs,rhs-lhs

def enumerate_all(vertices,tags):
    ix={v:i for i,v in enumerate(vertices)}
    neigh=[0]*len(vertices)
    for a,b in tags:
        i,j=ix[a],ix[b]
        neigh[i]|=1<<j
        neigh[j]|=1<<i
    clique_counts={str(k):0 for k in range(2,8)}
    strata={}
    total=facet=tight=facet_tight=0
    best=None
    tight_rows=[]
    def visit(cands,chosen):
        nonlocal total,facet,tight,facet_tight,best
        m=len(chosen)
        if m>=2:
            if m>7:
                raise ValueError("known support unexpectedly has clique size > 7")
            clique_counts[str(m)]+=1
            full=(1<<m)-1
            for mask in range(1,full):
                comp=full^mask
                if mask>comp:
                    continue
                A,B,lhs,rhs,slack=score(chosen,mask,tags)
                total+=1
                facet_case=len(A)!=len(B)
                if facet_case: facet+=1
                if slack<0:
                    raise ValueError("C030 violates a supported 2-partition inequality")
                if slack==0:
                    tight+=1
                    if facet_case: facet_tight+=1
                    tight_rows.append({"clique":list(chosen),"A":A,"B":B,
                                       "lhs_over_270":lhs,"rhs_over_270":rhs})
                key=f"{m}:{min(len(A),len(B))}-{max(len(A),len(B))}"
                row=strata.setdefault(key,{"count":0,"minimum_slack_over_270":None})
                row["count"]+=1
                old=row["minimum_slack_over_270"]
                row["minimum_slack_over_270"]=slack if old is None else min(old,slack)
                if best is None or slack<best["slack_over_270"]:
                    best={"clique":list(chosen),"A":A,"B":B,
                          "lhs_over_270":lhs,"rhs_over_270":rhs,
                          "slack_over_270":slack}
        c=cands
        while c:
            bit=c & -c
            c^=bit
            i=bit.bit_length()-1
            visit(c & neigh[i],chosen+[vertices[i]])
    visit((1<<len(vertices))-1,[])
    return {"known_support_clique_counts":clique_counts,
            "two_partition_inequalities":total,
            "facet_size_unequal_cases":facet,
            "tight_inequalities":tight,
            "tight_facet_cases":facet_tight,
            "global_minimum":best,
            "tight_rows":tight_rows,
            "strata":strata}

def main():
    source=json.loads(SOURCE.read_text())
    cert=json.loads(CERT.read_text())
    if source.get("schema")!="q-joint-boundary-gap-v1":
        raise ValueError("wrong source schema")
    if source["fractional_cover"]["means"]!={"P":[1,27],"Q":[7,10],"R":[14,27]}:
        raise ValueError("unexpected C030 means")
    vertices=source["boundary"]["vertices"]
    if len(vertices)!=22 or vertices!=sorted(set(vertices)):
        raise ValueError("unexpected W22 vertices")
    got=enumerate_all(vertices,build_tags(source))
    if got!=cert["audit"]:
        raise ValueError("2-partition audit differs from frozen certificate")
    if got["two_partition_inequalities"]!=8529 or got["facet_size_unequal_cases"]!=6830:
        raise ValueError("unexpected totals")
    if len(got["tight_rows"])!=1 or got["tight_rows"][0]["clique"]!=[229,305,4641]:
        raise ValueError("unexpected tight family")
    print(json.dumps({"status":"PASS","audit":got,"scope":cert["scope"]},sort_keys=True))

if __name__=="__main__":
    main()
