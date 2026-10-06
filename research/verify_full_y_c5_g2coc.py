#!/usr/bin/env python3
"""T161: exact full-Y ceiling for known-coordinate c=5 G2COC inequalities.

For c=5 every pair in the union of the five nonempty groups has coefficient
+1 or -1. Hence if every coefficient-bearing pair is one of the certified
E/P/Q/R coordinates, the union is a clique of U=E union P union Q union R.
The independently reconstructed U has clique number 7, so odd total size is
only 5 or 7. This verifier exhausts both cases and checks the q=1 projection
against the exact T158 P/R pentagon.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

if not __debug__:
    raise RuntimeError("Verification requires assertions; run without -O")

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
import verify_pr_matching_window_ceiling as matching

def normalize_pairs(raw):
    pairs=[tuple(sorted(map(int,e))) for e in raw]
    assert len(pairs)==len(set(pairs))
    return set(pairs)

def c5_coeff(a,b):
    if a==b:
        return -1
    return 1 if (a-b)%5 in (1,4) else -1

def score(row):
    p,q,r,u,rhs=row
    maximum=max(p*x+r*y+q for x,y in matching.VERTICES)
    return F(rhs)-maximum,maximum

def build_report():
    g=matching.read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=matching.read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=matching.read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    n,E,P,R=matching.validate_inputs(g,pb,rb)
    Q=normalize_pairs(pb["orbit_nodes_by_grade"]["2"])
    assert len(Q)==780 and not(Q&(E|P|R))
    U=E|P|Q|R
    kind={e:"E" for e in E}
    kind.update({e:"P" for e in P});kind.update({e:"Q" for e in Q});kind.update({e:"R" for e in R})
    adj=[set() for _ in range(n)]
    for a,b in U:
        adj[a].add(b);adj[b].add(a)

    ordered=matching.ordered_cliques(adj)
    maximal=matching.maximal_cliques(adj)
    derived={j:set() for j in range(2,8)}
    for clique in maximal:
        for j in derived:
            derived[j].update(combinations(clique,j))
    assert ordered==derived
    assert {j:len(ordered[j]) for j in range(5,8)}=={5:11160,6:3380,7:380}
    assert max(map(len,maximal))==7

    rows=Counter(); rows_by_n={5:Counter(),7:Counter()}; reps={}
    instances={5:0,7:0}
    for vs in sorted(ordered[5]):
        root=min(vs); rest=sorted(set(vs)-{root})
        for tail in permutations(rest):
            cyc=(root,)+tail; coeff=Counter()
            for i,j in combinations(range(5),2):
                c=1 if (i-j)%5 in (1,4) else -1
                coeff[kind[tuple(sorted((cyc[i],cyc[j])))]]+=c
            row=(coeff["P"],coeff["Q"],coeff["R"],coeff["E"],2)
            rows[row]+=1;rows_by_n[5][row]+=1;instances[5]+=1
            reps.setdefault(row,{"N":5,"groups":[[v] for v in cyc]})
    assert instances[5]==11160*24==267840

    patterns=[labels for labels in product(range(5),repeat=7)
              if labels[0]==0 and len(set(labels))==5]
    assert len(patterns)==3360
    pairs=list(combinations(range(7),2))
    for vs in sorted(ordered[7]):
        vs=tuple(sorted(vs))
        tags=[kind[tuple(sorted((vs[i],vs[j])))] for i,j in pairs]
        for labels in patterns:
            coeff=Counter()
            for (i,j),tag in zip(pairs,tags):
                coeff[tag]+=c5_coeff(labels[i],labels[j])
            row=(coeff["P"],coeff["Q"],coeff["R"],coeff["E"],3)
            rows[row]+=1;rows_by_n[7][row]+=1;instances[7]+=1
            if row not in reps:
                reps[row]={"N":7,"groups":[[vs[i] for i in range(7) if labels[i]==a] for a in range(5)]}
    assert instances[7]==380*3360==1276800
    assert sum(instances.values())==1544640

    scored=sorted((score(row)[0],row,score(row)[1],count)
                  for row,count in rows.items())
    violating=[x for x in scored if x[0]<0]
    tight=[x for x in scored if x[0]==0]
    assert not violating and not tight
    best=scored[0]
    assert best[0]==F(1,3)
    assert best[1]==(2,1,-1,-2,2)
    assert best[2]==F(5,3)
    assert best[3]==3120
    assert reps[best[1]]=={
        "N":5,
        "groups":[[31],[35],[873],[877],[229]],
    }
    assert len(rows)==55

    row_payload=[[list(row),count] for row,count in sorted(rows.items())]
    byn_payload={
        str(N):[[list(row),count] for row,count in sorted(rows_by_n[N].items())]
        for N in (5,7)
    }
    return {
        "schema":"full-y-c5-g2coc-ceiling-v1",
        "research_id":"T161",
        "status":"PASS_EXACT_FULL_Y_KNOWN_COORDINATE_C5_G2COC_CEILING",
        "inputs":{
            "vertices":n,"E":len(E),"P":len(P),"Q":len(Q),"R":len(R),"U_edges":len(U),
            "geometry_semantic_sha256":matching.GEOMETRY,
            "P_basis_sha256":matching.P_BASIS,
            "R_basis_sha256":matching.R_BASIS,
        },
        "cliques":{
            "algorithms":["ordered common-neighbor recursion","pivoting Bron-Kerbosch plus deduplicated subsets"],
            "counts":{"5":len(ordered[5]),"6":len(ordered[6]),"7":len(ordered[7])},
            "maximum_size":7,
            "sha256":{"5":matching.digest(sorted(ordered[5])),"7":matching.digest(sorted(ordered[7]))},
        },
        "enumeration":{
            "normalized_instances":{"N5":instances[5],"N7":instances[7],"total":sum(instances.values())},
            "unique_rows":len(rows),
            "unique_rows_by_N":{"N5":len(rows_by_n[5]),"N7":len(rows_by_n[7])},
            "row_multiplicity_sha256":matching.digest(row_payload),
            "row_multiplicity_sha256_by_N":{k:matching.digest(v) for k,v in byn_payload.items()},
        },
        "q_equals_1_projection":{
            "violating_rows":0,"tight_rows":0,"minimum_slack":"1/3",
            "best_row":{"P":2,"Q":1,"R":-1,"unit":-2,"rhs":2,
                        "maximum_lhs":"5/3","multiplicity":3120,
                        "representative":reps[best[1]]},
            "T158_vertices":[[str(p),str(r)] for p,r in matching.VERTICES],
        },
        "scope":"Every c=5 G2COC whose coefficient-bearing pairs are all in certified E/P/Q/R. For c=5 every pair bears coefficient +/-1, so E119 omega(U)=7 reduces the full known-coordinate family to N=5 or 7. No such inequality shrinks the q=1 T158 P/R pentagon. c>=6 has zero-coefficient distant pairs and is not covered; neither full15 nor HN is resolved.",
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt",type=Path,default=ROOT/"certificates/full_y_c5_g2coc_ceiling.json")
    ap.add_argument("--write-receipt",action="store_true")
    args=ap.parse_args()
    report=build_report()
    if args.write_receipt:
        args.receipt.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    else:
        assert matching.canonical(matching.read(args.receipt))==matching.canonical(report)
    print(json.dumps(report,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
