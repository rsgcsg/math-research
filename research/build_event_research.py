"""Search-only E111 construction; all saved mathematics needs separate replay."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import sys
from run_event_pricing import load, search


def build(root, data):
    from event_pricing_cnf import formula
    from verify_event_pricing import bind_events
    from pysat.solvers import Solver
    boundary=load(root/'certificates/rank2_joint_boundary.json')
    events=[[j,*r['pair_witness']] for j,r in enumerate(boundary['motions']) if r['pair_witness'] is not None]
    events += [[14,a,b,x,y] for (a,x),(b,y) in combinations(data['mappings'][14],2)]
    built=formula(len(data['points']),data['edges'],5,bind_events(events,data['mappings']),
                  [1]*len(events),len(events))
    for j,a,b,x,y in events:
        e=built['equality'][tuple(sorted((a,b)))];f=built['equality'][tuple(sorted((x,y)))]
        built['clauses'].extend([[-e,f],[e,-f]])
    with Solver(name='cadical195',bootstrap_with=built['clauses']) as solver:
        solver.set_phases([i*5+int(c)+1 for i,c in enumerate(data['words'][4])])
        solver.conf_budget(100000)
        answer=solver.solve_limited()
        if answer is not True:
            raise RuntimeError('positive search incomplete; no certificate is published')
        positives=set(x for x in solver.get_model() if x>0)
        choices=[[c for c in range(5) if i*5+c+1 in positives] for i in range(len(data['points']))]
        if any(len(v)!=1 for v in choices):raise ValueError('invalid solver model')
        word=''.join(str(v[0]) for v in choices);statistics=solver.accum_stats()
    tiny=dict(n=4,k=2,edges=[[0,1],[1,2]],events=[
        dict(source=[0,2],target=[0,3],pattern=[0,0]),
        dict(source=[0,2],target=[1,3],pattern=[0,0])])
    toy=search(tiny,[1,1],0,1000)
    edge_set={tuple(e) for e in data['edges']};motion=dict(data['mappings'][0])
    a,b=next((a,b) for a,b in data['edges'] if a in motion and b in motion
             and tuple(sorted((motion[a],motion[b]))) in edge_set)
    record=[0,a,b,motion[a],motion[b]]
    real=search(dict(n=len(data['points']),k=5,edges=data['edges'],events=[record[1:]]),[10**12],-1,1000)
    if any(x['status']!='VERIFIED_NO_WORD_AT_OR_BELOW_TARGET' for x in (toy,real)):
        raise RuntimeError('negative calibration not certified')
    return dict(schema='shared-event-research-v1',input_semantic_sha256=boundary['input_semantic_sha256'],
                positive_word=word,event_records=events,tiny_query=toy['query'],
                zero_gap_record=record,zero_gap_query=real['query'],
                search_statistics=dict(positive=statistics,tiny=toy['statistics'],zero_gap=real['statistics']),
                scope='E111 positive restricted-event witness, C024 negative calibration, and a nonnegative-only Y pricing calibration; no full fifteen-domain law or HN bound.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=build(root,load(args.cache))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps(dict(status='GENERATED_FOR_INDEPENDENT_CHECK',events=len(result['event_records']))))


if __name__=='__main__':main()
