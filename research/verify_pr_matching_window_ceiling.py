#!/usr/bin/env python3
"""Exact census of the alpha<=2 matching-window family using only P/R events.

The geometry and actual transport components are pinned to independently replayed
published inputs. This checks a combinatorial consequence, not a new geometry
reconstruction or a full15 feasibility claim.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')

GEOMETRY = '90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957'
P_BASIS = '757a6f62edfb5285b9fde82f55c93454abd6e6a5b1985f3838d4c2a93e003534'
R_BASIS = 'f21599cb3ed6076e797f1fed319d5e8d4941c50b05fdaed12c6de218a6e9c976'
VERTICES = [(F(1,27),F(14,27)), (F(1,6),F(0)), (F(1,3),F(0)),
            (F(1,3),F(1,3)), (F(1,5),F(3,5))]


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,
                      allow_nan=False).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def unique_keys(pairs):
    out = {}
    for k,v in pairs:
        if k in out:
            raise ValueError('Duplicate JSON key: '+k)
        out[k] = v
    return out


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw,
                      object_pairs_hook=unique_keys)


def validate_inputs(g,b,r):
    assert digest(g)==GEOMETRY
    for obj,field,expected in [(b,'basis_sha256',P_BASIS),
                               (r,'candidate_sha256',R_BASIS)]:
        obj0=dict(obj)
        assert obj0.pop(field)==expected==digest(obj0)
        assert obj['geometry_semantic_sha256']==GEOMETRY
    E=set(map(tuple,g['edges']))
    P=set(map(tuple,b['orbit_nodes_by_grade']['1/sqrt3']))
    R=set(map(tuple,r['orbit_nodes']))
    n=len(g['points'])
    assert n==10077 and (len(E),len(P),len(R))==(49858,1860,1472)
    assert not(E&P or E&R or P&R)
    assert all(type(a) is int and type(z) is int and 0<=a<z<n for a,z in E|P|R)
    return n,E,P,R


def ordered_cliques(adj):
    out={n:set() for n in range(2,8)}
    def visit(vs,cand):
        n=len(vs)
        if n>=2:
            out[n].add(tuple(vs))
        if n==7:
            # Directly certify no larger clique, rather than assume a cutoff.
            assert not cand
            return
        for j,v in enumerate(cand):
            visit(vs+[v],[w for w in cand[j+1:] if w in adj[v]])
    for a in range(len(adj)):
        visit([a],sorted(w for w in adj[a] if w>a))
    return out


def maximal_cliques(adj):
    out=[]
    def bk(vs,p,x):
        if not p and not x:
            out.append(tuple(sorted(vs)))
            return
        u=max(p|x,key=lambda z:len(p&adj[z]))
        for v in sorted(p-adj[u]):
            bk(vs+[v],p&adj[v],x&adj[v])
            p.remove(v)
            x.add(v)
    for a in range(len(adj)):
        bk([a],{b for b in adj[a] if b>a},{b for b in adj[a] if b<a})
    assert len(out)==len(set(out)) and max(map(len,out))==7
    return out


def census(n,E,P,R):
    H=P|R
    adj=[set() for _ in range(n)]
    for a,b in E|H:
        adj[a].add(b)
        adj[b].add(a)
    cl=ordered_cliques(adj)
    maximal=maximal_cliques(adj)
    independently={j:set() for j in range(2,8)}
    for vs in maximal:
        for j in independently:
            independently[j].update(combinations(vs,j))
    assert cl==independently
    eligible={j:Counter() for j in cl}
    degree=Counter()
    for j,windows in cl.items():
        for vs in windows:
            # Test alpha(G)<=2 directly: every triple contains an actual unit edge.
            if not all(any(e in E for e in combinations(tr,2))
                       for tr in combinations(vs,3)):
                continue
            pairs=list(combinations(vs,2))
            a=sum(e in P for e in pairs)
            b=sum(e in R for e in pairs)
            eligible[j][a,b]+=1
            for v in vs:
                ap=sum(tuple(sorted((v,w))) in P for w in vs if w!=v)
                ar=sum(tuple(sorted((v,w))) in R for w in vs if w!=v)
                degree[ap,ar]+=1
    # Every finite matching-family constraint is linear, so testing all five
    # vertices suffices on the displayed pentagon. Its local realizability is
    # a separate theorem; this checker only needs the rational candidate points.
    for a,b in degree:
        assert all(a*p+b*r<=1 for p,r in VERTICES)
    for j,patterns in eligible.items():
        for a,b in patterns:
            assert all(a*p+b*r>=j-5 for p,r in VERTICES)
            if j%2:
                assert all(a*p+b*r<=j//2 for p,r in VERTICES)
    assert not eligible[7]
    assert eligible[5]==Counter({(4,2):2280})
    assert eligible[6]==Counter({(6,3):380})
    def rows(c):
        return [dict(P=a,R=b,count=v) for (a,b),v in sorted(c.items())]
    return dict(
        schema='pr-matching-window-ceiling-v1', status='PASS_EXACT_FIXED_FAMILY_CENSUS',
        geometry_semantic_sha256=GEOMETRY,P_basis_sha256=P_BASIS,R_basis_sha256=R_BASIS,
        union_vertices=n,union_edges=len(E|H),
        algorithms=['ordered common-neighbor recursion','pivoting Bron-Kerbosch and deduplicated subsets'],
        maximal_clique_size_counts={str(k):v for k,v in sorted(Counter(map(len,maximal)).items())},
        clique_counts={str(j):len(v) for j,v in cl.items()},
        clique_set_sha256={str(j):digest(sorted(v)) for j,v in cl.items()},
        alpha_le_2_window_counts={str(j):rows(v) for j,v in eligible.items()},
        degree_patterns=rows(degree),
        tested_polygon_vertices=[[str(p),str(r)] for p,r in VERTICES],
        scope='All alpha<=2 induced windows of the fixed Y whose every nonunit pair belongs to the certified P or R component. No constraint from this complete matching family cuts the displayed pentagon. This does not cover other pair components, alpha>=3 windows, higher pattern laws, or full15 feasibility.')


def main():
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true')
    args=ap.parse_args()
    g=read(root/'certificates/Y_full_geometry.json.gz')
    b=read(root/'certificates/g14_pair_orbit_basis.json.gz')
    r=read(root/'certificates/g14_r_pair_orbit_basis.json.gz')
    inputs=validate_inputs(g,b,r)
    rejected=[]
    for name,index,mutate in [
        ('missing-unit-edge',0,lambda x:x['edges'].pop()),
        ('missing-P-node',1,lambda x:x['orbit_nodes_by_grade']['1/sqrt3'].pop()),
        ('wrong-R-node',2,lambda x:x['orbit_nodes'][0].__setitem__(0,0))]:
        trial=deepcopy([g,b,r]);mutate(trial[index])
        try:
            validate_inputs(*trial)
        except (AssertionError,ValueError):
            rejected.append(name)
        else:
            raise AssertionError('Malformed input accepted: '+name)
    report=census(*inputs)
    report['rejected_mutations']=rejected
    path=root/'certificates/pr_matching_window_ceiling.json'
    if args.write_receipt:
        path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    else:
        assert canonical(read(path))==canonical(report),'Saved receipt differs from exact replay'
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    main()
