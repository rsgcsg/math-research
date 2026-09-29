"""Independent solver-free replay of complete full15 three-atom cases.

The mathematical encoding and weighted gauge are proved in the companion
documents; the RUP proof checker neither imports nor trusts the producer.
"""
from pathlib import Path
import argparse
import json
from audit_full_law_preparation import reconstruct
from full15_support_semantics import reconstruct_case
from verify_anchored_eta import read, require, geometry_check
from verify_eta_minimum_support import check_rup


def case_identity(c,summary):
    require(c['schema']=='full15-three-atom-search-v1','schema')
    require(c['input_semantic_sha256']==summary['semantic_sha256'],'exact input')
    require(c['status']=='VERIFIED_RESTRICTED_UNSAT','certification status')
    require(type(c['weighted']) is bool and type(c['case']) is int
            and c['case'] in range(3),'case identity')


def replay_reconstruction(c,built):
    require(c['cnf_sha256']==built['cnf_sha256'],'semantic CNF hash')
    require(type(c['full_clause_count']) is int and c['full_clause_count']==built['full_clause_count'],
            'full clause count')
    require(type(c['full_variable_count']) is int and c['full_variable_count']==built['nv'],
            'full variable count')
    checked=check_rup(built['initial_clauses'],c['rup_clauses'])
    return dict(weighted=c['weighted'],case=c['case'],cnf_sha256=built['cnf_sha256'],
                full_variables=built['nv'],full_clauses=built['full_clause_count'],
                selected_motion_clauses=built['selected_motion_clauses'],**checked)


def verify_case(c,data,summary):
    case_identity(c,summary)
    built=reconstruct_case(data,c['weighted'],c['case'],c['initial_clause_ids'])
    return replay_reconstruction(c,built)


def main():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('certificates',type=Path,nargs='*')
    args=p.parse_args();root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    geometry_check(read(root/'certificates/eta_gauge_geometry.json'),data)
    paths=args.certificates or [root/'certificates'/f'full15_three_{kind}{i}.json.xz'
                               for kind in ('equal','weighted') for i in range(3)]
    cases=[read(path) for path in paths]
    keys=[(c['weighted'],c['case']) for c in cases]
    require(len(keys)==len(set(keys)),'duplicate case')
    reports=[]
    for c in cases:
        report=verify_case(c,data,summary);reports.append(report)
        print(json.dumps(report,sort_keys=True),flush=True)
    complete=set(keys)=={(w,i) for w in (False,True) for i in range(3)}
    print(json.dumps(dict(status='PASS',complete_six_cases=complete,
                         scope='No full15 law on three atoms' if complete else
                         'Only the individually listed restricted cases; not a complete exclusion',
                         hn_bound_changed=False)),flush=True)


if __name__=='__main__':main()
