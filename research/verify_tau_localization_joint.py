"""Independent finite-domain and two prescribed marginal-law incompatibility.

Rebuilds all E077 geometry. Does not import the exploratory coupling producer,
SAT, or accept its negative status as evidence. Infinite T111 has a written proof.
"""
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import json
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice,digest


def verify(root):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    parent,c=geometry(root,geometry_context=True)
    r=c['ring'];mul=r['mul'];tau=r['tau'];X=r['points'];points=c['points']
    bar=lambda p:tuple(Q(x)/2 for x in conjugate_twice(p))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    z=r['blocks'][0][64];omega=tuple(-2*a-3*b for a,b in zip(one,z))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    # Exact identities used by T111, not a finite-n extrapolation.
    assert mul(tau,bar(tau))==one
    assert tuple(a+b for a,b in zip(tau,bar(tau)))==tuple(-a/5 for a in one)
    assert tau==tuple((9*a-8*b)/5 for a,b in zip(nu,one))
    assert bar(tau)==tuple((7*b-9*a)/5 for a,b in zip(nu,one))
    lookup={p:i for i,p in enumerate(points)}
    expected=[5084,556,5289,4671,1895];probes=[]
    def pattern(ids):
        labels={};return tuple(labels.setdefault(c['word'][i],len(labels)) for i in ids)
    for (name,a),count in zip([('tau',tau),('nu',nu),('eta',eta),('omega',omega),('bar',None)],expected):
        m=[]
        for i,p in enumerate(points):
            q=bar(p) if a is None else mul(a,p)
            if q in lookup:m.append((i,lookup[q]))
        assert len(m)==count
        if name=='tau':assert {i for i,j in m}=={lookup[p] for p in X}
        left,right=zip(*m);same=pattern(left)==pattern(right)
        assert not same  # A diagnostic about this saved word only.
        probes.append(dict(motion=name,domain=len(m),mapping_sha256=digest(m),saved_word_partition_equal=same))
    left={lookup[p]:r['residue'](p) for p in X}
    right={lookup[mul(tau,p)]:r['residue'](p) for p in X}
    shared=sorted(left.keys()&right.keys());assert len(shared)==91
    cross=[(u,v) for u,v in c['edges'] if not (u in left and v in left or u in right and v in right)]
    assert len(cross)==170
    characters=r['characters'];assert len(characters)==12
    values=lambda ch,layer:{v:sum(a*b for a,b in zip(ch,x))%5 for v,x in layer.items()}
    leftwords=[values(ch,left) for ch in characters];rightwords=[values(ch,right) for ch in characters]
    compatible=[];survivors=[];rejections=[]
    # Independently solve the overlap permutation relation, then enumerate only
    # its bijective extensions. This covers all 120 permutations for each pair.
    for a,lw in enumerate(leftwords):
        for b,rw in enumerate(rightwords):
            relation={(rw[v],lw[v]) for v in shared}
            if any(len({y for x,y in relation if x==k})>1 for k in range(5)):continue
            fixed=dict(relation)
            if len(set(fixed.values()))!=len(fixed):continue
            missing=[k for k in range(5) if k not in fixed]
            free=[k for k in range(5) if k not in fixed.values()]
            for completion in permutations(free):
                pi=dict(fixed);pi.update(zip(missing,completion))
                assert sorted(pi)==list(range(5)) and sorted(pi.values())==list(range(5))
                assert all(lw[v]==pi[rw[v]] for v in shared)
                compatible.append((a,b,tuple(pi[k] for k in range(5))))
                color=lambda v:lw[v] if v in lw else pi[rw[v]]
                bad=next(((u,v) for u,v in cross if color(u)==color(v)),None)
                if bad is None:survivors.append((a,b,pi))
                else:rejections.append(dict(left=a,right=b,permutation=[pi[k] for k in range(5)],edge=bad))
    assert compatible and not survivors
    return dict(status='PASS',theorems=['T111','T112'],experiment='E078',
                geometry=parent['geometry'],probes=probes,
                overlap_compatible=len(compatible),proper_gluings=len(survivors),
                rejections=rejections,
                scope='No proper coupling of the two prescribed T109 marginal laws; arbitrary new marginals and full joint remain open')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
