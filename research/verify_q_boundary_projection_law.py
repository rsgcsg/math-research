#!/usr/bin/env python3
"""Verify T170: a 12-atom exact Q-projection law on the T165 boundary face."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'certificates/q_joint_boundary_gap.json'
CERT=ROOT/'certificates/q_boundary_projection_law.json'

def pair(a,b): return (a,b) if a<b else (b,a)
def req(x,msg):
    if not x: raise ValueError(msg)

def main():
    src=json.loads(SRC.read_text())
    cert=json.loads(CERT.read_text())
    req(src['schema']=='q-joint-boundary-gap-v1','source schema')
    req(cert['schema']=='q-boundary-projection-law-v1' and cert['research_id']=='T170','certificate schema')
    b=src['boundary']; order=b['order']; ix={v:i for i,v in enumerate(order)}
    req(len(order)==22 and len(set(order))==22,'W22 order')
    windows=b['saturated_windows']
    q_pairs=[pair(*t['pair']) for t in b['terms'] if t['type']=='Q']
    p_pairs=[pair(*t['pair']) for t in b['terms'] if t['type']=='P']
    r_pairs=[pair(*t['pair']) for t in b['terms'] if t['type']=='R']
    req(len(q_pairs)==11 and len(set(q_pairs))==11,'eleven Q events')

    tags={pair(*t['pair']):t['type'] for t in b['terms']}
    for w in windows:
        req(len(w)==7 and len(set(w))==7,'window')
        for i,a in enumerate(w):
            for c in w[i+1:]:
                tags.setdefault(pair(a,c),'E')
    edges={p for p,t in tags.items() if t=='E'}
    req(len(edges)==31,'reconstructed unit edges')

    D=cert['denominator']; atoms=cert['atoms']
    req(D==840 and len(atoms)==12,'fixed denominator/support')
    req(sum(a['weight_numerator'] for a in atoms)==D,'probability mass')
    q_sums=[0]*11
    p_sums=[0]*len(p_pairs); r_sums=[0]*len(r_pairs)
    seen=set()

    for atom in atoms:
        w=atom['weight_numerator']; c=atom['partition']
        req(type(w) is int and w>0,'positive integer weight')
        req(len(c)==22 and all(type(x) is int and 0<=x<5 for x in c),'five-block word')
        req(tuple(c) not in seen,'distinct atoms'); seen.add(tuple(c))
        # restricted-growth canonical representation, used only to pin the words
        req(c[0]==0,'canonical first color')
        top=0
        for x in c[1:]:
            req(x<=top+1,'restricted-growth word')
            top=max(top,x)
        req(all(c[ix[a]]!=c[ix[d]] for a,d in edges),'proper on all certified unit edges')
        for win in windows:
            same=sum(c[ix[a]]==c[ix[d]] for i,a in enumerate(win) for d in win[i+1:])
            req(same==2,'saturated K7 has exactly two equal pairs')
        a,o,d=b['PRR_triple']
        req((c[ix[a]]==c[ix[o]])+(c[ix[d]]==c[ix[o]])-(c[ix[a]]==c[ix[d]])==1,'PRR equality')
        mask=0
        for j,(a,d) in enumerate(q_pairs):
            bit=(c[ix[a]]==c[ix[d]])
            if bit: mask|=1<<j
            q_sums[j]+=w*bit
        req(mask==atom['q_mask'],'stored Q mask')
        for j,(a,d) in enumerate(p_pairs): p_sums[j]+=w*(c[ix[a]]==c[ix[d]])
        for j,(a,d) in enumerate(r_pairs): r_sums[j]+=w*(c[ix[a]]==c[ix[d]])

    req(all(10*s==7*D for s in q_sums),'all Q marginals equal 7/10')
    # This law is deliberately only a Q-projection witness.
    req(len(set(p_sums))>1 and len(set(r_sums))>1,'P/R are not balanced')
    req(not all(27*s==D for s in p_sums),'not C030 P marginals')
    req(not all(27*s==14*D for s in r_sums),'not C030 R marginals')
    print(json.dumps({
      'status':'PASS','research_id':'T170','atoms':len(atoms),'denominator':D,
      'q_events':len(q_pairs),'q_numerators':q_sums,
      'distinct_P_marginals':len(set(p_sums)),'distinct_R_marginals':len(set(r_sums)),
      'scope':cert['scope']
    },sort_keys=True))

if __name__=='__main__': main()
