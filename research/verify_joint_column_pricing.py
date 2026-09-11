"""Independent E063 geometry, separation countercolumns and rational law check.

No LP, SAT or producer imports. A search UNKNOWN remains explicitly UNKNOWN.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import hashlib
import json
from verify_quintic_joint_ports import verify as parent_geometry
from verify_quintic_core_probe import multiplication_twice,product_twice


def pat(w,ids):
    blocks={};return tuple(blocks.setdefault(w[i],len(blocks)) for i in ids)


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/joint_column_pricing.json').read_text())
    assert data['schema']==1 and data['experiment']=='E063'
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert data['core_sha256']==hashlib.sha256(raw).hexdigest()
    parent,points,edges,base,copies=parent_geometry(root,root/'certificates/quintic_joint_translations.json',geometry_context=True)
    assert data['geometry']==parent['geometry']
    old=json.loads((root/'certificates/quintic_joint_ports.json').read_text())
    old_maps={m['name']:m['mapping'] for m in old['motions']}
    den=old['denominator'];table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16];power=one
    shifts={}
    for j in range(1,5):
        power=mul(power,eta);shifts[f'one_plus_eta_{j}']=tuple(int((x+y)*den) for x,y in zip(one,power))
    zz=mul(eta,tuple(Q(x,den) for x in points[base[64]]))
    shifts['bridge_shift']=tuple(int((x+y)*den) for x,y in zip(one,zz))
    events=data['events'];assert len(events)==18
    labels={label:0 for label in shifts}
    for index,event in enumerate(events):
        pairs=event['pairs'];assert len(pairs)==4
        left,right=zip(*pairs)
        assert len(set(left))==len(set(right))==4
        assert all(0<=v<len(points) for v in left+right)
        assert not any(set(left)<=b or set(right)<=b for b in copies)
        if event['translation'] is None:
            assert index<3 and event['motion']==old['motions'][index]['name']
            assert pairs==old['motions'][index]['mixed_witness']
            assert all(pair in old_maps[event['motion']] for pair in pairs)
        else:
            label=event['translation_label'];assert tuple(event['translation'])==shifts[label]
            labels[label]+=1
            assert all(tuple(y-x for x,y in zip(points[i],points[j]))==shifts[label] for i,j in pairs)
    assert all(n==3 for n in labels.values())
    patterns=sorted({pat(w,range(4)) for w in product(range(4),repeat=4)})
    assert len(patterns)==15
    def col(w):
        assert len(w)==len(points) and set(w)<=set('01234')
        assert all(w[i]!=w[j] for i,j in edges)
        out=[]
        for e in events:
            left,right=zip(*e['pairs']);a,b=pat(w,left),pat(w,right)
            out += [int(a==p)-int(b==p) for p in patterns]
        return out
    words=data['initial_words'];assert len(words)==len(set(words))==5
    e062=json.loads((root/'certificates/quintic_joint_translations.json').read_text())
    assert words==list(dict.fromkeys(s['word'] for s in e062['stages']))
    columns=[col(w) for w in words]
    # All fifteen new quartets genuinely reject the E062 final single-atom law.
    assert all(pat(words[-1],[i for i,j in e['pairs']])!=pat(words[-1],[j for i,j in e['pairs']]) for e in events[3:])
    added=0
    for iteration,step in enumerate(data['history']):
        assert step['iteration']==iteration and step['columns']==len(columns) and step['events']==len(events)
        if step['status']!='SAT':
            assert iteration==len(data['history'])-1
            assert step['status'] in ('UNKNOWN','UNKNOWN_ENCODING_LIMIT','UNSAT_SEARCH_ONLY')
            continue
        y=step['y'];assert len(y)==270 and all(type(x) is int for x in y)
        assert all(sum(a*b for a,b in zip(y,c))>0 for c in columns)
        c=col(step['word']);score=sum(a*b for a,b in zip(y,c))
        assert score==step['score'] and score<=0
        columns.append(c);added+=1
    result=data['result'];law_support=None
    if 'library_separator' in data:
        sep=data['library_separator'];y=sep['y']
        assert len(y)==270 and all(type(x) is int for x in y)
        assert sep['columns']==len(columns)
        assert min(sum(a*b for a,b in zip(y,c)) for c in columns)==sep['margin']>0
    if result['status']=='RATIONAL_LAW':
        weights=[Q(s) for s in result['weights']]
        assert len(weights)==len(result['words']) and all(w>0 for w in weights) and sum(weights)==1
        cc=[col(w) for w in result['words']]
        assert all(sum(w*c[i] for w,c in zip(weights,cc))==0 for i in range(270))
        law_support=len(weights)
    else:assert result['status'] in ('UNKNOWN_ROUND_LIMIT','UNKNOWN_ENCODING_LIMIT','UNKNOWN_RATIONAL_EXTRACTION','UNKNOWN_DUAL','UNKNOWN_DUAL_ROUNDING','UNKNOWN','UNSAT_SEARCH_ONLY')
    combined=data.get('combined_repair',{})
    if combined.get('status')=='SAT':
        assert law_support==1
        word=result['words'][0];perms=combined['permutations'];assert len(perms)==5
        for motion,pi in zip(e062['motions'],perms):
            assert sorted(pi)==list(range(5))
            assert all(pi[int(word[i])]==int(word[j]) for i,j in motion['mapping'])
    return dict(experiment='E063',geometry=data['geometry'],mixed_quartets=18,partition_equalities=270,
                certified_countercolumns=added,joint_search_status=result['status'],rational_law_support=law_support,
                fixed_library_separator={k:v for k,v in data.get('library_separator',{}).items() if k!='y'},
                combined_E062_maximal_laws=combined.get('status')=='SAT',
                scope='Selected quartet laws; E062 full maximal laws only if combined flag true; not all partial isometries; no HN lower bound')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
