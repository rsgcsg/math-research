"""Independent full-domain positive checker for E097. No search imports."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
from verify_quintic_tau_union import verify as geometry
from verify_quintic_multiword_joint import _definitions, _check_data as check_legacy
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest


def shape(word,ids):
    # Different implementation of unlabelled partitions: block membership sets.
    groups={}
    for pos,i in enumerate(ids):groups.setdefault(word[i],[]).append(pos)
    return tuple(sorted(tuple(v) for v in groups.values()))


def check(root,data,parent,c):
    if not __debug__:raise RuntimeError('Do not disable verification assertions')
    assert data['schema']==1 and data['experiment']=='E097'
    assert data['geometry']==parent['geometry']
    assert data['support']==data['colors']==5
    result=data['result'];assert isinstance(result,dict)
    words=result['words'];assert isinstance(words,list) and len(words)==5
    for word in words:
        assert isinstance(word,str) and len(word)==len(c['points']) and set(word)<=set('01234')
        assert all(word[i]!=word[j] for i,j in c['edges'])
    additions=_new_definitions(c);u=additions[0][1]
    definitions=_definitions(c)+[additions[0],('dyadic_u_squared',c['ring']['mul'](u,u),(Q(0),)*32,False),additions[1]]
    count=result['full_domain_count'];assert type(count) is int and count in (15,16,17)
    assert result['motions']==[d[0] for d in definitions[:count]]
    for key in ('word_permutations','color_permutations','mapping_sha256'):
        assert isinstance(result[key],list) and len(result[key])==count
    legacy=deepcopy(data);legacy['experiment']='E083'
    for key in ('motions','word_permutations','color_permutations','mapping_sha256'):
        legacy['result'][key]=legacy['result'][key][:14]
    legacy_report=check_legacy(root,legacy,parent,c)
    domains=[];equalities=0
    for t,definition in enumerate(definitions[:count]):
        mapping=_mapping(c,definition)
        assert digest(mapping)==result['mapping_sha256'][t]
        if t>=14:assert len(mapping)==[29,805,33][t-14]
        s=result['word_permutations'][t];p=result['color_permutations'][t]
        assert all(type(x) is int for x in s) and sorted(s)==list(range(5))
        assert len(p)==5
        for a in range(5):
            assert all(type(x) is int for x in p[a]) and sorted(p[a])==list(range(5))
            assert all(int(words[s[a]][j])==p[a][int(words[a][i])] for i,j in mapping)
        assert Counter(shape(w,[i for i,j in mapping]) for w in words)==Counter(shape(w,[j for i,j in mapping]) for w in words)
        domains.append(dict(motion=definition[0],size=len(mapping)));equalities+=len(mapping)*5
    return dict(status='PASS',experiment='E097',proper_edge_obligations=5*len(c['edges']),
                exact_mapping_obligations=equalities,full_domains=domains,
                whole_partition_multisets=True,retained_old_full_domains=14,
                retained_old_X_maps=len(legacy_report['retained_E065_maps']),
                retained_old_four_point_events=legacy_report['retained_E063_quartets'],
                geometry=parent['geometry'],scope='Listed full domains only; not a new plane bound')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Do not disable verification assertions')
    root=Path(__file__).resolve().parents[1];path=root/'certificates/joint_pair_cegar.json'
    data=json.loads(path.read_text())
    if data['result'] is None:
        report=dict(status='NO_POSITIVE_WITNESS',search_status=data['search']['status'],
                    scope='No mathematical negative conclusion is certified')
    else:
        parent,context=geometry(root,geometry_context=True);report=check(root,data,parent,context)
    report['certificate_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    (root/'certificates/joint_pair_cegar_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VALIDATION '+json.dumps(report),flush=True)
