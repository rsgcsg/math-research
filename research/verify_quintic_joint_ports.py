"""Independent stdlib replay of E061; no producer or SAT imports."""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_core_probe import (multiplication_twice, product_twice,
                                      conjugate_twice, filter_map, digest)


def verify(root, certificate=None, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    data=json.loads((certificate or root/'certificates/quintic_joint_ports.json').read_text())
    raw=(root/'certificates/parts509_core.json').read_bytes()
    assert data['schema']==1 and data['experiment'] in ('E061','E062')
    assert hashlib.sha256(raw).hexdigest()==data['core_sha256']
    core=json.loads(raw);table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    P=[tuple(Q(x,core['coordinate_denominator']) for x in a+b+[0]*16) for a,b in core['points']]
    power=one;blocks=[P]
    for _ in range(4):
        power=mul(power,eta);r=tuple(-x for x in power);A=add(r,bar(r))
        blocks.extend([[mul(r,p) for p in P],[mul(r,add(A,p)) for p in P]])
    shift=add(one,mul(eta,P[64]));minus_eta=tuple(-x for x in eta)
    blocks.append([add(shift,mul(minus_eta,p)) for p in P])
    den=math.lcm(*(x.denominator for b in blocks for p in b for x in p))
    assert den==data['denominator']
    pts=sorted({tuple(int(x*den) for x in p) for b in blocks for p in b})
    physical=[tuple(Q(x,den) for x in p) for p in pts];lookup={p:i for i,p in enumerate(physical)}
    copies=[{lookup[p] for p in b} for b in blocks]
    prime,images,bars=filter_map(table);assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,
               sum(x*y for x,y in zip(p,bars))%prime) for p in pts]
    edges=[]
    for i,j in combinations(range(len(pts)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        d=[x-y for x,y in zip(pts[i],pts[j])]
        if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
    summary=dict(vertices=len(pts),actual_pairs=len(pts)*(len(pts)-1)//2,induced_edges=len(edges),
                 point_sha256=digest(pts),edge_sha256=digest(edges))
    assert summary==data['geometry']
    expected=[('eta',eta,zero,False),('conjugate',one,zero,True),('bridge',minus_eta,shift,False)]
    if data['experiment']=='E062':
        expected += [('translation_one',one,one,False),('translation_z',one,P[64],False)]
    assert len(data['motions'])==len(expected) and len(data['stages'])==len(expected)
    for m,(name,r,t,reflection) in zip(data['motions'],expected):
        assert m['name']==name and mul(r,bar(r))==one
        mapping=[]
        for i,p in enumerate(physical):
            q=add(t,mul(r,bar(p) if reflection else p))
            if q in lookup:mapping.append([i,lookup[q]])
        assert mapping==m['mapping']
        witness=m['mixed_witness']
        if name.startswith('translation_'):
            assert witness==[]
            continue
        assert len(witness)==4
        assert len({i for i,j in witness})==4 and all(pair in mapping for pair in witness)
        assert not any({i for i,j in witness}<=b or {j for i,j in witness}<=b for b in copies)
        for (i,j),(k,l) in combinations(witness,2):
            d=add(physical[i],tuple(-x for x in physical[k]))
            e=add(physical[j],tuple(-x for x in physical[l]))
            assert mul(d,bar(d))==mul(e,bar(e))
    for count,stage in enumerate(data['stages'],1):
        assert stage['motions']==count and stage['status']=='SAT'
        word=stage['word'];assert len(word)==len(pts) and set(word)<=set('01234')
        assert all(word[i]!=word[j] for i,j in edges)
        assert len(stage['permutations'])==count
        for motion,pi in zip(data['motions'],stage['permutations']):
            assert sorted(pi)==list(range(5))
            assert all(pi[int(word[i])]==int(word[j]) for i,j in motion['mapping'])
    # C018: regular unit pentagon plus isolated center, independently exact.
    power=one;q=zero
    for k in range(1,5):
        power=mul(power,eta);q=add(q,tuple(Q(k,5)*x for x in power))
    assert mul(add(eta,tuple(-x for x in one)),q)==one
    pent=[zero];power=one
    for _ in range(5):pent.append(mul(q,power));power=mul(power,eta)
    pent_edges=[]
    for i,j in combinations(range(6),2):
        d=add(pent[i],tuple(-x for x in pent[j]))
        if mul(d,bar(d))==one:pent_edges.append((i,j))
    assert pent_edges==[(1,2),(1,5),(2,3),(3,4),(4,5)]
    rotation=[0,2,3,4,5,1];word=[0,0,1,0,1,2]
    orbit=[]
    for _ in range(5):
        assert all(word[i]!=word[j] for i,j in pent_edges)
        orbit.append(tuple(word));word=[word[rotation[i]] for i in range(6)]
    assert set(orbit)=={tuple(w[rotation[i]] for i in range(6)) for w in orbit}
    # Enumerate all five-color equivariant words from center and first vertex.
    for pi in permutations(range(5)):
        for center in range(5):
            if pi[center]!=center:continue
            for start in range(5):
                cycle=[start]
                for _ in range(5):cycle.append(pi[cycle[-1]])
                assert cycle[-1]!=start or any(cycle[i]==cycle[i+1] for i in range(5))
    if data['experiment']=='E062':
        old=data['stages'][2]['word']
        for motion,pairs in zip(data['motions'][3:], [[[1,224],[7,238]],[[31,1],[186,25]]]):
            assert all(pair in motion['mapping'] for pair in pairs)
            (i,j),(k,l)=pairs
            assert (old[i]==old[k]) != (old[j]==old[l])
    result=dict(experiment=data['experiment'],geometry=summary,maximal_domains=[len(m['mapping']) for m in data['motions']],
                mixed_four_point_witnesses=3,full_words_checked=len(expected),C018='C5 plus isolated center verified')
    if geometry_context:return result,pts,edges,[lookup[p] for p in P],copies
    return result


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
