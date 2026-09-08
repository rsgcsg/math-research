"""Canonical S6 transfer relations and a finite invariant search for long chains.

At each layer rotate the A/B indices to place its shared point at A0 and
normalize the central B phase at the left port. Node type is (local increment,
central increment). The output frame changes between nodes by h_b.
Only maximal difference supports (full or missing one residue) are needed.
"""
from collections import deque
from itertools import permutations, product
from pathlib import Path
import argparse
import json

FRAMES = [(0,)+p for p in permutations(range(1,6))]
TYPES = list(product((0,-1),repeat=2))
ROOTS = [(-2,1),(-1,-1),(-1,2),(1,-2),(1,1),(2,-1)]


def c(m,n,step):
    return n%3 if m%2==0 else 3+(n+(step if m//2==0 else 0))%3


def h(color,b):
    return (color+1)%3 if color<3 else 3+(color-3+1-b)%3


def bits(mask):
    while mask:
        bit=mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def relations():
    domains = {t:sum(1<<i for i,p in enumerate(FRAMES)
                     if all(p[c(m,n,t[0])]!=c(m,n,t[1]) for m,n in ROOTS)) for t in TYPES}
    transitions = {}
    for t,nt in product(TYPES,repeat=2):
        a,b=t
        for omitted in [-1]+[r for r in range(3) if r != (-a)%3]:
            support = [d for d in range(3) if d!=omitted]
            table = [0]*len(FRAMES)
            for i in bits(domains[t]):
                p=FRAMES[i]
                for j in bits(domains[nt]):
                    q=FRAMES[j]
                    if all(h(p[x],b)!=q[(x+1)%3] for x in range(3)) and all(
                        h(p[3+x],b)!=q[3+(x+d+1)%3] for x in range(3) for d in support):
                        table[i] |= 1<<j
            transitions[t,nt,omitted]=table
    return domains,transitions


def advance(mask,table):
    out=0
    for i in bits(mask):
        out |= table[i]
    return out


def run(limit=100000):
    domains, transitions=relations()
    pools={(t,f):set() for t in TYPES for f in range(3)}
    queue=deque()
    for t in TYPES:
        pools[t,0].add(domains[t])
        queue.append((t,0,domains[t],[]))
    steps=0
    while queue:
        t,f,mask,trace=queue.popleft()
        if mask not in pools[t,f]:
            continue
        steps+=1
        if steps>limit:
            return dict(status='UNKNOWN_LIMIT', processed=steps)
        for nt in TYPES:
            for omitted in [-1]+[r for r in range(3) if r != (-t[0])%3]:
                if omitted == -1 and f == 2:
                    continue
                nf=f+1 if omitted==-1 else 0
                nm=advance(mask,transitions[t,nt,omitted])
                edge=dict(source_type=t,target_type=nt,omitted=omitted)
                if not nm:
                    return dict(status='ABSTRACT_COUNTEREXAMPLE', trace=trace+[edge],
                                processed=steps, source_frames=list(bits(mask)))
                pool=pools[nt,nf]
                if any(old & nm == old for old in pool):
                    continue
                pool.difference_update(old for old in list(pool) if old & nm == nm)
                pool.add(nm)
                queue.append((nt,nf,nm,trace+[edge]))
    return dict(status='CLOSED_NONEMPTY_INVARIANT',processed=steps,
                domains={str(t):bin(d).count('1') for t,d in domains.items()},
                invariant=[dict(node_type=t,full_run=f,frames=list(bits(mask)))
                           for (t,f),pool in pools.items() for mask in sorted(pool)])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    parser.add_argument('--limit',type=int,default=100000)
    args=parser.parse_args()
    result=run(args.limit)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result if result['status']!='CLOSED_NONEMPTY_INVARIANT' else
                     {k:v for k,v in result.items() if k!='invariant'} | {'invariant_sets':len(result['invariant'])},indent=2))
