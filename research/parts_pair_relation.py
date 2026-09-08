"""Cover all two-port five-color relations by directly saved colorings."""
import json
from pathlib import Path
from pysat.solvers import Solver
from parts_core import clauses


def run(path):
    data=json.loads(path.read_text())
    edges=[tuple(e) for e in data['induced_edges']]
    n=509
    full=(1<<n)-1
    equal=[1<<i for i in range(n)]
    different=[0]*n
    edge_masks=[0]*n
    for a,b in edges:
        edge_masks[a]|=1<<b;edge_masks[b]|=1<<a
    models=[]
    def add_model(colors):
        masks=[0]*5
        for i,c in enumerate(colors):
            masks[c]|=1<<i
        for i,c in enumerate(colors):
            equal[i]|=masks[c]
            different[i]|=full^masks[c]
        assert all(colors[a]!=colors[b] for a,b in edges)
        models.append(''.join(map(str,colors)))
    add_model(data['five_coloring'])
    failures=[]
    with Solver(name='cadical195',bootstrap_with=clauses(n,edges,5)) as solver:
        while True:
            requests=[('equal',i,(full^equal[i])&~edge_masks[i]&~((1<<(i+1))-1)) for i in range(n)]
            requests += [('different',i,(full^different[i])&~((1<<(i+1))-1)) for i in range(n)]
            request=next(((kind,i,(bits&-bits).bit_length()-1) for kind,i,bits in requests if bits),None)
            if request is None:
                break
            kind,i,j=request
            assumptions=[5*i+1,5*j+(1 if kind=='equal' else 2)]
            solver.conf_budget(100000)
            status=solver.solve_limited(assumptions=assumptions)
            if status is not True:
                failures.append(dict(relation=kind,pair=[i,j],status='UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'))
                break
            model=set(solver.get_model())
            colors=[next(c for c in range(5) if 5*v+c+1 in model) for v in range(n)]
            assert (colors[i]==colors[j])==(kind=='equal')
            add_model(colors)
            if len(models)%100==0:
                print(f'{len(models)} witnesses',flush=True)
    return dict(status='PAIR_RELATION_FULL' if not failures else 'PARTIAL_SEARCH',
                n=n,k=5,models=models,failures=failures,
                statement='every distinct pair can differ; every nonunit pair can agree')


if __name__=='__main__':
    result=run(Path('certificates/parts509_core.json'))
    Path('certificates/parts509_pairs.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],models=len(result['models']),failures=result['failures'])))
