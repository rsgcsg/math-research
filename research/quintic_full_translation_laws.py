"""E065: sufficient single-word repair of ten full maximal motion domains.

UNSAT here is only a restricted color-frame search result, never a joint proof.
"""
from pathlib import Path
import json
import hashlib
from itertools import combinations
from joint_column_pricing import Encoding
from quintic_joint_ports import build


def main():
    from pysat.solvers import Solver
    root=Path(__file__).resolve().parents[1]
    _,points,_,edges,_,geometry,_=build(root);n=len(points)
    parent=(root/'certificates/quintic_joint_translations.json').read_bytes()
    source=(root/'certificates/joint_column_pricing.json').read_bytes()
    motions=json.loads(parent)['motions'];lookup={p:i for i,p in enumerate(points)}
    shifts={e['translation_label']:e['translation'] for e in json.loads(source)['events'] if e['translation'] is not None}
    for name,t in shifts.items():
        pairs=[]
        for i,p in enumerate(points):
            q=tuple(x+y for x,y in zip(p,t))
            if q in lookup:pairs.append([i,lookup[q]])
        motions.append(dict(name=name,translation=t,mapping=pairs))
    enc=Encoding(n,edges,[])
    for m,motion in enumerate(motions):
        def pv(a,b):return 5*n+25*m+5*a+b+1
        enc.clauses += [[pv(a,b) for b in range(5)] for a in range(5)]
        enc.clauses += [[pv(a,b) for a in range(5)] for b in range(5)]
        enc.clauses += [[-pv(a,b),-pv(a,c)] for a in range(5) for b,c in combinations(range(5),2)]
        enc.clauses += [[-pv(a,b),-pv(c,b)] for b in range(5) for a,c in combinations(range(5),2)]
        enc.clauses += [[-5*i-a-1,-pv(a,b),5*j+b+1] for i,j in motion['mapping'] for a in range(5) for b in range(5)]
    with Solver(name='cadical195',bootstrap_with=enc.clauses) as solver:
        solver.conf_budget(20000);answer=solver.solve_limited()
        result=dict(status='SAT' if answer else 'UNKNOWN' if answer is None else 'UNSAT_FRAME_SEARCH_ONLY')
        if answer:
            model=set(solver.get_model())
            result['word']=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(n))
            result['permutations']=[[next(b for b in range(5) if 5*n+25*m+5*a+b+1 in model) for a in range(5)] for m in range(len(motions))]
    data=dict(schema=1,experiment='E065',geometry=geometry,parent_sha256=hashlib.sha256(parent).hexdigest(),
              event_source_sha256=hashlib.sha256(source).hexdigest(),motions=motions,result=result,conflict_budget=20000)
    (root/'certificates/quintic_full_translation_laws.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],domains=[len(m['mapping']) for m in motions])),flush=True)


if __name__=='__main__':main()
