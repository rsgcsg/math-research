"""Independent E064 full two-port relation check; no search/SAT imports."""
from pathlib import Path
import hashlib
import json
from verify_quintic_joint_ports import verify as geometry_check


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/quintic_pair_completion.json').read_text())
    assert data['schema']==1 and data['experiment']=='E064'
    raw=(root/'certificates/joint_column_pricing.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['source_sha256']
    old=json.loads(raw)
    parent,points,edges,_,_=geometry_check(root,root/'certificates/quintic_joint_translations.json',geometry_context=True)
    assert data['geometry']==parent['geometry']
    n=len(points)
    words=old['initial_words']+[s['word'] for s in old['history'] if s['status']=='SAT']+old['result']['words']
    def check_word(w):
        assert isinstance(w,str) and len(w)==n and set(w)<=set('01234')
        assert all(w[i]!=w[j] for i,j in edges)
    for w in words:check_word(w)
    # Distinct full signatures certify an unequal-color witness for every pair.
    assert len({tuple(w[i] for w in words) for i in range(n)})==n
    coverage=[1<<i for i in range(n)]
    for i,j in edges:coverage[i]|=1<<j;coverage[j]|=1<<i
    def add_word(w):
        classes={c:sum(1<<i for i,x in enumerate(w) if x==c) for c in '01234'}
        for i,c in enumerate(w):coverage[i]|=classes[c]
    for w in words:add_word(w)
    full=(1<<n)-1;missing=[]
    for i in range(n):
        absent=(full^coverage[i])&~((1<<(i+1))-1)
        while absent:
            j=(absent&-absent).bit_length()-1;missing.append([i,j]);absent&=absent-1
    assert [q['pair'] for q in data['queries']]==missing
    assert len(missing)==14
    for q in data['queries']:
        assert q['status']=='SAT'
        w=q['word'];check_word(w);i,j=q['pair'];assert w[i]==w[j]
        add_word(w)
    assert all(mask==full for mask in coverage)
    joint=data['joint_same'];assert joint['status']=='SAT'
    check_word(joint['word'])
    assert all(joint['word'][i]==joint['word'][j] for i,j in missing)
    return dict(experiment='E064',geometry=parent['geometry'],old_words=len(words),
                repaired_pairs=len(missing),all_pairs=n*(n-1)//2,
                nonunit_equal_extensions=n*(n-1)//2-len(edges),
                simultaneous_14_equalities=True,
                scope='Every proper assignment on any two vertices extends to X; not simultaneous pair laws or HN bounds')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
