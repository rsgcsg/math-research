"""Replay new evidence from independently reconstructed geometry, without solvers."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import subprocess
import sys
from audit_full_law_preparation import reconstruct
from test_event_pricing_encoding import checks as encoding_checks
from test_translated_rotation_contacts import check as support_checks
from verify_event_research import check as events_check, mutation_tests
from verify_event_pricing import rebuild, verify_query, bind_events
from verify_rank2_connectivity import check as connectivity_check
from verify_rank2_rotation import verify as verify_host, read
from rup_hint_export import export
from verify_rup_lrat import check as check_rup


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    cert=read(root/'certificates/shared_event_research.json.gz')
    boundary=read(root/'certificates/rank2_joint_boundary.json')
    event_report=events_check(cert,data,summary,boundary)
    event_report['mutation_rejections']=mutation_tests(cert,data,summary,boundary)
    tiny_instance=dict(n=4,k=2,edges=[[0,1],[1,2]],events=[
        dict(source=[0,2],target=[0,3],pattern=[0,0]),
        dict(source=[0,2],target=[1,3],pattern=[0,0])])
    rejected=[]
    tests={
        'negative-RAT-hint':lambda q:q.__setitem__('proof',['999 0 -1 0']),
        'wrong-verdict':lambda q:q.__setitem__('status','SAT'),
        'boolean-coefficient':lambda q:q.__setitem__('coefficients',[True,1]),
        'trailing-proof-data':lambda q:q['proof'].append('9999 0 1 0'),
    }
    for name,mutate in tests.items():
        q=deepcopy(cert['tiny_query']);mutate(q)
        try:verify_query(tiny_instance,q)
        except (AssertionError,ValueError,IndexError,KeyError):rejected.append(name)
        else:raise AssertionError('accepted '+name)
    for name,events in [
        ('noncanonical-pattern',[dict(source=[0,1],target=[1,2],pattern=[1,1])]),
        ('duplicate-domain-vertex',[dict(source=[0,0],target=[1,2],pattern=[0,0])]),
        ('boolean-partition-label',[dict(source=[0],target=[1],pattern=[False])]),
    ]:
        try:rebuild(4,[[0,1]],2,events,[1],0)
        except (AssertionError,ValueError,TypeError):rejected.append(name)
        else:raise AssertionError('accepted '+name)
    for name,initial,trace in [
        ('non-RUP-RAT-step',[[1,2]],['3 0']),
        ('SAT-is-not-UNSAT',[[1]],['0']),
        ('malformed-trace',[[1],[-1]],['1 0 0']),
    ]:
        try:export(initial,trace)
        except ValueError:rejected.append(name)
        else:raise AssertionError('accepted '+name)
    square=[[1,2],[-1,2],[1,-2],[-1,-2]]
    assert check_rup(square,export(square,['2 0','0']))['status']=='VERIFIED_RUP_REFUTATION'
    verified_host=verify_host(root,mutation_tests=False)
    path=root/'certificates/rank2_rotation_coloring.json.gz';host=read(path);raw=path.read_bytes()
    connectivity=read(root/'certificates/rank2_connectivity.json')
    connected=connectivity_check(host,connectivity,raw)
    cm={
        'missing-tree-edge':lambda c:c['tree_edges'].pop(),
        'wrong-host-digest':lambda c:c.__setitem__('host_certificate_sha256','0'*64),
        'wrong-walk-orientation':lambda c:c['loops'][0]['edges'].__setitem__(0,-c['loops'][0]['edges'][0]),
        'wrong-generator':lambda c:c['loops'][1].__setitem__('gain',[0,2,0]),
        'boolean-edge':lambda c:c['tree_edges'].__setitem__(0,True),
    }
    for name,mutate in cm.items():
        c=deepcopy(connectivity);mutate(c)
        try:connectivity_check(host,c,raw)
        except (AssertionError,ValueError,IndexError,KeyError):rejected.append(name)
        else:raise AssertionError('accepted '+name)
    for name in ['test_research_checkpoint.py','verify_event_research.py','verify_rank2_connectivity.py','test_event_pricing_encoding.py','test_translated_rotation_contacts.py','run_event_pricing.py']:
        # run_event_pricing parses required flags first: supply them to reach its guard.
        extra=['--cache','unused','--request','unused','--output','unused'] if name=='run_event_pricing.py' else []
        process=subprocess.run([sys.executable,'-O',str(root/'research'/name),*extra],capture_output=True,text=True,timeout=20)
        assert process.returncode!=0 and 'requires assertions' in process.stderr
        rejected.append(name+':optimized-mode')
    print(json.dumps(dict(status='PASS',event_evidence=event_report,connectivity=connected,
                         complete_host_rebuilt=verified_host['status'],
                         encoding_calibration=encoding_checks(),translated_support_calibration=support_checks(),
                         additional_rejections=sorted(rejected),
                         scope='New finite evidence, complete host/input reconstruction, and encoding calibration. T139 additionally uses the cited external theorem; no fifteen-domain solution or HN bound.'),indent=2))


if __name__=='__main__':main()
