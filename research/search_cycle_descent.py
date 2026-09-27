"""Search for a full-Y zero word for E111 plus a transported five-point family.

Search only (requires python-sat). A SAT word is verified by the separate
standard-library cycle-descent checker. UNSAT of this singleton request is not
UNSAT for arbitrary-support common laws, and no such negative inference is made.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
from itertools import combinations
from event_pricing_cnf import formula, dimacs
from verify_motion_packet import read
from verify_event_pricing import partition_value, check_word


def search(data, template, inherited, conflicts, mode='full'):
    from pysat.solvers import Solver
    if type(conflicts) is not int or conflicts<=0 or mode not in ('full','avoid'):
        raise ValueError('search parameters')
    root=template['core']['Y_indices'];tuples=template['transport']['tuples_in_Y']
    events=[dict(source=rec[1:3],target=rec[3:5],pattern=[0,0])
            for rec in inherited['event_records']]
    old_count=len(events)
    if mode=='full':
        events += [dict(source=[root[a],root[b]],target=[row[a],row[b]],pattern=[0,0])
                   for row in tuples for a,b in combinations(range(5),2)]
    else:
        events += [dict(source=row,target=row,pattern=p) for row in tuples
                   for p in template['core']['patterns']]
    built=formula(len(data['points']),data['edges'],5,events,[0]*len(events),0)
    clauses=built['clauses']; selectors=built['partitions']
    for i,event in enumerate(events):
        a=selectors[tuple(event['source']),tuple(event['pattern'])]
        b=selectors[tuple(event['target']),tuple(event['pattern'])]
        if mode=='avoid' and i>=old_count:clauses.append([-a])
        else:clauses.extend([[-a,b],[a,-b]])
    start=time.monotonic()
    with Solver(name='g3',bootstrap_with=clauses) as solver:
        # Decision phases are only a heuristic, not clauses fixing a background.
        solver.set_phases([5*i+int(c)+1 for i,c in enumerate(inherited['positive_word'])])
        solver.conf_budget(conflicts);answer=solver.solve_limited()
        statistics=solver.accum_stats();model=solver.get_model() if answer else None
    out=dict(schema='cycle-descent-search-v1',mode=mode,
             status='SAT_WITNESS' if answer else ('UNSAT_FIXED_SINGLETON_UNCERTIFIED' if answer is False else 'UNKNOWN_FIXED_SINGLETON'),
             conflict_budget=conflicts,statistics=statistics,
             elapsed_seconds=time.monotonic()-start,variables=built['nv'],clauses=len(clauses),
             cnf_sha256=hashlib.sha256(dimacs(built['nv'],clauses)).hexdigest(),
             scope='Search result, not its own independent certificate; no arbitrary-law negative claim.')
    if model:
        positive=set(model);word=''.join(str(next(c for c in range(5) if 5*i+c+1 in positive))
                                       for i in range(len(data['points'])))
        check_word(word,len(data['points']),5,data['edges'])
        for i,event in enumerate(events):
            a=partition_value(word,event['source'],event['pattern'])
            b=partition_value(word,event['target'],event['pattern'])
            if mode=='avoid' and i>=old_count:
                if a:raise ValueError('solver word violates avoidance')
            elif a!=b:raise ValueError('solver word violates partition equality')
        out['word']=word
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--conflicts',type=int,default=30000)
    parser.add_argument('--mode',choices=('full','avoid'),default='full')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    data=read(args.cache);template=read(root/'certificates/original_Y_cycle_descent.json')
    raw=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    if hashlib.sha256(raw).hexdigest()!=template['input_semantic_sha256']:
        raise ValueError('cache is not the bound actual-Y input')
    inherited=read(root/'certificates/shared_event_research.json.gz')
    result=search(data,template,inherited,args.conflicts,args.mode)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='word'},indent=2))


if __name__=='__main__':main()
