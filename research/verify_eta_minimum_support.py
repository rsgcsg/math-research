"""Independent complete two-case RUP replay for the joined eta system.

The CNF is rebuilt from all actual Y edges and the exact observation domains.
Proof hints, solver libraries, and the native hint exporter are not imported.
"""
from collections import defaultdict, deque
from pathlib import Path
import argparse
import json
from audit_full_law_preparation import reconstruct
from eta_joined_cnf import build
from verify_anchored_eta import read, require, geometry_check
from verify_eta_joined_law import expand_compact, check as check_positive


def check_rup(initial, additions):
    """RUP-only: negate each claimed clause and perform ordinary propagation."""
    require(initial and additions, 'nonempty input and proof')
    maximum=max(abs(lit) for row in initial for lit in row)
    clauses=[];occ=defaultdict(list);units=[]
    def store(row):
        require(isinstance(row,list) and all(type(v) is int and 0<abs(v)<=maximum for v in row),
                'integer literals within the authenticated variable range')
        require(len(row)==len(set(row)) and all(-v not in row for v in row), 'clause structure')
        index=len(clauses);clauses.append(tuple(row))
        for lit in row:occ[lit].append(index)
        if len(row)==1:units.append(row[0])
    for row in initial:
        require(row, 'initial clauses must not be empty');store(row)
    def conflict(assumptions):
        value=[0]*(maximum+1)
        left=[len(c) for c in clauses];satisfied=bytearray(len(clauses))
        pending=deque(units+assumptions)
        while pending:
            lit=pending.popleft();v=abs(lit);sign=1 if lit>0 else -1
            if value[v]:
                if value[v]!=sign:return True
                continue
            value[v]=sign
            for index in occ[lit]:satisfied[index]=1
            for index in occ[-lit]:
                if satisfied[index]:continue
                left[index]-=1
                if left[index]==0:return True
                if left[index]==1:
                    candidate=next((x for x in clauses[index] if not value[abs(x)]),None)
                    require(candidate is not None, 'propagation bookkeeping')
                    pending.append(candidate)
        return False
    for index,row in enumerate(additions):
        require(isinstance(row,list) and all(type(v) is int and 0<abs(v)<=maximum for v in row),
                'proof literals')
        require(len(row)==len(set(row)) and all(-v not in row for v in row), 'proof clause')
        require(conflict([-v for v in row]), 'unproved RUP addition '+str(index))
        if not row:
            require(index==len(additions)-1, 'data after contradiction')
            return dict(status='VERIFIED_RUP_REFUTATION',initial_clauses=len(initial),
                        additions=len(additions),final_empty=True,solver_imports=False)
        store(row)
    raise ValueError('no final empty clause')


def replay_case(case, built):
    require(case['cnf_sha256']==built['cnf_sha256'], 'semantic CNF hash')
    require(type(case['full_clause_count']) is int and case['full_clause_count']==len(built['clauses']),
            'complete clause count')
    require(type(case['full_variable_count']) is int and case['full_variable_count']==built['nv'],
            'complete variable count')
    ids=case['initial_clause_ids']
    require(isinstance(ids,list) and ids and all(type(i) is int and 1<=i<=len(built['clauses']) for i in ids)
            and ids==sorted(set(ids)), 'authenticated initial clause IDs')
    return check_rup([built['clauses'][i-1] for i in ids],case['rup_clauses'])


def verify(data, summary, positive, negative, geometry):
    geometry_check(geometry,data)
    law=expand_compact(positive,data,summary)
    result=check_positive(law,data,summary)
    require(negative['schema']=='eta-joined-minimum-support-v1', 'negative schema')
    require(negative['input_semantic_sha256']==summary['semantic_sha256'], 'negative geometry')
    require(negative['target']=='F union Gamma union complete eta', 'negative scope')
    cases=negative['cases']
    require(len(cases)==2 and [c['sigma'] for c in cases]==[[0,1],[1,0]]
            and all(type(x) is int for c in cases for x in c['sigma']), 'all two-state permutations')
    reports=[]
    for c in cases:
        built=build(data,law,c['sigma'])
        report=replay_case(c,built)
        reports.append(dict(sigma=c['sigma'],cnf_sha256=built['cnf_sha256'],
                            complete_variables=built['nv'],complete_clauses=len(built['clauses']),**report))
    return dict(status='PASS',positive=result,two_state_refutations=reports,
                minimum_partition_support=3,
                scope='Minimum three for S=F union Gamma union full eta. The arbitrary-weight reduction uses the written majority-atom lemma. This is not a full fifteen-domain law or HN bound.')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    argparse.ArgumentParser(description=__doc__).parse_args()
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    report=verify(data,summary,read(root/'certificates/eta_joined_three_compact.json.gz'),
                  read(root/'certificates/eta_joined_minimum_support.json.xz'),
                  read(root/'certificates/eta_gauge_geometry.json'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
