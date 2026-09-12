"""Stdlib independent exact module-coset and affine-law verification.

No search/producer, SymPy, SAT, or LP imports. Does not infer a proper coloring
of the infinite orbit, whose new edges are not checked here.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
from verify_quintic_full_translation_laws import verify as predecessor
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice


def verify(root,certificate=None,geometry_context=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/quintic_module_law.json').read_text())
    assert data['schema']==1 and data['experiment']=='E069'
    oldraw=(root/'certificates/quintic_full_translation_laws.json').read_bytes()
    assert data['parent_sha256']==hashlib.sha256(oldraw).hexdigest()
    parent,points,edges,base=predecessor(root,geometry_context=True)
    assert data['geometry']==parent['geometry']
    den=json.loads((root/'certificates/quintic_joint_translations.json').read_text())['denominator']
    table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    physical=[tuple(Q(x,den) for x in p) for p in points];z=physical[base[64]]
    powers=[one]
    for j in range(4):powers.append(mul(powers[-1],eta))
    assert mul(powers[-1],eta)==one
    basis=powers[:4]+[mul(z,p) for p in powers[:4]]
    # Independent rational row reduction, carrying direct basis identities.
    reduced=[]
    for j,vector in enumerate(basis):
        v=list(vector);expression=[Q(int(i==j)) for i in range(8)]
        for pivot,row,coeff in reduced:
            factor=v[pivot]
            v=[x-factor*y for x,y in zip(v,row)]
            expression=[x-factor*y for x,y in zip(expression,coeff)]
        pivot=next(i for i,x in enumerate(v) if x);scale=v[pivot]
        v=[x/scale for x in v];expression=[x/scale for x in expression]
        new=[]
        for p,row,coeff in reduced:
            factor=row[pivot]
            new.append((p,[x-factor*y for x,y in zip(row,v)],
                        [x-factor*y for x,y in zip(coeff,expression)]))
        reduced=sorted(new+[(pivot,v,expression)])
    assert len(reduced)==8 and [p for p,_,_ in reduced]==data['basis_pivots']
    for pivot,row,coeff in reduced:
        assert all(row[i]==sum(coeff[j]*basis[j][i] for j in range(8)) for i in range(32))
    def decompose(p):
        v=list(p);coeff=[Q(0)]*8
        for pivot,row,expression in reduced:
            factor=v[pivot]
            v=[x-factor*y for x,y in zip(v,row)]
            coeff=[x+factor*y for x,y in zip(coeff,expression)]
        return tuple(v),coeff
    def split(p):
        remainder,coeff=decompose(p);floors=[v.numerator//v.denominator for v in coeff]
        return (remainder,tuple(v-i for v,i in zip(coeff,floors))),sum(floors[:4]+[2*x for x in floors[4:]])%5
    # Verify generator stability and phi transformation; inverse matrices need
    # not be guessed, since eta has order 5 and conjugation/negation order 2.
    for operation,sign in ((lambda p:mul(eta,p),1),(bar,1),(lambda p:tuple(-x for x in p),-1)):
        for j,p in enumerate(basis):
            remainder,coeff=decompose(operation(p))
            assert not any(remainder) and all(x.denominator==1 for x in coeff)
            assert sum(coeff[:4]+[2*x for x in coeff[4:]])%5==sign*(1 if j<4 else 2)%5
    point_data=[split(p) for p in physical]
    assert len({key for key,h in point_data})==data['cosets']==941
    assert [s['stage'] for s in data['stages']]==['translations','full_group']
    words=[]
    for stage in data['stages']:
        assert stage['status']=='SAT'
        word=stage['word'];assert len(word)==len(points) and set(word)==set('01234')
        assert all(word[i]!=word[j] for i,j in edges)
        labels={}
        for (key,h),c in zip(point_data,word):
            value=(int(c)-h)%5
            assert labels.setdefault(key,value)==value
        if stage['stage']=='full_group':
            hits=[]
            for reflection in (False,True):
                for sign in (1,-1):
                    for j,power in enumerate(powers):
                        count=0
                        for p,c in zip(physical,word):
                            q=tuple(sign*x for x in mul(power,bar(p) if reflection else p));key,h=split(q)
                            if key not in labels:continue
                            count+=1;assert labels[key]==(sign*int(c)-h)%5
                        hits.append([reflection,sign,j,count])
            assert hits==data['orbit_hits']
        words.append(word)
    old=json.loads(oldraw);oldword=old['result']['word'];lookup={p:i for i,p in enumerate(points)}
    assert [(e['power'],e['kind']) for e in data['extra_translations']]==[(j,k) for j in range(1,5) for k in ('unit','root')]
    for e in data['extra_translations']:
        t=powers[e['power']] if e['kind']=='unit' else mul(powers[e['power']],z)
        assert all((x*den).denominator==1 for x in t)
        shift=tuple(int(x*den) for x in t);mapping=[]
        for i,p in enumerate(points):
            q=tuple(x+y for x,y in zip(p,shift))
            if q in lookup:mapping.append((i,lookup[q]))
        assert len(mapping)==e['domain'] and sorted(e['permutation'])==list(range(5))
        assert all(e['permutation'][int(oldword[i])]==int(oldword[j]) for i,j in mapping)
    report=dict(status='PASS',experiment='E069',theorem='T103',geometry=parent['geometry'],
                module_rank=8,cosets=941,proper_words_checked=2,orthogonal_maps_checked=20,
                extra_translation_domains=[e['domain'] for e in data['extra_translations']],
                scope='Full maximal X-domains for every motion in M semidirect H; not all congruences, not an infinite orbit coloring')
    if geometry_context:
        return report,dict(physical=physical,points=points,edges=edges,basis=basis,powers=powers,
                           one=one,z=z,mul=mul,bar=bar,decompose=decompose)
    return report


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
