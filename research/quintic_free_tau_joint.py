"""Free one-word search, then S5 averaging, on thirteen full Y domains.

No fixed residue-character restrictions. Failure is only a one-word failure;
old infinite integral-motion obligations are not replaced by these thirteen.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice,digest
from joint_column_pricing import Encoding


def run(root,budget=20000):
    from pysat.solvers import Solver
    parent,c=geometry(root,geometry_context=True)
    r=c['ring'];mul=r['mul'];pts=c['points'];lookup={p:i for i,p in enumerate(pts)}
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16];z=r['blocks'][0][64]
    add=lambda p,q:tuple(a+b for a,b in zip(p,q))
    bar=lambda p:tuple(Q(x)/2 for x in conjugate_twice(p))
    omega=tuple(-2*a-3*b for a,b in zip(one,z))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    definitions=[('tau',r['tau'],zero,False),('nu',nu,zero,False),('eta',eta,zero,False),
                 ('omega',omega,zero,False),('bar',one,zero,True),
                 ('bridge',tuple(-x for x in eta),add(one,mul(eta,z)),False),
                 ('translation_one',one,one,False),('translation_z',one,z,False)]
    power=one
    for j in range(1,5):
        power=mul(power,eta);definitions.append((f'one_plus_eta_{j}',one,add(one,power),False))
    definitions.append(('bridge_shift',one,add(one,mul(eta,z)),False))
    e=Encoding(len(pts),c['edges'],[])
    for k,idx in enumerate([0,153,150]):e.clauses.append([5*lookup[r['blocks'][0][idx]]+k+1])
    history=[];motion_vars=[];maps=[];positive=None
    with Solver(name='cadical195',bootstrap_with=e.clauses) as solver:
        for name,a,t,reflection in definitions:
            mapping=[(i,lookup[q]) for i,p in enumerate(pts)
                     if (q:=add(t,mul(a,bar(p) if reflection else p))) in lookup]
            pi=[[e.fresh() for b in range(5)] for aa in range(5)];clauses=[]
            for group in pi+list(map(list,zip(*pi))):
                clauses.append(group);clauses.extend([-x,-y] for x,y in combinations(group,2))
            clauses.extend([-5*i-aa-1,-pi[aa][b],5*j+b+1]
                           for i,j in mapping for aa in range(5) for b in range(5))
            solver.append_formula(clauses);solver.conf_budget(budget)
            ans=solver.solve_limited()
            status='SAT' if ans is True else 'UNSAT_ONE_WORD_ONLY' if ans is False else 'UNKNOWN'
            stage=dict(motion=name,status=status,domain=len(mapping),stats=solver.accum_stats())
            history.append(stage);print(json.dumps(stage),flush=True)
            if ans is not True:break
            maps.append(mapping);motion_vars.append(pi)
            model={v for v in solver.get_model() if v>0}
            word=''.join(str(next(k for k in range(5) if 5*i+k+1 in model)) for i in range(len(pts)))
            perms=[[next(b for b in range(5) if row[b] in model) for row in p] for p in motion_vars]
            positive=dict(word=word,permutations=perms,motions=[d[0] for d in definitions[:len(maps)]],
                          mapping_sha256=[digest(m) for m in maps])
            print(json.dumps(dict(positive=positive)),flush=True)
    return dict(experiment='E079',geometry=parent['geometry'],history=history,result=positive,
                scope='Positive selected full domains only; not all integral motions, all congruences, or a new HN bound')


if __name__=='__main__':print(json.dumps(run(Path(__file__).resolve().parents[1]),indent=2))
