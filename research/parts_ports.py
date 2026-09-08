"""Actual five-color boundary relations of the induced Parts 509 graph.

Tests two central hexagons in different algebraic directions, with their common
center. No monochromaticity or activation is assumed of arbitrary colorings.
Every positive model is saved; UNSAT remains a search result until DRAT checked.
"""
import argparse
import gzip
import json
import time
from pathlib import Path
from pysat.solvers import Solver
from parts_core import clauses
from relations import color_partitions


def cycle_at(adjacency,first):
    neighbors=adjacency[0]
    cycle=[first]
    while len(cycle)<6:
        choices=sorted((adjacency[cycle[-1]]&neighbors)-set(cycle))
        assert choices
        cycle.append(choices[0])
    assert first in adjacency[cycle[-1]]
    return cycle


def run(core_path,first,second,limit=0):
    data=json.loads(core_path.read_text())
    edges=[tuple(e) for e in data['induced_edges']]
    adjacency=[set() for _ in range(509)]
    for a,b in edges:
        adjacency[a].add(b);adjacency[b].add(a)
    ports=cycle_at(adjacency,first)+cycle_at(adjacency,second)
    assert len(ports)==len(set(ports))==12
    edge_set=set(edges)
    port_edges=[(a,b) for a in range(12) for b in range(a+1,12)
                if tuple(sorted((ports[a],ports[b]))) in edge_set]
    assert len(port_edges)==12
    cases=list(color_partitions(12,port_edges,4))
    assert len(cases)==22327
    models=[]
    failures=[]
    started=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=clauses(509,edges,5)) as solver:
        for index,word in enumerate(cases):
            if limit and index>=limit:
                break
            assumptions=[1]+[5*v+c+2 for v,c in zip(ports,word)]
            solver.conf_budget(100000)
            status=solver.solve_limited(assumptions=assumptions)
            if status is not True:
                failures.append(dict(index=index,word=word,
                                     status='UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                                     core=solver.get_core() if status is False else None))
                print(json.dumps(failures[-1]),flush=True)
                break
            model=set(solver.get_model())
            coloring=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(509))
            assert coloring[0]=='0'
            assert all(int(coloring[v])==c+1 for v,c in zip(ports,word))
            assert all(coloring[a]!=coloring[b] for a,b in edges)
            models.append(coloring)
            if (index+1)%1000==0:
                print(f'{index+1}/{len(cases)} exact-positive models; {time.monotonic()-started:.1f}s',flush=True)
    return dict(status='ALL_BOUNDARY_PATTERNS_EXTEND' if len(models)==len(cases) else 'PARTIAL_SEARCH',
                core_file=core_path.name,center=0,ports=ports,port_edges=port_edges,
                k=5,expected_boundary_patterns=len(cases),models=models,
                failures=failures,negative_results_certified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--first',type=int,default=149)
    parser.add_argument('--second',type=int,default=397)
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--output',type=Path,default=Path('certificates/parts509_ports.json.gz'))
    args=parser.parse_args()
    result=run(Path('certificates/parts509_core.json'),args.first,args.second,args.limit)
    args.output.write_bytes(gzip.compress((json.dumps(result)+'\n').encode(),mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k!='models'},indent=2))
