"""Exact four-port relations on parallelograms, with witness coverage first.

Equal midpoint pairs generate the finite geometric family. Existing complete
colorings cover many requests through intersections of witness-index bitsets.
Only uncovered proper partitions trigger SAT. A negative answer is provisional.
"""
import argparse
import gzip
import json
import time
from collections import defaultdict,Counter
from itertools import combinations
from pathlib import Path
from parts_core import clauses
from relations import color_partitions


def parallelograms(points):
    flat=[tuple(x for axis in p for x in axis) for p in points]
    buckets=defaultdict(list)
    for a,b in combinations(range(len(points)),2):
        buckets[tuple(x+y for x,y in zip(flat[a],flat[b]))].append((a,b))
    result=set()
    for pairs in buckets.values():
        for (a,b),(c,d) in combinations(pairs,2):
            assert len({a,b,c,d})==4
            # Degenerate collinear equal-midpoint quadruples retained explicitly.
            result.add(tuple(sorted((a,b,c,d))))
    return sorted(result)


def run(limit=10000):
    from pysat.solvers import Solver
    root=Path(__file__).resolve().parents[1]
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    n=509;edges=[tuple(e) for e in core['induced_edges']];edge_set=set(edges)
    base=json.loads(gzip.decompress((root/'certificates/parts509_triples.json.gz').read_bytes()))['models']
    local_pairs=list(combinations(range(4),2))
    patterns=list(color_partitions(4,[],5))
    assert len(patterns)==15
    models=[];equal=[[0]*n for _ in range(n)];all_bits=0
    # Build the initial equality masks by intersecting per-vertex color sets.
    color_masks=[[0]*5 for _ in range(n)]
    for index,word in enumerate(base):
        assert len(word)==n and all(word[a]!=word[b] for a,b in edges)
        for v,c in enumerate(word):
            color_masks[v][int(c)]|=1<<index
    for a,b in combinations(range(n),2):
        equal[a][b]=sum(color_masks[a][c]&color_masks[b][c] for c in range(5))
    models.extend(base);all_bits=(1<<len(models))-1
    def add_model(word):
        nonlocal all_bits
        bit=1<<len(models)
        for a,b in combinations(range(n),2):
            if word[a]==word[b]:
                equal[a][b]|=bit
        models.append(word);all_bits|=bit
    family=parallelograms(core['points'])
    print(f'Exact equal-midpoint quadruples: {len(family)}',flush=True)
    requests=[];failure=None;counts=Counter();start=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=clauses(n,edges,5)) as solver:
        for index,ports in enumerate(family):
            unit=[(ports[i],ports[j]) in edge_set for i,j in local_pairs]
            eq=[equal[ports[i]][ports[j]] for i,j in local_pairs]
            for pattern in patterns:
                same=[pattern[i]==pattern[j] for i,j in local_pairs]
                if any(a and b for a,b in zip(unit,same)):
                    continue
                candidates=all_bits
                for mask,positive in zip(eq,same):
                    candidates &= mask if positive else ~mask
                counts[max(pattern)+1]+=1
                if candidates:
                    continue
                if len(requests)>=limit:
                    failure=dict(status='REQUEST_LIMIT',ports=ports,pattern=pattern)
                    break
                assumptions=[5*v+c+1 for v,c in zip(ports,pattern)]
                solver.conf_budget(200000)
                status=solver.solve_limited(assumptions=assumptions)
                requests.append(dict(ports=ports,pattern=pattern,status='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'))
                if status is not True:
                    failure=requests[-1]
                    print(json.dumps(failure),flush=True)
                    break
                model=set(solver.get_model())
                word=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(n))
                assert all(word[a]!=word[b] for a,b in edges)
                assert all(int(word[v])==c for v,c in zip(ports,pattern))
                add_model(word)
                eq=[equal[ports[i]][ports[j]] for i,j in local_pairs]
            if failure:
                break
            if (index+1)%100000==0:
                print(f'{index+1} quadruples; {len(requests)} new SAT queries; {time.monotonic()-start:.1f}s',flush=True)
    return dict(status='ALL_EQUAL_MIDPOINT_FOUR_PORT_RELATIONS_FULL' if not failure else 'PARTIAL_SEARCH',
                family_size=len(family),processed_through=index,patterns_by_blocks=dict(counts),
                models=models,new_requests=requests,failure=failure,
                includes_collinear_quadruples=True,negative_results_certified=False)


if __name__=='__main__':
    args=argparse.ArgumentParser()
    args.add_argument('--limit',type=int,default=10000)
    args=args.parse_args()
    result=run(args.limit)
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/parts509_parallelograms.json.gz').write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k not in ('models','new_requests')},indent=2))
