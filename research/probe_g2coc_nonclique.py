#!/usr/bin/env python3
"""Search minimal non-clique G2COC families on full Y: (c,N)=(6,7),(7,7).

All coefficient-bearing pairs must lie in the certified support
U=E union P union Q union R. Opposite/distant group pairs with coefficient zero
are allowed to be outside U. The output is diagnostic search data only.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"))
import verify_pr_matching_window_ceiling as matching

def norm(raw):
    x={tuple(sorted(map(int,e))) for e in raw}; assert len(x)==len(raw); return x

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    g=matching.read(ROOT/"certificates/Y_full_geometry.json.gz")
    pb=matching.read(ROOT/"certificates/g14_pair_orbit_basis.json.gz")
    rb=matching.read(ROOT/"certificates/g14_r_pair_orbit_basis.json.gz")
    n,E,P,R=matching.validate_inputs(g,pb,rb); Q=norm(pb["orbit_nodes_by_grade"]["2"])
    U=E|P|Q|R
    tag={e:"E" for e in E};tag.update({e:"P" for e in P});tag.update({e:"Q" for e in Q});tag.update({e:"R" for e in R})
    adj=[set() for _ in range(n)]
    for a,b in U:adj[a].add(b);adj[b].add(a)

    rows={6:Counter(),7:Counter()}; reps={6:{},7:{}}; counts={6:0,7:0}
    def add(c,groups):
        coeff=Counter()
        for i in range(c):
            Gi=groups[i]
            for a,b in combinations(Gi,2):
                e=tuple(sorted((a,b))); assert e in U; coeff[tag[e]]-=1
            for step,sgn in ((1,1),(2,-1)):
                j=(i+step)%c
                if i<j or (i+step)>=c:
                    # each unordered group-pair should be counted once; canonical by modular distance
                    pass
        # direct unordered group pair classification avoids wrap bookkeeping
        for i in range(c):
            for j in range(i+1,c):
                d=(j-i)%c
                md=min(d,c-d)
                if md not in (1,2):continue
                sgn=1 if md==1 else -1
                for a in groups[i]:
                    for b in groups[j]:
                        e=tuple(sorted((a,b))); assert e in U; coeff[tag[e]]+=sgn
        rhs=3
        row=(coeff["P"],coeff["Q"],coeff["R"],coeff["E"],rhs)
        rows[c][row]+=1;counts[c]+=1
        reps[c].setdefault(row,[list(G) for G in groups])

    # c=7,N=7: singleton groups; enumerate C7^2 embeddings in sparse U.
    for v0 in range(n):
        greater={x for x in adj[v0] if x>v0}
        for v1 in sorted(greater):
            for v2 in sorted((adj[v0]&adj[v1])-{v0,v1}):
                if v2<=v0:continue
                used2={v0,v1,v2}
                for v3 in sorted((adj[v1]&adj[v2])-used2):
                    if v3<=v0:continue
                    used3=used2|{v3}
                    for v4 in sorted((adj[v2]&adj[v3])-used3):
                        if v4<=v0:continue
                        used4=used3|{v4}
                        for v5 in sorted((adj[v3]&adj[v4])-used4):
                            if v5<=v0 or v5 not in adj[v0]:continue
                            used5=used4|{v5}
                            cand=(adj[v4]&adj[v5]&adj[v0]&adj[v1])-used5
                            for v6 in sorted(cand):
                                if v6<=v0 or v1>=v6:continue
                                add(7,[[v0],[v1],[v2],[v3],[v4],[v5],[v6]])

    # c=6,N=7: rotate unique size-2 group to S0; quotient reflection by s1<s5.
    for a,b in sorted(U):
        common0=adj[a]&adj[b]
        for s1 in sorted(common0-{a,b}):
            used1={a,b,s1}
            for s2 in sorted((common0&adj[s1])-used1):
                used2=used1|{s2}
                for s3 in sorted((adj[s1]&adj[s2])-used2):
                    used3=used2|{s3}
                    for s4 in sorted((common0&adj[s2]&adj[s3])-used3):
                        used4=used3|{s4}
                        cand=(common0&adj[s1]&adj[s3]&adj[s4])-used4
                        for s5 in sorted(cand):
                            if s1>=s5:continue
                            add(6,[[a,b],[s1],[s2],[s3],[s4],[s5]])

    def score(row):
        p,q,r,u,rhs=row
        mx=max(p*x+r*y+q for x,y in matching.VERTICES)
        return F(rhs)-mx,mx
    out={}
    for c in (6,7):
        scored=sorted((score(row)[0],row,score(row)[1],mult) for row,mult in rows[c].items())
        bad=[x for x in scored if x[0]<0]; tight=[x for x in scored if x[0]==0]
        def pack(x):
            sl,row,mx,mult=x;p,q,r,u,rhs=row
            return {"slack_at_q_1":str(sl),"maximum_lhs_at_q_1":str(mx),"multiplicity":mult,
                    "row":{"P":p,"Q":q,"R":r,"unit":u,"rhs":rhs},
                    "groups":reps[c][row]}
        out[str(c)]={"instances":counts[c],"unique_rows":len(rows[c]),"violating":len(bad),"tight":len(tight),
                     "best":[pack(x) for x in scored[:20]],"violating_rows":[pack(x) for x in bad[:100]]}
    report={"schema":"minimal-nonclique-g2coc-probe-v1","status":"SEARCH_ONLY",
            "inputs":{"vertices":n,"E":len(E),"P":len(P),"Q":len(Q),"R":len(R),"U":len(U)},
            "families":out,
            "scope":"Complete enumeration of known-coordinate minimal non-clique families c6,N7 and c7,N7 modulo rotation/reflection conventions described in source. Larger N or c are not covered."}
    raw=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:args.output.write_text(raw)
    print(raw)

if __name__=="__main__":main()
