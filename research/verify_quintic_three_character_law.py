"""Independent three-word full joint checker, over exact module cosets."""
from pathlib import Path
import hashlib
import json
from verify_quintic_module_law import verify as predecessor


def verify(root,certificate=None,*,expected_experiment='E070',geometry_context=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/quintic_three_character_law.json').read_text())
    assert data['schema']==1 and data['experiment']==expected_experiment
    raw=(root/'certificates/quintic_module_law.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['parent_sha256']
    parent,context=predecessor(root,geometry_context=True)
    assert data['geometry']==parent['geometry']
    points=context['physical'];mul=context['mul'];bar=context['bar'];decompose=context['decompose']
    one=context['one'];z=context['z'];omega=tuple(-2*x-3*y for x,y in zip(one,z))
    omegas=[one,omega,mul(omega,omega)]
    assert mul(omegas[2],omega)==one and mul(omega,bar(omega))==one
    assert all(x+y+z==0 for x,y,z in zip(*omegas))
    def split(p):
        rem,coeff=decompose(p);integers=[v.numerator//v.denominator for v in coeff]
        a=sum(integers[:4]);b=sum(integers[4:])
        return (rem,tuple(v-i for v,i in zip(coeff,integers))),[(a+2*b)%5,(2*a+3*b)%5,(2*a)%5]
    for i,basis_vector in enumerate(context['basis']):
        for j,om in enumerate(omegas):
            rem,coeff=decompose(mul(om,basis_vector))
            assert not any(rem) and all(v.denominator==1 for v in coeff)
            character=sum(coeff[:4])+2*sum(coeff[4:])
            expected=((1,2),(2,3),(2,0))[j][int(i>=4)]
            assert character%5==expected
    point_data=[split(p) for p in points];assert len({key for key,h in point_data})==data['cosets']==941
    result=data['result'];assert result['status']=='SAT' and len(result['words'])==3
    words=result['words'];labels=[{} for _ in range(3)]
    for j,word in enumerate(words):
        assert isinstance(word,str) and len(word)==len(points) and set(word)==set('01234')
        assert all(word[a]!=word[b] for a,b in context['edges'])
        for (key,h),color in zip(point_data,word):
            value=(int(color)-h[j])%5
            assert labels[j].setdefault(key,value)==value
    counts={}
    for k,om in enumerate(omegas):
        for e,ep in enumerate(context['powers']):
            r=mul(om,ep)
            for sign in (1,-1):
                for reflection in (False,True):
                    count=0
                    for i,p in enumerate(points):
                        q=mul(r,bar(p) if reflection else p)
                        key,h=split(tuple(sign*x for x in q))
                        if key not in labels[0]:continue
                        count+=1
                        for j in range(3):
                            other=(j+k)%3
                            if reflection:other=(-other)%3
                            assert labels[j][key]==(sign*int(words[other][i])-h[j])%5
                    counts[(reflection,sign,k,e)]=count
    assert len(counts)==60 and data['orbit_hits']==[[r,s,k,e,counts[(r,s,k,e)]] for r in (False,True) for s in (1,-1) for k in range(3) for e in range(5)]
    # The old one-word law is genuinely changed, not merely renamed.
    oldword=json.loads(raw)['stages'][-1]['word']
    pairs=((0,4787),(2,3700))
    assert all(mul(omega,points[i])==points[j] for i,j in pairs)
    (i,j),(k,l)=pairs;assert (oldword[i]==oldword[k])!=(oldword[j]==oldword[l])
    report=dict(status='PASS',experiment=expected_experiment,theorem='T104',geometry=parent['geometry'],
                proper_words=3,module_rank=8,module_cosets=941,orthogonal_maps=60,
                old_word_partition_mismatch=[list(p) for p in pairs],
                scope='One mixture of three S5-averaged words for all X-domains in M semidirect H30; not all plane motions or an infinite induced coloring')
    return (report,context) if geometry_context else report


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
