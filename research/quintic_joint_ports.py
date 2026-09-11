"""E061 search: genuine mixed maximal congruences and free full-pattern repairs.

One color-equivariant word is a sufficient positive law after S5 averaging.
Failure of this restricted witness class is never a negative joint certificate.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse
import hashlib
import json
from quintic_second_host import multiply,conjugate,add
from quintic_independent_center import geometry


def build(root):
    raw=(root/'certificates/parts509_core.json').read_bytes()
    P=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in json.loads(raw)['points']]
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    power=one;blocks=[P]
    for j in range(4):
        power=multiply(power,eta);r=tuple(-x for x in power);A=add(r,conjugate(r))
        blocks.extend([[multiply(r,p) for p in P],[multiply(r,add(A,p)) for p in P]])
    translation=add(one,multiply(eta,P[64]));minus_eta=tuple(-x for x in eta)
    blocks.append([add(translation,multiply(minus_eta,p)) for p in P])
    pts,ids,edges,den,summary=geometry(blocks)
    physical=[tuple(Q(x,den) for x in p) for p in pts];lookup={p:i for i,p in enumerate(physical)}
    motions=[]
    for name,r,t,reflection in [('eta',eta,zero,False),('conjugate',one,zero,True),('bridge',minus_eta,translation,False)]:
        mapping=[]
        for i,p in enumerate(physical):
            q=add(t,multiply(r,conjugate(p) if reflection else p))
            if q in lookup:mapping.append([i,lookup[q]])
        source={i for i,j in mapping};target={j for i,j in mapping}
        assert not any(source<=set(b) or target<=set(b) for b in ids)
        # Small mixed witness: both domain and image escape every single copy.
        witness=[]
        for pair in mapping:
            if not witness:witness.append(pair);continue
            old_s={i for i,j in witness};old_t={j for i,j in witness}
            old_score=sum(old_s<=set(b) for b in ids)+sum(old_t<=set(b) for b in ids)
            s=old_s|{pair[0]};tgt=old_t|{pair[1]}
            score=sum(s<=set(b) for b in ids)+sum(tgt<=set(b) for b in ids)
            if score<old_score:witness.append(pair)
            if score==0:break
        witness += [p for p in mapping if p not in witness][:max(0,4-len(witness))]
        motions.append(dict(name=name,mapping=mapping,mixed_witness=witness))
    return raw,pts,ids,edges,den,summary,motions


def run(root,budget=100000,include_translations=False):
    from pysat.solvers import Solver
    raw,pts,ids,edges,den,summary,motions=build(root);n=len(pts)
    if include_translations:
        lookup={p:i for i,p in enumerate(pts)}
        for name,t in [('translation_one',(den,)+(0,)*31),('translation_z',pts[ids[0][64]])]:
            mapping=[]
            for i,p in enumerate(pts):
                q=tuple(x+y for x,y in zip(p,t))
                if q in lookup:mapping.append([i,lookup[q]])
            motions.append(dict(name=name,mapping=mapping,mixed_witness=[]))
    clauses=[[5*v+k+1 for k in range(5)] for v in range(n)]
    clauses += [[-5*v-k-1,-5*v-l-1] for v in range(n) for k,l in combinations(range(5),2)]
    clauses += [[-5*i-k-1,-5*j-k-1] for i,j in edges for k in range(5)]
    stages=[]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        for m,motion in enumerate(motions):
            def pv(a,b):return 5*n+25*m+5*a+b+1
            cc=[[pv(a,b) for b in range(5)] for a in range(5)]
            cc += [[pv(a,b) for a in range(5)] for b in range(5)]
            cc += [[-pv(a,b),-pv(a,c)] for a in range(5) for b,c in combinations(range(5),2)]
            cc += [[-pv(a,b),-pv(c,b)] for b in range(5) for a,c in combinations(range(5),2)]
            cc += [[-5*i-a-1,-pv(a,b),5*j+b+1] for i,j in motion['mapping'] for a in range(5) for b in range(5)]
            solver.append_formula(cc);solver.conf_budget(budget);answer=solver.solve_limited()
            stage=dict(motions=m+1,status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY')
            if answer is True:
                model=set(solver.get_model())
                stage['word']=''.join(str(next(a for a in range(5) if 5*v+a+1 in model)) for v in range(n))
                stage['permutations']=[[next(b for b in range(5) if 5*n+25*g+5*a+b+1 in model) for a in range(5)] for g in range(m+1)]
            stages.append(stage);print(json.dumps({k:v for k,v in stage.items() if k!='word'}),flush=True)
            if answer is not True:break
    return dict(schema=1,experiment='E062' if include_translations else 'E061',core_sha256=hashlib.sha256(raw).hexdigest(),geometry=summary,
                denominator=den,motions=motions,stages=stages,budget=budget,
                scope='Only selected maximal congruences; equivariant-word failure is not full-joint infeasibility')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);parser.add_argument('--budget',type=int,default=100000)
    parser.add_argument('--translations',action='store_true')
    args=parser.parse_args();data=run(Path(__file__).resolve().parents[1],args.budget,args.translations)
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
