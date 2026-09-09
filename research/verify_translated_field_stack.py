"""Independent finite residue targets and explicit orthogonal transports.

The lift to all of K^2 and all integer sheets requires T063's proof.
"""
from itertools import combinations,product
from pathlib import Path
import json


def verify(root):
    data=json.loads((root/'certificates/translated_field_stack.json').read_text())
    assert data['schema']==1 and data['prime']==11
    vertices=list(product(range(2),range(11),range(11)));seen={};total_edges=0
    for case in data['cases']:
        u,v=case['offset'];norm=(u*u+v*v)%11
        assert norm==case['norm'] and norm not in seen
        assert case['status']=='SAT_CANDIDATE' and case['vertices']==242
        colors=list(map(int,case['word']));assert len(colors)==242 and set(colors)<=set(range(5))
        count=0
        for i,j in combinations(range(242),2):
            a,x,y=vertices[i];b,z,t=vertices[j]
            dx,dy=(x-z)%11,(y-t)%11
            same=a==b and (dx*dx+dy*dy)%11==1
            cross=a!=b and (dx,dy) in ((u,v),(-u%11,-v%11))
            if same or cross:assert colors[i]!=colors[j];count+=1
        assert count==case['edges'];total_edges+=count;seen[norm]=(u,v)
    assert set(seen)==set(range(11)) and seen[0]==(0,0)
    transforms=0
    for x,y in product(range(11),repeat=2):
        norm=(x*x+y*y)%11
        if norm==0:assert (x,y)==(0,0);continue
        u,v=seen[norm];inv=pow(norm,-1,11)
        # M=[u,Ju][v,Jv]^T/n maps source (x,y) to representative (u,v).
        c=(u*x+v*y)*inv%11;s=(v*x-u*y)*inv%11
        assert (c*c+s*s)%11==1
        assert ((c*x-s*y)%11,(s*x+c*y)%11)==(u,v)
        transforms+=1
    return dict(status='PASS',target_graphs=len(seen),target_vertices_each=242,
                all_target_pairs_checked=11*242*241//2,target_edges_checked=total_edges,
                nonzero_offset_orthogonal_transports=transforms,
                scope='All 121 residue offsets covered; arbitrary denominators and infinite sheets use T063')


if __name__=='__main__':
    if not __debug__:raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
