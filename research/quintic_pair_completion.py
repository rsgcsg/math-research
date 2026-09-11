"""E064: unrestricted proper-five-color pair extension queries (search only)."""
from pathlib import Path
import hashlib
import json
from joint_column_pricing import Encoding
from quintic_joint_ports import build


def main():
    from pysat.solvers import Solver
    root=Path(__file__).resolve().parents[1]
    source=(root/'certificates/joint_column_pricing.json').read_bytes()
    old=json.loads(source)
    words=old['initial_words']+[s['word'] for s in old['history'] if s['status']=='SAT']+old['result']['words']
    _,points,_,edges,_,geometry,_=build(root)
    n=len(points);covered=[0]*n;neighbors=[0]*n
    for w in words:
        masks=[0]*5
        for i,c in enumerate(w):masks[int(c)]|=1<<i
        for i,c in enumerate(w):covered[i]|=masks[int(c)]
    for i,j in edges:neighbors[i]|=1<<j;neighbors[j]|=1<<i
    missing=[]
    for i in range(n):
        bits=((1<<n)-1)&~(covered[i]|neighbors[i])&~((1<<(i+1))-1)
        while bits:
            bit=bits&-bits;missing.append([i,bit.bit_length()-1]);bits-=bit
    results=[]
    with Solver(name='cadical195',bootstrap_with=Encoding(n,edges,[]).clauses) as solver:
        for i,j in missing:
            solver.conf_budget(20000)
            answer=solver.solve_limited(assumptions=[5*i+1,5*j+1])
            entry=dict(pair=[i,j],status='SAT' if answer else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY')
            if answer:
                model=set(solver.get_model())
                entry['word']=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(n))
            results.append(entry)
            print(json.dumps({k:v for k,v in entry.items() if k!='word'}),flush=True)
    encoding=Encoding(n,edges,[])
    for i,j in missing:encoding.clauses.append([encoding.equal(i,j)])
    with Solver(name='cadical195',bootstrap_with=encoding.clauses) as solver:
        solver.conf_budget(20000);answer=solver.solve_limited()
        joint=dict(status='SAT' if answer else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY')
        if answer:
            model=set(solver.get_model())
            joint['word']=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(n))
    print(json.dumps(dict(joint_status=joint['status'])),flush=True)
    data=dict(schema=1,experiment='E064',source_sha256=hashlib.sha256(source).hexdigest(),
              geometry=geometry,conflict_budget=20000,queries=results,joint_same=joint)
    (root/'certificates/quintic_pair_completion.json').write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
