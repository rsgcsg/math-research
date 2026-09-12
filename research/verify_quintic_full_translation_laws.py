"""Independent E065 geometry, maximal domains and positive partition law."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
from verify_quintic_joint_ports import verify as parent_geometry
from verify_quintic_core_probe import multiplication_twice,product_twice


def verify(root,certificate=None,geometry_context=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/quintic_full_translation_laws.json').read_text())
    assert data['schema']==1 and data['experiment']=='E065'
    raw=(root/'certificates/quintic_joint_translations.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['parent_sha256']
    assert hashlib.sha256((root/'certificates/joint_column_pricing.json').read_bytes()).hexdigest()==data['event_source_sha256']
    parent,pts,edges,base,_=parent_geometry(root,root/'certificates/quintic_joint_translations.json',geometry_context=True)
    assert data['geometry']==parent['geometry']
    old=json.loads(raw);den=old['denominator'];motions=data['motions']
    assert len(motions)==10 and motions[:5]==old['motions']
    table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16];power=one
    expected=[]
    for j in range(1,5):
        power=mul(power,eta);expected.append((f'one_plus_eta_{j}',tuple(x+y for x,y in zip(one,power))))
    z=tuple(Q(x,den) for x in pts[base[64]])
    expected.append(('bridge_shift',tuple(x+y for x,y in zip(one,mul(eta,z)))))
    lookup={p:i for i,p in enumerate(pts)}
    for m,(name,t) in zip(motions[5:],expected):
        assert m['name']==name and all((x*den).denominator==1 for x in t)
        shift=tuple(int(x*den) for x in t);assert tuple(m['translation'])==shift
        mapping=[]
        for i,p in enumerate(pts):
            q=tuple(x+y for x,y in zip(p,shift))
            if q in lookup:mapping.append([i,lookup[q]])
        assert mapping==m['mapping']
    result=data['result'];assert result['status']=='SAT'
    word=result['word'];assert len(word)==len(pts) and set(word)<=set('01234')
    assert all(word[i]!=word[j] for i,j in edges)
    perms=result['permutations'];assert len(perms)==10
    for m,pi in zip(motions,perms):
        assert sorted(pi)==list(range(5))
        assert all(pi[int(word[i])]==int(word[j]) for i,j in m['mapping'])
    # Explicitly retain all 18 earlier quartet obligations, not only their count.
    events=json.loads((root/'certificates/joint_column_pricing.json').read_text())['events']
    maps={m['name']:set(map(tuple,m['mapping'])) for m in motions}
    def pattern(ids):
        labels={};return tuple(labels.setdefault(word[i],len(labels)) for i in ids)
    for e in events:
        name=e['motion'] if e['translation'] is None else e['translation_label']
        assert all(tuple(p) in maps[name] for p in e['pairs'])
        assert pattern([i for i,j in e['pairs']])==pattern([j for i,j in e['pairs']])
    report=dict(experiment='E065',geometry=parent['geometry'],maximal_domains=[len(m['mapping']) for m in motions],
                full_maximal_partition_laws=10,retained_quartets=len(events),
                scope='One S5-averaged proper word; selected ten maps and internal common words only, not all congruences or HN')
    if geometry_context:return report,pts,edges,base
    return report


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
