"""E102 independent BFS and direct word verification for one S3 cover.

This is a single specified 15-word operator family, NOT all S3 covers. The
negative claim is derived from old-constraint unit propagation and a physical
pair event, independently of the search solver's UNSAT response.
"""
from array import array
from collections import Counter, deque
from itertools import combinations
from pathlib import Path
import copy
import json
from verify_joint_nilpotent_cover import prepare
from verify_quintic_core_probe import digest


def actions(old, signs, shifts):
    assert len(signs)==14 and set(signs)<={-1,1}
    assert len(shifts)==14 and all(len(row)==5 and all(type(x) is int and 0<=x<3 for x in row) for row in shifts)
    sigmas=[];palettes=[]
    for j in range(14):
        sigma=[3*old['word_permutations'][j][a]+(signs[j]*s+shifts[j][a])%3
               for a in range(5) for s in range(3)]
        assert sorted(sigma)==list(range(15));sigmas.append(sigma)
        palettes.append([old['color_permutations'][j][a][:] for a in range(5) for s in range(3)])
    return sigmas,palettes


def analyze(prepared, signs, shifts):
    n=len(prepared['context']['points']);sigma,pi=actions(prepared['old'],signs,shifts)
    adjacency=[[] for _ in range(n*75)]
    for j,mapping in enumerate(prepared['maps'][:14]):
        for a in range(15):
            b=sigma[j][a];palette=pi[j][a]
            for p,q in mapping:
                for color in range(5):
                    x=(a*n+p)*5+color;y=(b*n+q)*5+palette[color]
                    adjacency[x].append(y);adjacency[y].append(x)
    classes=array('I',[0])*(n*75);count=0
    for start in range(len(classes)):
        if classes[start]:continue
        count+=1;classes[start]=count;queue=deque([start])
        while queue:
            x=queue.popleft()
            for y in adjacency[x]:
                if not classes[y]:classes[y]=count;queue.append(y)
    del adjacency
    clauses=set()
    color=lambda a,p,c:classes[(a*n+p)*5+c]
    for a in range(15):
        for p in range(n):
            ids=[color(a,p,c) for c in range(5)];clauses.add(tuple(sorted(set(ids))))
            for x,y in combinations(ids,2):clauses.add(tuple(sorted({-x,-y})))
        for p,q in prepared['context']['edges']:
            for c in range(5):clauses.add(tuple(sorted({-color(a,p,c),-color(a,q,c)})))
    clauses=sorted(clauses);values={};trace=[];changed=True
    while changed:
        changed=False
        for idx,clause in enumerate(clauses):
            if any(values.get(abs(x))==(x>0) for x in clause):continue
            unset=[x for x in clause if abs(x) not in values]
            assert unset
            if len(unset)==1:
                x=unset[0];values[abs(x)]=x>0;trace.append([x,idx]);changed=True
    forced=[]
    for a in range(15):
        assert all(color(a,5557,c)==color(a,238,c) for c in range(5))
        allowed=[{c for c in range(5) if values.get(color(a,p,c)) is not False} for p in [233,239]]
        assert all(allowed)
        if allowed[0].isdisjoint(allowed[1]):forced.append(a)
    assert len(forced)==8
    # Base-word tree gauge turns eta's four chosen edges into identity.
    # tau and bar then act on each three-element fiber as a cycle and a
    # reflection, generating the full six-element symmetric group.
    assert all(x==0 for x in shifts[2]) and signs[2]==1
    perm1=tuple((s+shifts[0][0])%3 for s in range(3))
    perm2=tuple((signs[4]*s+shifts[4][0])%3 for s in range(3))
    monodromy={(0,1,2)};queue=deque(monodromy)
    while queue:
        p=queue.popleft()
        for q in [perm1,perm2]:
            r=tuple(q[p[i]] for i in range(3))
            if r not in monodromy:monodromy.add(r);queue.append(r)
    assert len(monodromy)==6
    summary=dict(classes=count,base_clauses=len(clauses),
                 classes_sha256=digest(list(classes)),formula_sha256=digest(clauses),
                 forced_variables=len(values),unit_trace=trace,
                 source_unequal_forced_atoms=forced,image_unequal_count=0,
                 denominator=15,monodromy_order=6)
    return summary,sigma,pi


def check_positive(data,prepared,summary,sigma,pi):
    assert data['schema']=='joint-s3-cover-v1' and data['experiment']=='E102'
    assert data['source_sha256']==prepared['source_sha256']
    assert data['geometry']==prepared['report']['geometry'] and data['analysis']==summary
    words=data['words'];n=len(prepared['context']['points'])
    assert len(words)==15 and all(isinstance(w,str) and len(w)==n and set(w)<=set('01234') for w in words)
    assert all(w[p]!=w[q] for w in words for p,q in prepared['context']['edges'])
    pattern=lambda w,indices: _pattern(w,indices)
    for j,mapping in enumerate(prepared['maps'][:14]):
        assert all(int(words[sigma[j][a]][q])==pi[j][a][int(words[a][p])]
                   for a in range(15) for p,q in mapping)
        left=Counter(pattern(w,[p for p,q in mapping]) for w in words)
        right=Counter(pattern(w,[q for p,q in mapping]) for w in words)
        assert left==right
    assert len({pattern(w,range(n)) for w in words})==15
    assert words[0][31]!='1'  # genuinely leaves the old fixed-operator truth pattern
    counts=[sum(w[p]!=w[q] for w in words) for p,q in [(233,239),(5557,238)]]
    assert counts==data['positive_event_counts']==[12,0]
    return dict(status='PASS',experiment='E102',vertices=n,edges=len(prepared['context']['edges']),
                words=15,distinct_partitions=15,full_old_domains=14,
                checked_word_edges=15*len(prepared['context']['edges']),
                positive_event_counts=counts,analysis=summary,
                scope='Specified affine F3/S3 cover only: positive old14, but every proper word selection has source unequal mass >=8/15 and image mass 0. Not all S3 covers or full-joint.')


def _pattern(word,indices):
    labels={};return tuple(labels.setdefault(word[i],len(labels)) for i in indices)


def verify(root,mutations=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    root=Path(root);data=json.loads((root/'certificates/joint_s3_cover.json').read_text())
    prepared=prepare(root);summary,sigma,pi=analyze(prepared,data['signs'],data['shifts'])
    report=check_positive(data,prepared,summary,sigma,pi)
    if mutations:
        cases=[]
        bad=copy.deepcopy(data);bad['source_sha256']='0'*64;cases.append(('source',bad))
        bad=copy.deepcopy(data);bad['analysis']['source_unequal_forced_atoms']=[];cases.append(('negative_event',bad))
        bad=copy.deepcopy(data);bad['analysis']['unit_trace']=[];cases.append(('unit_derivation',bad))
        bad=copy.deepcopy(data);w=list(bad['words'][0]);p,q=prepared['context']['edges'][0];w[q]=w[p];bad['words'][0]=''.join(w);cases.append(('word_edge',bad))
        bad=copy.deepcopy(data);bad['words']=bad['words'][:-1];cases.append(('missing_word',bad))
        bad=copy.deepcopy(data);bad['positive_event_counts']=[0,0];cases.append(('positive_event',bad))
        rejected=[]
        for name,bad in cases:
            try:check_positive(bad,prepared,summary,sigma,pi)
            except (AssertionError,KeyError,IndexError,ValueError):rejected.append(name)
            else:raise AssertionError('Accepted mutation: '+name)
        report['mutations_rejected']=rejected
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--mutations',action='store_true');args=p.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],args.mutations),indent=2))
