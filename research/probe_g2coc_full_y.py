#!/usr/bin/env python3
"""Search-only full-Y probe for known-coordinate c=5 G2COC inequalities.

Every pair in a c=5 G2COC union has coefficient +/-1, so a candidate whose
coordinates are all known E/P/Q/R pairs must live on a clique of
U=E union P union Q union R. E119 already certifies clique number(U)=7.
This script exhausts N=5 and N=7 c=5 candidates and asks whether any projected
inequality cuts the exact T158 P/R pentagon on the q=1 face.

Search output is diagnostic only. Any promoted mathematical claim needs a
separate frozen receipt and independent verifier.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
import verify_pr_matching_window_ceiling as matching

def normalize_pairs(raw):
    out={tuple(sorted(map(int,e))) for e in raw}
    assert len(out)==len(raw)
    return out

def c5_coeff(a,b):
    if a==b:
        return -1
    d=(a-b)%5
    return 1 if d in (1,4) else -1

def evaluate_row(row):
    p,q,r,u,rhs=row
    vals=[p*x+r*y+q for x,y in matching.VERTICES]
    maximum=max(vals)
    return F(rhs)-maximum,maximum

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()

    g=matching.read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=matching.read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=matching.read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    n,E,P,R=matching.validate_inputs(g,pb,rb)
    Q=normalize_pairs(pb["orbit_nodes_by_grade"]["2"])
    assert len(Q)==780 and not(Q&(E|P|R))
    U=E|P|Q|R
    kind={e:"E" for e in E}
    kind.update({e:"P" for e in P})
    kind.update({e:"Q" for e in Q})
    kind.update({e:"R" for e in R})
    adj=[set() for _ in range(n)]
    for a,b in U:
        adj[a].add(b);adj[b].add(a)
    cl=matching.ordered_cliques(adj)
    assert len(cl[5])==11160 and len(cl[7])==380

    rows=Counter(); reps={}; total=0
    for vs in sorted(cl[5]):
        root=min(vs)
        rest=sorted(set(vs)-{root})
        for tail in permutations(rest):
            cyc=(root,)+tail
            coeff=Counter()
            for i,j in combinations(range(5),2):
                d=(i-j)%5
                c=1 if d in (1,4) else -1
                coeff[kind[tuple(sorted((cyc[i],cyc[j])))]]+=c
            row=(coeff["P"],coeff["Q"],coeff["R"],coeff["E"],2)
            rows[row]+=1; total+=1
            reps.setdefault(row,{"N":5,"vertices":list(cyc),"groups":[[v] for v in cyc]})

    patterns=[]
    for labels in product(range(5),repeat=7):
        if labels[0]!=0 or len(set(labels))!=5:
            continue
        patterns.append(labels)
    assert len(patterns)==3360

    for vs in sorted(cl[7]):
        vs=tuple(sorted(vs))
        pairs=list(combinations(range(7),2))
        tags=[kind[tuple(sorted((vs[i],vs[j])))] for i,j in pairs]
        for labels in patterns:
            coeff=Counter()
            for (i,j),tag in zip(pairs,tags):
                coeff[tag]+=c5_coeff(labels[i],labels[j])
            row=(coeff["P"],coeff["Q"],coeff["R"],coeff["E"],3)
            rows[row]+=1; total+=1
            if row not in reps:
                groups=[[vs[i] for i in range(7) if labels[i]==a] for a in range(5)]
                reps[row]={"N":7,"vertices":list(vs),"groups":groups}

    scored=[]
    for row,count in rows.items():
        slack,maximum=evaluate_row(row)
        scored.append((slack,row,maximum,count))
    scored.sort(key=lambda x:(x[0],x[1]))
    violating=[x for x in scored if x[0]<0]
    tight=[x for x in scored if x[0]==0]

    def pack(x):
        slack,row,maximum,count=x
        p,q,r,u,rhs=row
        return {
            "slack_at_q_1":str(slack),
            "maximum_lhs_at_q_1":str(maximum),
            "row":{"P":p,"Q":q,"R":r,"unit":u,"rhs":rhs},
            "multiplicity":count,
            "representative":reps[row],
        }

    report={
        "schema":"full-y-c5-g2coc-probe-v1",
        "status":"SEARCH_ONLY",
        "inputs":{"vertices":n,"E":len(E),"P":len(P),"Q":len(Q),"R":len(R),
                  "U_edges":len(U),"U_5_cliques":len(cl[5]),"U_7_cliques":len(cl[7])},
        "normalized_instances":total,
        "expected_instances":11160*24+380*3360,
        "unique_rows":len(rows),
        "violating_rows_at_q_1":len(violating),
        "tight_rows_at_q_1":len(tight),
        "best_rows":[pack(x) for x in scored[:20]],
        "violating_rows":[pack(x) for x in violating[:100]],
        "scope":"Exhaustive c=5 G2COC with all nonzero pair coordinates in E/P/Q/R; because c=5 uses every pair, these are exactly N=5 or N=7 U-clique candidates. Search diagnostic only; c>=6 allows zero-coefficient unknown pairs and is not covered.",
    }
    assert total==report["expected_instances"]
    raw=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.write_text(raw)
    print(raw)

if __name__=="__main__":
    main()
