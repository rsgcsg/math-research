#!/usr/bin/env python3
"""Independent small-graph calibration of the weighted A/B/C odd-cycle lemma."""
import argparse
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path
if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')


def pair(a,b):return tuple(sorted((a,b)))


def odd_cycles(n):
    out=[]
    for length in range(3,n+1,2):
        for subset in combinations(range(n),length):
            for tail in permutations(subset[1:]):
                if tail[0]>tail[-1]:continue
                order=(subset[0],)+tail
                out.append((order,{pair(order[i],order[(i+1)%length]) for i in range(length)}))
    return out


def hypotheses(types,edges):
    n=len(types);adj=[set() for _ in types]
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    A={i for i,t in enumerate(types) if t=='A'}
    B={i for i,t in enumerate(types) if t=='B'}
    C={i for i,t in enumerate(types) if t=='C'}
    assert A|B|C==set(range(n))
    if any(adj[a]&A for a in A):return False
    if any(len(adj[a]&B)>1 for a in A):return False
    color={}
    for start in A|B:
        if start in color:continue
        color[start]=0;queue=[start]
        for u in queue:
            for v in adj[u]&(A|B):
                if v not in color:color[v]=1-color[u];queue.append(v)
                elif color[v]==color[u]:return False
    for c in C:
        stars=[]
        for a in adj[c]&A:
            bs=adj[a]&B
            if bs&adj[c]:return False  # C-A-B triangle.
            stars.extend(bs)
        if any(pair(b,d) in edges for b,d in combinations(stars,2)):
            return False  # C-A-B-B-A five-cycle; a repeated B has no self-edge.
    return True


def largest_excess(types,edges,p,cycles=None):
    weights={'A':(1+p)/2,'B':(1-p)/2,'C':p}
    best=F(-1000)
    for order,required in (cycles if cycles is not None else odd_cycles(len(types))):
        if required<=edges:
            excess=sum(weights[types[i]] for i in order)-F(len(order)-1,2)
            best=max(best,excess)
    return best


def verify_conflict_characterization():
    # Two distinct-coordinate triples involve at most six physical vertices.
    # Fix the first triple by relabeling; these 120 second triples cover every
    # overlap pattern, including all-disjoint and identical triples.
    def parts(a):
        if len(a)==6:
            yield tuple(a)
            return
        for x in range(max(a)+2):
            yield from parts(a+[x])
    ps=list(parts([0]));assert len(ps)==203
    u=(0,1,2);posu=pair(1,2);negu={pair(0,1),pair(0,2)}
    count=0
    for v in permutations(range(6),3):
        i,j,k=v;posv=pair(j,k);negv={pair(i,j),pair(i,k)}
        symbolic=(posu in negv or posv in negu)
        simultaneous=any(z[1]==z[2] and z[0]!=z[1]
                         and z[j]==z[k] and z[i]!=z[j] for z in ps)
        assert symbolic==(not simultaneous)
        count+=1
    assert count==120
    return count


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true');args=ap.parse_args()
    conflict_checks=verify_conflict_characterization()
    types='AABBCC';cycles=odd_cycles(6)
    # All simple graphs on two vertices of each type satisfying the first two
    # hypotheses by construction. The remaining hypotheses are checked directly.
    free=[(2,3),(0,4),(0,5),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5),(4,5)]
    total=qualified=0
    for choices in product([None,2,3],repeat=2):
        base={pair(a,b) for a,b in enumerate(choices) if b is not None}
        for mask in range(1<<len(free)):
            edges=base|{e for j,e in enumerate(free) if mask>>j&1}
            total+=1
            if not hypotheses(types,edges):continue
            qualified+=1
            for p in (F(0),F(1,27),F(1,5)):
                assert largest_excess(types,edges,p,cycles)<=0
    # Each following counterexample fails a specific necessary input condition.
    tests=[
        ('A-independence','AAC',{(0,1),(0,2),(1,2)}),
        ('AB-bipartiteness','BBB',{(0,1),(0,2),(1,2)}),
        ('A-degree-to-B','CABAB',{(0,1),(1,2),(2,3),(3,4),(0,4)}),
        ('forbidden-CAB-triangle','CAB',{(0,1),(1,2),(0,2)}),
        ('forbidden-CABBA-five-cycle','CABBA',{(0,1),(1,2),(2,3),(3,4),(0,4)}),
    ]
    witnesses=[]
    for name,labels,edges in tests:
        assert not hypotheses(labels,edges)
        excess=largest_excess(labels,edges,F(1,5))
        assert excess>0
        witnesses.append(dict(missing_hypothesis=name,types=labels,edges=[list(e) for e in sorted(edges)],excess=str(excess)))
    sharp_types='ACC';sharp_edges={(0,1),(0,2),(1,2)}
    assert hypotheses(sharp_types,sharp_edges)
    assert largest_excess(sharp_types,sharp_edges,F(1,5))==0
    assert largest_excess(sharp_types,sharp_edges,F(1,4))==F(1,8)
    report=dict(schema='star-odd-cycle-lemma-calibration-v1',status='PASS_SMALL_GRAPH_CALIBRATION',
                all_constructed_graphs=total,graphs_satisfying_all_hypotheses=qualified,
                conflict_overlap_cases=conflict_checks,six_vertex_partitions_per_case=203,
                odd_cycle_templates=len(cycles),parameter_samples=['0','1/27','1/5'],
                hypothesis_counterexamples=witnesses,
                sharp_parameter_boundary=dict(types=sharp_types,edges=[list(e) for e in sorted(sharp_edges)],p='1/4',excess='1/8'),
                scope='Small-graph calibration and hypothesis rejection examples only. The arbitrary-size theorem is proved by the A/B/C count argument and star path reduction, not inferred from this finite test.')
    path=Path(__file__).resolve().parents[1]/'certificates/star_odd_cycle_lemma_calibration.json'
    if args.write_receipt:path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    else:assert json.loads(path.read_text())==report,'Saved receipt differs from exact replay'
    print(json.dumps(dict(status=report['status'],graphs=total,qualified=qualified,
                         hypothesis_counterexamples=len(witnesses),parameter_boundary_sharp=True)))


if __name__=='__main__':main()
