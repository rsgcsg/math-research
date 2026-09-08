"""Five-color precoloring-extension search for every set of three ports.

Bitset coverage records all three partition types (3, 2+1, 1+1+1). Each SAT
model covers many requests. Negative results remain uncertified until replay.
"""
import argparse
import gzip
import json
import time
from pathlib import Path
from pysat.solvers import Solver
from parts_core import clauses


def run(limit):
    data=json.loads(Path('certificates/parts509_core.json').read_text())
    edges=[tuple(e) for e in data['induced_edges']]
    n=509;full=(1<<n)-1
    adjacent=[0]*n
    for a,b in edges:
        adjacent[a]|=1<<b;adjacent[b]|=1<<a
    mono=[0]*(n*n);pair=[0]*(n*n);distinct=[0]*(n*n)
    models=[]
    def add_model(word):
        colors=list(map(int,word))
        assert len(colors)==n and all(0<=c<5 for c in colors)
        assert all(colors[a]!=colors[b] for a,b in edges)
        masks=[0]*5
        for v,c in enumerate(colors):
            masks[c]|=1<<v
        for a in range(n):
            ma=masks[colors[a]]
            for b in range(a+1,n):
                index=n*a+b
                if colors[a]==colors[b]:
                    mono[index]|=ma
                    pair[index]|=full^ma
                else:
                    distinct[index]|=full^(ma|masks[colors[b]])
        models.append(word)
    started=time.monotonic()
    for word in json.loads(Path('certificates/parts509_pairs.json').read_text())['models']:
        add_model(word)
    print(f'Loaded {len(models)} pair witnesses in {time.monotonic()-started:.1f}s',flush=True)
    def missing():
        for a in range(n):
            for b in range(a+1,n):
                index=n*a+b
                later=full^((1<<(b+1))-1)
                if not(adjacent[a]>>b&1):
                    bits=later&~adjacent[a]&~adjacent[b]&~mono[index]
                    if bits:
                        return 'mono',[a,b,(bits&-bits).bit_length()-1],[0,0,0]
                    bits=full&~((1<<a)|(1<<b))&~pair[index]
                    if bits:
                        return 'pair',[a,b,(bits&-bits).bit_length()-1],[0,0,1]
                bits=later&~distinct[index]
                if bits:
                    return 'distinct',[a,b,(bits&-bits).bit_length()-1],[0,1,2]
        return None
    failures=[]
    requests=0
    with Solver(name='cadical195',bootstrap_with=clauses(n,edges,5)) as solver:
        while True:
            request=missing()
            if request is None:
                break
            if limit and requests>=limit:
                failures.append(dict(status='REQUEST_LIMIT',next=request))
                break
            kind,ports,colors=request
            assumptions=[5*v+c+1 for v,c in zip(ports,colors)]
            solver.conf_budget(100000)
            status=solver.solve_limited(assumptions=assumptions)
            requests+=1
            if status is not True:
                failures.append(dict(status='UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                                     kind=kind,ports=ports,colors=colors,
                                     core=solver.get_core() if status is False else None))
                print(json.dumps(failures[-1]),flush=True)
                break
            model=set(solver.get_model())
            word=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(n))
            assert all(int(word[v])==c for v,c in zip(ports,colors))
            add_model(word)
            if requests%100==0:
                print(f'{requests} new requests; {len(models)} witnesses; {time.monotonic()-started:.1f}s',flush=True)
    return dict(status='TRIPLE_RELATION_FULL' if not failures else 'PARTIAL_SEARCH',
                n=n,k=5,models=models,failures=failures,requests=requests,
                negative_results_certified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int,default=2000)
    args=parser.parse_args()
    result=run(args.limit)
    Path('certificates/parts509_triples.json.gz').write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k!='models'},indent=2))
