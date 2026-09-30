#!/usr/bin/env python3
"""Four-point calibration: eliminating hidden pairs is stronger than deleting nodes."""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations,permutations
import json
from pathlib import Path
if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')


def pair(a,b):return tuple(sorted((a,b)))

def patterns(n):
    def rec(a):
        if len(a)==n:
            yield tuple(a);return
        for x in range(max(a)+2):yield from rec(a+[x])
    yield from rec([0])

def pattern(word):
    names={};out=[]
    for x in word:
        if x not in names:names[x]=len(names)
        out.append(names[x])
    return tuple(out)

def conflict(u,v):
    i,j,k=u;l,a,b=v
    return pair(j,k) in {pair(l,a),pair(l,b)} or pair(a,b) in {pair(i,j),pair(i,k)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true');args=ap.parse_args()
    points=[F(i,3) for i in range(4)]
    E={e for e in combinations(range(4),2) if (points[e[1]]-points[e[0]])**2==1}
    assert E=={(0,3)}
    S={(0,1),(1,2),(2,3)};U=E|S
    motion={0:1,1:2,2:3}
    assert all(points[b]-points[a]==F(1,3) for a,b in motion.items())
    transports=[(e,pair(motion[e[0]],motion[e[1]])) for e in sorted(S) if set(e)<=motion.keys()]
    assert transports==[((0,1),(1,2)),((1,2),(2,3))]
    nodes=[t for t in permutations(range(4),3) if pair(t[0],t[1]) in U and pair(t[1],t[2]) in U]
    assert len(nodes)==8
    known={e:F(1) for e in S};known.update({e:F(0) for e in E})
    z={t:known[pair(t[1],t[2])]-known[pair(t[0],t[1])] for t in nodes}
    positive={t for t in nodes if z[t]>0}
    assert positive=={(3,0,1),(0,3,2)}
    assert not any(conflict(a,b) for a,b in combinations(positive,2))
    assert all(z[t]<=int(t in positive) for t in nodes)
    # The vector for any s in [0,1] is s*z and is dominated by the stable-set
    # mixture s*1_positive+(1-s)*1_empty. This certifies the whole induced lift.
    terms=[[(3,0,1),(0,2,1)],[(3,0,2),(0,3,2)]]
    coefficients=Counter()
    allparts=list(patterns(4));assert len(allparts)==15
    for edge in terms:
        assert conflict(*edge)
        for t in edge:
            i,j,k=t;coefficients[pair(j,k)]+=1;coefficients[pair(i,j)]-=1
        for w in allparts:
            score=sum(int(w[j]==w[k])-int(w[i]==w[j]) for i,j,k in edge)
            assert score<=1
    coefficients={e:a for e,a in coefficients.items() if a}
    assert coefficients=={(0,1):1,(1,2):1,(2,3):1,(0,3):-3}
    proper=[w for w in allparts if w[0]!=w[3]];assert len(proper)==10
    assert max(sum(w[a]==w[b] for a,b in S) for w in proper)==2
    maximal=[tuple([0]*s+[1]*(4-s)) for s in range(1,4)]
    minimal=[(0,1,0,1)]
    for words,target in [(maximal,F(2,3)),(minimal,F(0))]:
        assert all(w[0]!=w[3] and len(set(w))<=2 for w in words)
        assert all(F(sum(w[a]==w[b] for w in words),len(words))==target for a,b in S)
        assert Counter(pattern(w[:3]) for w in words)==Counter(pattern(w[1:]) for w in words)
    report=dict(schema='hidden-pair-elimination-calibration-v1',status='PASS_EXACT_FOUR_POINT_PROJECTION_GAP',
                points=[str(x) for x in points],actual_unit_edges=[list(e) for e in sorted(E)],
                observed_step_pairs=[list(e) for e in sorted(S)],partial_translation='1/3',
                known_node_count=len(nodes),positive_independent_set=[list(t) for t in sorted(positive)],
                induced_antidominant_stable_set_feasible_interval=['0','1'],
                eliminating_BW_edges=terms,eliminated_unknown_pair=[0,2],
                combined_coefficients=[dict(pair=list(e),coefficient=a) for e,a in sorted(coefficients.items())],
                combined_upper_bound=2,full_partition_and_translation_law_interval=['0','2/3'],
                all_partitions=15,proper_partitions=10,
                maximum_law=[list(w) for w in maximal],maximum_law_weights=['1/3']*3,
                minimum_law=[list(w) for w in minimal],minimum_law_weights=['1'],
                scope='A standard variable-elimination mechanism on a separate exact four-point plane configuration. Not a stronger P/R inequality on the research Y, not a full15 result, and not a chromatic lower bound.')
    root=Path(__file__).resolve().parents[1]
    path=root/'certificates/hidden_pair_elimination.json'
    # Normalize tuple-only presentation fields before comparing a JSON receipt.
    report=json.loads(json.dumps(report,sort_keys=True))
    if args.write_receipt:path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    else:assert json.loads(path.read_text())==report,'Saved receipt differs from exact replay'
    print(json.dumps(dict(status=report['status'],known_nodes=8,all_partitions=15,proper_partitions=10,
                         induced_interval=['0','1'],true_interval=['0','2/3'])))


if __name__=='__main__':main()
