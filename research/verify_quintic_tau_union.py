"""E077 independent actual induced graph checker, including all cross edges."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
from verify_quintic_residue5_ring import verify as ring
from verify_quintic_core_probe import filter_map,product_twice,conjugate_twice,digest


def verify(root,geometry_context=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((root/'certificates/quintic_tau_union.json').read_text())
    assert data['schema']==1 and data['experiment']=='E077'
    assert data['core_sha256']==hashlib.sha256((root/'certificates/parts509_core.json').read_bytes()).hexdigest()
    _,context=ring(root,geometry_context=True)
    X=context['points'];mul=context['mul'];tau=context['tau'];table=context['table']
    right=[mul(tau,p) for p in X]
    den=math.lcm(*(x.denominator for p in X+right for x in p));assert den==data['denominator']
    integer=lambda p:tuple(int(x*den) for x in p)
    first={integer(p) for p in X};second={integer(p) for p in right};points=sorted(first|second)
    prime,images,bars=filter_map(table);assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        d=[x-y for x,y in zip(points[i],points[j])]
        if product_twice(d,conjugate_twice(d),table)==[4*den*den]+[0]*31:edges.append((i,j))
    geometry=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,induced_edges=len(edges),
                  point_sha256=digest(points),edge_sha256=digest(edges),overlap=len(first&second),
                  new_cross_edges=sum(not ({points[u],points[v]}<=first or {points[u],points[v]}<=second) for u,v in edges))
    assert geometry==data['geometry']
    assert data['result']['status']=='SAT'
    word=data['result']['five_coloring'];assert len(word)==len(points) and set(word)==set('01234')
    assert all(word[i]!=word[j] for i,j in edges)
    outside=sum(any(x.denominator%5==0 for x in context['coordinates'](tuple(Q(a,den) for a in p))) for p in points)
    assert outside>0
    report=dict(status='PASS',experiment='E077',geometry=geometry,points_outside_ring=outside,
                scope='Actual induced X union tau X is five-colorable; not full joint or all tau layers')
    if geometry_context:
        return report,dict(ring=context,points=[tuple(Q(a,den) for a in p) for p in points],
                           edges=edges,word=word)
    return report


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
