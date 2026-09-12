"""Independent E079 proper word and complete maximal-domain checker."""
from fractions import Fraction as Q
from pathlib import Path
import json
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice,digest


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/quintic_free_tau_joint.json').read_text())
    assert data['experiment']=='E079'
    parent,c=geometry(root,geometry_context=True)
    assert data['geometry']==parent['geometry']
    result=data['result'];word=result['word']
    assert len(word)==len(c['points']) and set(word)<=set('01234')
    assert all(word[u]!=word[v] for u,v in c['edges'])
    r=c['ring'];mul=r['mul'];points=c['points'];lookup={p:i for i,p in enumerate(points)}
    one=(Q(1),)+(Q(0),)*31;zero=(Q(0),)*32;eta=zero[:16]+one[:16]
    z=r['blocks'][0][64]
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    omega=tuple(-2*x-3*y for x,y in zip(one,z))
    shift=tuple(x+y for x,y in zip(one,mul(eta,z)))
    definitions=[('tau',r['tau'],zero,False),('nu',nu,zero,False),('eta',eta,zero,False),
                 ('omega',omega,zero,False),('bar',one,zero,True),
                 ('bridge',tuple(-a for a in eta),shift,False),
                 ('translation_one',one,one,False),('translation_z',one,z,False)]
    power=one
    for j in range(1,5):
        power=mul(power,eta)
        definitions.append((f'one_plus_eta_{j}',one,tuple(x+y for x,y in zip(one,power)),False))
    definitions.append(('bridge_shift',one,shift,False))
    size=len(result['motions']);assert 5<=size<=13
    assert result['motions']==[d[0] for d in definitions[:size]]
    assert len(result['permutations'])==len(result['mapping_sha256'])==size
    maps={};counts=[]
    for idx,(name,a,t,reflection) in enumerate(definitions[:size]):
        m=[]
        for i,p in enumerate(points):
            source=tuple(Q(x)/2 for x in conjugate_twice(p)) if reflection else p
            target=tuple(x+y for x,y in zip(mul(a,source),t))
            if target in lookup:m.append((i,lookup[target]))
        assert digest(m)==result['mapping_sha256'][idx]
        pi=result['permutations'][idx];assert sorted(pi)==list(range(5))
        assert all(pi[int(word[i])]==int(word[j]) for i,j in m)
        maps[name]=set(m);counts.append(dict(motion=name,domain=len(m)))
    # Explicitly check retained E065 obligations on the same physical old X,
    # rather than infer them from map names or from solver stages.
    old=json.loads((root/'certificates/quintic_full_translation_laws.json').read_text())
    oldids=[lookup[p] for p in r['points']];retained=[]
    for m in old['motions']:
        name='bar' if m['name']=='conjugate' else m['name']
        if name in maps:
            assert all((oldids[i],oldids[j]) in maps[name] for i,j in m['mapping'])
            retained.append(m['name'])
    events=json.loads((root/'certificates/joint_column_pricing.json').read_text())['events']
    retained_events=0
    for event in events:
        name=event['motion'] if event['translation'] is None else event['translation_label']
        name='bar' if name=='conjugate' else name
        if name in maps:
            assert all((oldids[i],oldids[j]) in maps[name] for i,j in event['pairs'])
            retained_events+=1
    return dict(status='PASS',experiment='E079',geometry=parent['geometry'],full_domains=counts,
                retained_E065_maps=retained,retained_E063_quartets=retained_events,
                scope='One S5-averaged free proper word for the listed complete domains; not all old infinite integral-motion obligations or HN')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
