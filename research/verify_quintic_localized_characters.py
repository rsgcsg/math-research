"""Independent exact localized-coset, character-screen and positive-word audit."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import json
from verify_quintic_joint_ports import verify as geometry
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice


def verify(root):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    parent,pts,edges,base,_=geometry(root,root/'certificates/quintic_joint_translations.json',geometry_context=True)
    den=json.loads((root/'certificates/quintic_joint_translations.json').read_text())['denominator']
    points=[tuple(Q(x,den) for x in p) for p in pts]
    table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16];z=points[base[64]]
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    omega=tuple(-2*a-3*b for a,b in zip(one,z));powers=[one]
    for _ in range(4):powers.append(mul(eta,powers[-1]))
    basis=powers[:4]+[mul(z,p) for p in powers[:4]]
    basis += [mul(nu,p) for p in basis[:]]
    rows=[]
    for j,vector in enumerate(basis):
        v=list(vector);e=[Q(int(i==j)) for i in range(16)]
        for pivot,row,old in rows:
            factor=v[pivot];v=[x-factor*y for x,y in zip(v,row)];e=[x-factor*y for x,y in zip(e,old)]
        assert any(v);pivot=next(i for i,x in enumerate(v) if x);scale=v[pivot]
        rows.append((pivot,[x/scale for x in v],[x/scale for x in e]))
    def decompose(p):
        v=list(p);coeff=[Q(0)]*16
        for pivot,row,e in rows:
            factor=v[pivot];v=[x-factor*y for x,y in zip(v,row)];coeff=[x+factor*y for x,y in zip(coeff,e)]
        assert all(p[i]==v[i]+sum(coeff[j]*basis[j][i] for j in range(16)) for i in range(32))
        return tuple(v),coeff
    def mod5(x):return x.numerator*pow(x.denominator,-1,5)%5
    def split(p):
        rem,coeff=decompose(p);residues=[];shifts=[]
        for x in coeff:
            d=x.denominator
            while d%3==0:d//=3
            # Independent small-residue search instead of modular inversion.
            residue=next(Q(k,d) for k in range(d) if is_local(x-Q(k,d)))
            residues.append(residue);shifts.append(mod5(x-residue))
        return (rem,tuple(residues)),tuple(sum(shifts[i:i+4])%5 for i in range(0,16,4))
    def is_local(x):
        d=x.denominator
        while d%3==0:d//=3
        return d==1
    def dot(a,b):return sum(x*y for x,y in zip(a,b))%5
    pdata=[split(p) for p in points];keys={key for key,h in pdata}
    assert len(keys)==646
    screen=json.loads((root/'certificates/quintic_localized_character_screen.json').read_text())
    assert screen['schema']==1 and screen['experiment']=='E074' and screen['module_cosets']==646
    assert screen['geometry']==parent['geometry']
    characters=[c for c in product(range(5),repeat=4) if any(c) and next(x for x in c if x)==1]
    expected=[]
    for ch in characters:
        witness=next(([u,v] for u,v in edges if pdata[u][0]==pdata[v][0] and dot(ch,pdata[u][1])==dot(ch,pdata[v][1])),None)
        expected.append(dict(character=list(ch),zero_edge=witness))
    assert expected==screen['witnesses']
    survivors=[tuple(row['character']) for row in expected if row['zero_edge'] is None]
    assert len(survivors)==12
    data=json.loads((root/'certificates/quintic_twelve_characters.json').read_text())
    assert data['schema']==1 and data['experiment']=='E075' and data['geometry']==parent['geometry']
    assert data['characters']==list(map(list,survivors)) and data['module_cosets']==646
    assert [s['stage'] for s in data['stages']]==['all_N_translations','four_generators_with_N_translations']
    for stage in data['stages']:
        assert stage['status']=='SAT' and len(stage['words'])==12
        labels=[{} for _ in survivors]
        for j,(ch,word) in enumerate(zip(survivors,stage['words'])):
            assert len(word)==len(points) and set(word)==set('01234')
            assert all(word[u]!=word[v] for u,v in edges)
            for color,(key,h) in zip(word,pdata):
                value=(int(color)-dot(ch,h))%5
                assert labels[j].setdefault(key,value)==value
    words=data['stages'][-1]['words']
    def check_orientation(r,reflection):
        def op(p):return mul(r,bar(p) if reflection else p)
        transforms=[]
        for ch in survivors:
            values=[]
            for b in (one,z,nu,mul(nu,z)):
                rem,c=decompose(op(b));assert not any(rem) and all(is_local(x) for x in c)
                values.append(dot(ch,[mod5(sum(c[i:i+4])) for i in range(0,16,4)]))
            scale=next(x for x in values if x);target=tuple(x*pow(scale,-1,5)%5 for x in values)
            transforms.append((survivors.index(target),scale))
        count=0
        for i,p in enumerate(points):
            key,h=split(op(p))
            if key not in keys:continue
            count+=1
            for j,(other,scale) in enumerate(transforms):
                if labels[j][key]!=(scale*int(words[other][i])-dot(survivors[j],h))%5:
                    return dict(status='MISMATCH',point=i,character=j)
        return dict(status='PASS',coset_hits=count)
    generator_results={name:check_orientation(r,reflection) for name,r,reflection in
                       [('eta',eta,False),('omega',omega,False),('conjugate',one,True),('nu',nu,False)]}
    assert all(v['status']=='PASS' for v in generator_results.values())
    full=[];om=one
    for k in range(3):
        for e,ep in enumerate(powers):
            for reflection in (False,True):
                for sign in (1,-1):
                    r=tuple(sign*x for x in mul(om,ep))
                    result=check_orientation(r,reflection)
                    full.append(dict(k=k,e=e,reflection=reflection,sign=sign,**result))
        print('independent H30 block',k,flush=True)
        om=mul(om,omega)
    return dict(status='PASS',experiments=['E074','E075'],geometry=parent['geometry'],
                module_cosets=646,screened_projective_characters=156,survivors=12,
                stages_checked=2,proper_words_checked=24,generators=generator_results,
                old_full_orientations=full,
                scope='All N translations and four complete N-coset orientations certified; full H30 status explicit, infinite nu powers not inferred')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
