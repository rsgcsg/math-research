#!/usr/bin/env python3
"""Exact stdlib verifier for T162's robust Q-defect inequality."""
from __future__ import annotations
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
OLD=ROOT/'certificates/q_pr_joint_cuts.json'; NEW=ROOT/'certificates/q_robust_capacity.json'
W=(2,1,1,1,1,2,2,1,2)
ORDER=(33,35,229,231,233,877,887,4641,227,31,235,37,875,889,3483,5535,873,891,3477,7479,7489)
SHARP='002130244211300443302'
OPT=((7,(0,),'012323201234431010212'),(5,(5,6),'012034241210301413412'),(6,(1,2,3),'012223441023002411242'),(5,(3,4,8),'012123443313001442210'),(5,(2,7,8),'010234334024201001340'),(6,(1,4,7),'012130431212403412311'))

def load():
    old=json.loads(OLD.read_text()); q=old['quotient']; v=q['vertices']; rel={'E':[],'P':[],'R':[]}
    for x in q['realizations']:
        if x['type'] in rel: rel[x['type']].append(tuple(x['actual_pair']))
    Q=[tuple(x) for x in q['Q_bridges']]
    new=json.loads(NEW.read_text())
    assert new['schema']=='q-robust-capacity-v1' and new['q_weights']==list(W) and new['penalty_sum']==13
    assert new['sharp_witness']==SHARP and new['minimum_score']==9
    assert new['optimality_witnesses']==[{'s':s,'broken':list(b),'coloring':c} for s,b,c in OPT]
    assert len(v)==21 and [len(rel[k]) for k in ('E','P','R')]==[18,36,12] and len(Q)==9
    assert set(ORDER)==set(v) and sum(W)==13
    return v,rel,Q

def stats(word,v,rel,Q):
    assert len(word)==len(v) and all('0'<=x<='4' for x in word)
    c=dict(zip(v,map(int,word)))
    assert all(c[a]!=c[b] for a,b in rel['E'])
    s=sum(c[a]==c[b] for a,b in rel['P']+rel['R'])
    broken=tuple(i for i,(a,b) in enumerate(Q) if c[a]!=c[b])
    return s,broken,s+sum(W[i] for i in broken)

def search_below(threshold,v,rel,Q):
    pos={x:i for i,x in enumerate(ORDER)}; prev={x:[] for x in v}
    for a,b in rel['E']:
        if pos[a]>pos[b]: a,b=b,a
        prev[b].append((a,'E',0))
    for a,b in rel['P']+rel['R']:
        if pos[a]>pos[b]: a,b=b,a
        prev[b].append((a,'S',1))
    for i,(a,b) in enumerate(Q):
        if pos[a]>pos[b]: a,b=b,a
        prev[b].append((a,'Q',W[i]))
    a={}; nodes=0
    def rec(i,m,cost):
        nonlocal nodes; nodes+=1
        if cost>=threshold:return None
        if i==len(ORDER): return ''.join(str(a[x]) for x in v)
        x=ORDER[i]
        for col in range(min(4,m+1)+1):
            d=0; ok=True
            for u,k,w in prev[x]:
                same=col==a[u]
                if k=='E' and same: ok=False; break
                if k=='S' and same:d+=1
                if k=='Q' and not same:d+=w
            if ok and cost+d<threshold:
                a[x]=col
                z=rec(i+1,max(m,col),cost+d)
                if z is not None:return z
                del a[x]
        return None
    return rec(0,-1,0),nodes

def main():
    v,rel,Q=load(); assert stats(SHARP,v,rel,Q)==(9,(),9)
    for s,b,c in OPT: assert stats(c,v,rel,Q)[:2]==(s,b)
    # These six colorings force u0>=2, u5+u6>=4 and four inequalities whose half-sum is 7.
    mult={i:0 for i in (1,2,3,4,7,8)}
    for _,b,_ in OPT[2:]:
        for i in b: mult[i]+=1
    assert set(mult.values())=={2} and 2+4+(3+4+4+3)//2==13
    bad,nodes=search_below(9,v,rel,Q); assert bad is None
    if '--self-test' in sys.argv:
        bad10,_=search_below(10,v,rel,Q); assert bad10 is not None and stats(bad10,v,rel,Q)[2]==9
    print(f'PASS q-robust-capacity nodes={nodes} min_score=9 penalty_sum=13 expectation: 36p+12r+13(1-q)>=9; with T161 2r-p<=1: 42p+13(1-q)>=3')
if __name__=='__main__': main()
