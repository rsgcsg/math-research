"""Independent E111 replay: exact geometry, positive word, and two RUP calibrations.

No SAT solver, LP, producer or hint exporter is imported. The actual four-point
C024 geometry is independently reconstructed rather than trusted as a toy graph.
"""
from copy import deepcopy
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path
from audit_full_law_preparation import reconstruct
from verify_event_pricing import bind_events, check_word, partition_value, score, verify_query
from verify_joint_two_motion_counterexample import verify as verify_c024


def shape(word,indices):
    return tuple(sorted(tuple(p for p,i in enumerate(indices) if word[i]==c) for c in set(word[i] for i in indices)))


def check(cert,data,summary,boundary):
    if not __debug__:raise RuntimeError('verification requires assertions')
    assert cert['schema']=='shared-event-research-v1'
    assert cert['input_semantic_sha256']==summary['semantic_sha256']==boundary['input_semantic_sha256']
    expected=[[j,*row['pair_witness']] for j,row in enumerate(boundary['motions']) if row['pair_witness'] is not None]
    assert len(expected)==12
    expected += [[14,a,b,x,y] for (a,x),(b,y) in combinations(data['mappings'][14],2)]
    assert cert['event_records']==expected and len(expected)==418
    events=bind_events(cert['event_records'],data['mappings']);word=cert['positive_word'];n=len(data['points'])
    check_word(word,n,5,data['edges'])
    assert all(score(word,[e],[1])==0 for e in events)
    seed=data['words'][4];small=events[:12]+[[233,239,5557,238]]
    assert all(score(seed,[e],[1])==0 for e in small)
    motions=[]
    for name,mapping in zip(data['motions'],data['mappings']):
        same=shape(word,[a for a,b in mapping])==shape(word,[b for a,b in mapping])
        motions.append(dict(motion=name,domain=len(mapping),full_partition_equal=same))
    assert [m['motion'] for m in motions if m['full_partition_equal']]==['dyadic_u']
    # C024 geometry and its two actual motions, rebuilt independently.
    tiny=verify_c024();maps=tiny['maximal_domains']
    requests=[dict(motion=j,source=[0,2],pattern=[0,0]) for j in (0,1)]
    tiny_events=bind_events(requests,maps)
    q=cert['tiny_query'];assert q['coefficients']==[1,1] and q['target']==0
    tiny_report=verify_query(dict(n=4,k=2,edges=tiny['unit_edges'],events=tiny_events),q)
    assert tiny_report['strictly_positive_on_all_words']
    rec=cert['zero_gap_record'];assert rec==[0,31,193,6269,2135]
    real_events=bind_events([rec],data['mappings'])
    edge_set={tuple(e) for e in data['edges']}
    assert tuple(sorted(rec[1:3])) in edge_set and tuple(sorted(rec[3:5])) in edge_set
    q=cert['zero_gap_query'];assert q['coefficients']==[10**12] and q['target']==-1
    real_report=verify_query(dict(n=n,k=5,edges=data['edges'],events=real_events),q)
    assert real_report['lower_bound']==0 and not real_report['strictly_positive_on_all_words']
    return dict(status='PASS',input_semantic_sha256=summary['semantic_sha256'],
                positive_word_sha256=hashlib.sha256(word.encode()).hexdigest(),
                full_graph_edge_checks=len(data['edges']),pair_event_checks=len(events),
                old_seed_thirteen_event_checks=len(small),motions=motions,
                tiny_strict_gap_calibration=tiny_report,real_nonnegative_only_calibration=real_report,
                full_fifteen_domain_law=False,all_word_strict_obstruction=False,
                scope='All u-domain partitions and twelve specified pair events are simultaneously satisfied by one free word; the other fourteen full domains fail.')


def mutation_tests(cert,data,summary,boundary):
    mutations={
        'geometry-binding':lambda c:c.__setitem__('input_semantic_sha256','0'*64),
        'all-one-color':lambda c:c.__setitem__('positive_word','0'*len(c['positive_word'])),
        'missing-event':lambda c:c['event_records'].pop(),
        'wrong-motion-image':lambda c:c['event_records'][0].__setitem__(3,-1),
        'boolean-motion-index':lambda c:c['event_records'][0].__setitem__(0,True),
        'tiny-no-proof':lambda c:c['tiny_query'].__setitem__('proof',[]),
        'tiny-wrong-hint':lambda c:c['tiny_query'].__setitem__('proof',['999 0 999 0']),
        'tiny-cnfh':lambda c:c['tiny_query'].__setitem__('cnf_sha256','0'*64),
        'tiny-objective':lambda c:c['tiny_query'].__setitem__('coefficients',[2,1]),
        'Y-false-positive-gap':lambda c:c['zero_gap_query'].__setitem__('target',0),
        'Y-truncated-proof':lambda c:c['zero_gap_query']['proof'].pop(),
        'Y-incorrect-event':lambda c:c['zero_gap_record'].__setitem__(4,0),
    }
    for name,mutate in mutations.items():
        changed=deepcopy(cert);mutate(changed)
        try:check(changed,data,summary,boundary)
        except (AssertionError,ValueError,IndexError,KeyError,TypeError):continue
        raise AssertionError('accepted invalid certificate '+name)
    return sorted(mutations)


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    cert=json.loads(gzip.decompress((root/'certificates/shared_event_research.json.gz').read_bytes()))
    boundary=json.loads((root/'certificates/rank2_joint_boundary.json').read_text())
    result=check(cert,data,summary,boundary)
    result['mutation_rejections']=mutation_tests(cert,data,summary,boundary)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
