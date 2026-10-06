#!/usr/bin/env python3
"""Verify T171: exact four-atom law for aggregate P/Q/R counts on the T165 face."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'certificates/q_joint_boundary_gap.json'
CERT=ROOT/'certificates/pqr_total_boundary_projection_law.json'

def pair(a,b): return (a,b) if a<b else (b,a)
def req(x,msg):
    if not x: raise ValueError(msg)

def main():
    src=json.loads(SRC.read_text()); cert=json.loads(CERT.read_text())
    req(src['schema']=='q-joint-boundary-gap-v1','source schema')
    req(cert['schema']=='pqr-total-boundary-projection-law-v1' and cert['research_id']=='T171','certificate schema')
    b=src['boundary']; order=b['order']; ix={v:i for i,v in enumerate(order)}
    events={k:[pair(*t['pair']) for t in b['terms'] if t['type']==k] for k in ('P','Q','R')}
    req({k:len(v) for k,v in events.items()}=={'P':47,'Q':11,'R':31},'event counts')
    tags={pair(*t['pair']):t['type'] for t in b['terms']}
    for win in b['saturated_windows']:
        for i,a in enumerate(win):
            for d in win[i+1:]: tags.setdefault(pair(a,d),'E')
    edges={e for e,t in tags.items() if t=='E'}
    req(len(edges)==31,'unit edges')

    D=cert['denominator']; req(D==270,'denominator')
    atoms=cert['atoms']; req(len(atoms)==4 and sum(a['weight_numerator'] for a in atoms)==D,'four-atom mass')
    weighted={k:0 for k in events}; seen=set()
    individual={k:[0]*len(events[k]) for k in events}
    for atom in atoms:
        w=atom['weight_numerator']; c=atom['partition']
        req(type(w) is int and w>0 and len(c)==22,'atom')
        req(tuple(c) not in seen,'distinct atoms'); seen.add(tuple(c))
        req(c[0]==0 and all(type(x) is int and 0<=x<5 for x in c),'colors')
        top=0
        for x in c[1:]: req(x<=top+1,'restricted growth'); top=max(top,x)
        req(all(c[ix[a]]!=c[ix[d]] for a,d in edges),'proper')
        for win in b['saturated_windows']:
            same=sum(c[ix[a]]==c[ix[d]] for i,a in enumerate(win) for d in win[i+1:])
            req(same==2,'saturated window')
        a,o,d=b['PRR_triple']
        req((c[ix[a]]==c[ix[o]])+(c[ix[d]]==c[ix[o]])-(c[ix[a]]==c[ix[d]])==1,'PRR equality')
        actual={}
        for k,pairs in events.items():
            bits=[int(c[ix[a]]==c[ix[d]]) for a,d in pairs]
            actual[k]=sum(bits)
            weighted[k]+=w*actual[k]
            for j,v in enumerate(bits): individual[k][j]+=w*v
        req(actual==atom['counts'],'stored aggregate counts')

    # D times the exact C030 aggregate targets.
    req(weighted=={'P':470,'Q':2079,'R':4340},'exact target aggregate totals')
    # Deliberately not an eventwise balanced C030 law.
    req(any(27*x!=D for x in individual['P']),'P not eventwise 1/27')
    req(any(10*x!=7*D for x in individual['Q']),'Q not eventwise 7/10')
    req(any(27*x!=14*D for x in individual['R']),'R not eventwise 14/27')
    print(json.dumps({'status':'PASS','research_id':'T171','atoms':4,'denominator':D,
      'weighted_totals':weighted,'scope':cert['scope']},sort_keys=True))

if __name__=='__main__': main()
