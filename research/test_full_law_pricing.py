"""E105 independent replay, mutation rejection, and finite CNF calibration.

Optional search libraries are not required. The producer is imported ONLY for
encoding calibration, never by the independent mathematical evidence checker.
"""
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
from audit_full_law_preparation import reconstruct,unique_keys
from verify_full_law_pricing import check_data
from full_law_pricing import PatternCNF,shape


def encoding_tests():
    tests=0
    for n,k in ((0,2),(1,2),(2,2),(3,3),(4,3)):
        patterns=sorted(set(shape(w) for w in product(range(k),repeat=n)))
        enc=PatternCNF(n,[],k)
        events=[enc.event(list(range(n)),p) for p in patterns]
        for word in product(range(k),repeat=n):
            assignment={enc.color(i,c):c==word[i] for i in range(n) for c in range(k)}
            for (i,j),e in enc.eq.items(): assignment[e]=word[i]==word[j]
            for (_,pat),e in enc.events.items(): assignment[e]=shape(word)==pat
            satisfied=lambda clause:any(assignment[abs(lit)]==(lit>0) for lit in clause)
            assert all(satisfied(clause) for clause in enc.clauses)
            for e in list(enc.eq.values())+events:
                assignment[e]=not assignment[e]
                assert not all(satisfied(clause) for clause in enc.clauses)
                assignment[e]=not assignment[e];tests+=1
    # A->B and C->A balance the old A row but not the new B,C rows.
    assert Fraction(1,2)*1+Fraction(1,2)*(-1)==0
    assert Fraction(1,2)*(-1)!=0 and Fraction(1,2)*1!=0
    return dict(auxiliary_flip_checks=tests,omitted_new_row_counterexample=True)


def main():
    if not __debug__: raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    raw=(root/'certificates/full_law_pricing.json.gz').read_bytes()
    cert=json.loads(gzip.decompress(raw),object_pairs_hook=unique_keys)
    data,summary=reconstruct(root);result=check_data(cert,data,summary)
    def first(d):return d['runs'][0]['history'][0]
    mutations={
        'base':lambda d:d.__setitem__('base_commit','0'*40),
        'input-binding':lambda d:d.__setitem__('input_semantic_sha256','0'*64),
        'geometry':lambda d:d['geometry'].__setitem__('induced_edges',0),
        'missing-motion':lambda d:d['motions'].pop(),
        'improper-word':lambda d:d['runs'][0]['words'].__setitem__(5,'0'*10077),
        'false-cut':lambda d:first(d)['potential'][0].__setitem__(3,0),
        'false-price':lambda d:first(d).__setitem__('price',1),
        'future-word':lambda d:first(d)['potential'][0].__setitem__(1,500),
        'dropped-rows':lambda d:first(d).__setitem__('new_row_count',0),
        'wrong-index':lambda d:first(d).__setitem__('new_word_index',6),
        'boolean-margin':lambda d:first(d).__setitem__('pool_strict_margin',True),
        'fake-global-unsat':lambda d:d['runs'][0].__setitem__('status','UNSAT'),
        'fake-full-law':lambda d:d['runs'][0].__setitem__('full_law',['1']),
        'hidden-reuse':lambda d:d['runs'][2]['history'][0]['queries'][0].__setitem__('restricted_to_reused_patterns',False),
        'toy-gap':lambda d:d['counterexample'].__setitem__('uniform_strict_gap',0),
        'final-pool-cut':lambda d:d['runs'][0]['final_pool_values'].__setitem__(0,0),
    }
    rejected=[]
    for name,mutate in mutations.items():
        changed=deepcopy(cert);mutate(changed)
        try:check_data(changed,data,summary)
        except (ValueError,AssertionError):rejected.append(name)
        else:raise AssertionError('mutation accepted: '+name)
    for filename in ('verify_full_law_pricing.py','verify_joint_two_motion_counterexample.py','test_full_law_pricing.py'):
        p=subprocess.run([sys.executable,'-O',str(root/'research'/filename)],capture_output=True,text=True,timeout=20)
        assert p.returncode and 'requires assertions' in p.stderr
    result.update(certificate_sha256=hashlib.sha256(raw).hexdigest(),mutations_rejected=rejected,
                  optimized_mode_rejections=3,encoding=encoding_tests())
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
