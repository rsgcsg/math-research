"""Replay the infinite-host certificate, full-domain boundary, and rebuild.

All mathematical checks use the standard library. This command does not run
SAT. The fifteen-domain mismatch applies only to this saved coloring family.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from audit_full_law_preparation import reconstruct
from verify_rank2_rotation import read, verify, canonical


def partition(word, vertices):
    labels={};out=[]
    for i in vertices:
        c=word[i]
        out.append(labels.setdefault(c,len(labels)))
    return tuple(out)


def check_boundary(cert, inputs, summary, boundary):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    assert boundary['schema']=='rank2-joint-boundary-v1'
    assert boundary['input_semantic_sha256']==summary['semantic_sha256']
    assert canonical(cert['graph']['geometry'])==canonical(inputs['geometry'])
    graph=cert['graph'];word=list(map(int,cert['coloring']['word']));U=cert['coloring']['u']
    powers=[list(range(5)),U,[U[U[c]] for c in range(5)]]
    rid={p:i for i,p in enumerate(graph['representatives'])}
    full=[cert['coloring']['origin'] if t is None else powers[t[2]%3][word[rid[t[0]]]]
          for t in graph['coordinates']]
    assert len(full)==10077
    assert all(full[a]!=full[b] for a,b in inputs['edges'])
    assert len(boundary['motions'])==len(inputs['motions'])==15
    outcomes=[]
    for record,name,mapping in zip(boundary['motions'],inputs['motions'],inputs['mappings']):
        assert set(record)=={'motion','equal_partition','pair_witness'} and record['motion']==name
        equal=partition(full,[a for a,b in mapping])==partition(full,[b for a,b in mapping])
        assert type(record['equal_partition']) is bool and record['equal_partition']==equal
        if equal:assert record['pair_witness'] is None
        else:
            a,b,x,y=record['pair_witness']
            assert all(type(i) is int and 0<=i<len(full) for i in (a,b,x,y)) and a!=b
            forward=dict(mapping)
            assert forward[a]==x and forward[b]==y
            assert (full[a]==full[b]) != (full[x]==full[y])
        # Global u shifts (and all palette renamings) do not change a partition.
        for permutation in powers:
            shifted=[permutation[c] for c in full]
            assert partition(shifted,[a for a,b in mapping])==partition(full,[a for a,b in mapping])
            assert partition(shifted,[b for a,b in mapping])==partition(full,[b for a,b in mapping])
        outcomes.append(dict(motion=name,domain_size=len(mapping),equal_partition=equal,
                             pair_witness=record['pair_witness']))
    assert [r['motion'] for r in outcomes if r['equal_partition']]==['tau','eta','dyadic_u']
    return dict(status='PASS',motions=outcomes,source_edge_checks=len(inputs['edges']),
                full_joint_satisfied=False,scope='Saved infinite coloring and its global group/palette shifts only; not all proper colorings.')


def main():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    report=verify(root,mutation_tests=True)
    certificate=read(root/'certificates/rank2_rotation_coloring.json.gz')
    inputs,summary=reconstruct(root)
    boundary=read(root/'certificates/rank2_joint_boundary.json')
    report['joint_boundary']=check_boundary(certificate,inputs,summary,boundary)
    mutations={
        'wrong_input':lambda x:x.__setitem__('input_semantic_sha256','0'*64),
        'missing_motion':lambda x:x['motions'].pop(),
        'false_positive':lambda x:x['motions'][1].__setitem__('equal_partition',True),
        'false_negative':lambda x:x['motions'][0].__setitem__('equal_partition',False),
        'wrong_map':lambda x:x['motions'][1]['pair_witness'].__setitem__(2,-1),
        'boolean_truth':lambda x:x['motions'][0].__setitem__('equal_partition',1),
    }
    for name,mutate in mutations.items():
        changed=deepcopy(boundary);mutate(changed)
        try:check_boundary(certificate,inputs,summary,changed)
        except (AssertionError,KeyError,IndexError,ValueError):continue
        raise AssertionError('accepted boundary mutation: '+name)
    p=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=20)
    assert p.returncode and 'requires assertions' in p.stderr
    report['boundary_mutation_rejections']=sorted(mutations)+['optimized_mode']
    with tempfile.TemporaryDirectory() as d:
        out=Path(d)/'rebuild.json.gz'
        result=subprocess.run([sys.executable,str(root/'research/build_rank2_rotation.py'),'--output',str(out)],
                              capture_output=True,text=True,timeout=600)
        if result.returncode:raise RuntimeError(result.stdout+'\n'+result.stderr)
        assert out.read_bytes()==(root/'certificates/rank2_rotation_coloring.json.gz').read_bytes()
    report['producer_rebuild']='BYTE_IDENTICAL'
    report['certificate_sha256']=hashlib.sha256((root/'certificates/rank2_rotation_coloring.json.gz').read_bytes()).hexdigest()
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
