"""Exact maximal-domain diagnostics for a saved multiword law, not an obstruction.

Integer matrices are derived on every basis vector from the independently
checked field algebra. No floating point filter is used for domain membership.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import math
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice,digest


def run(root):
    parent,c=geometry(root,geometry_context=True)
    data=json.loads((root/'certificates/quintic_multiword_joint.json').read_text())
    assert data['geometry']==parent['geometry']
    words=data['result']['words'];assert all(len(w)==len(c['points']) for w in words)
    assert all(w[i]!=w[j] for w in words for i,j in c['edges'])
    r=c['ring'];mul=r['mul'];zero=(Q(0),)*32;one=(Q(1),)+zero[1:]
    eta=zero[:16]+one[:16];z=r['blocks'][0][64]
    omega=tuple(-2*a-3*b for a,b in zip(one,z))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    den=math.lcm(*(v.denominator for p in c['points'] for v in p))
    points=[tuple(int(v*den) for v in p) for p in c['points']];lookup={p:i for i,p in enumerate(points)}
    standard=[tuple(Q(int(i==j)) for i in range(32)) for j in range(32)]
    def mapping(a,t,reflection):
        columns=[mul(a,tuple(Q(v)/2 for v in conjugate_twice(e)) if reflection else e) for e in standard]
        scale=math.lcm(*(x.denominator for col in columns for x in col),*( (x*den).denominator for x in t))
        sparse=[[(i,int(x*scale)) for i,x in enumerate(col) if x] for col in columns]
        shift=[int(x*den*scale) for x in t];pairs=[]
        for index,p in enumerate(points):
            out=shift[:]
            for value,column in zip(p,sparse):
                if value:
                    for i,coeff in column:out[i]+=value*coeff
            if any(x%scale for x in out):continue
            q=tuple(x//scale for x in out)
            if q in lookup:pairs.append((index,lookup[q]))
        return pairs
    ep=[one];wp=[one]
    for _ in range(4):ep.append(mul(ep[-1],eta))
    for _ in range(2):wp.append(mul(wp[-1],omega))
    definitions=[]
    for j in range(5):
        for e in range(3):
            for sign in [1,-1]:
                for reflection in [False,True]:
                    a=tuple(sign*x for x in mul(ep[j],wp[e]))
                    definitions.append((f'H30_{j}_{e}_{sign}_{int(reflection)}',a,zero,reflection))
    for name,a in [('nu_squared',mul(nu,nu)),('tau_squared',mul(r['tau'],r['tau'])),
                   ('nu_eta',mul(nu,eta)),('nu_omega',mul(nu,omega)),('tau_eta',mul(r['tau'],eta)),
                   ('tau_omega',mul(r['tau'],omega))]:definitions.append((name,a,zero,False))
    definitions.append(('translation_eta_z',one,mul(eta,z),False))
    def pattern(word,indices):
        labels={};return tuple(labels.setdefault(word[i],len(labels)) for i in indices)
    reports=[]
    for name,a,t,reflection in definitions:
        pairs=mapping(a,t,reflection);source=[i for i,j in pairs];target=[j for i,j in pairs]
        left=Counter(pattern(w,source) for w in words);right=Counter(pattern(w,target) for w in words)
        witness=None
        if left!=right:
            # A small event when available. Absence of a pair event does not
            # erase a mismatch of the full-domain partition distribution.
            for (i,j),(k,l) in combinations(pairs[:200],2):
                counts=[sum(w[i]==w[k] for w in words),sum(w[j]==w[l] for w in words)]
                if counts[0]!=counts[1]:witness=dict(pairs=[[i,j],[k,l]],same_counts=counts);break
        report=dict(motion=name,domain=len(pairs),mapping_sha256=digest(pairs),
                    full_partition_equal=left==right,pair_witness=witness)
        reports.append(report);print(json.dumps(report),flush=True)
    return dict(experiment='E081',source_experiment='E080',probes=reports,
                scope='Diagnostics of this saved law only; no all-word obstruction or infinite extension claim')


if __name__=='__main__':print(json.dumps(run(Path(__file__).resolve().parents[1]),indent=2))
