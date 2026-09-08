"""Independent integer geometry and positive-relation checker for Parts 509.

No SAT or search-module imports. Multiquadratic products are reconstructed from
gcds of squarefree radicands rather than the searcher's bit-mask multiplication.
"""
import gzip
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path

RADICANDS=(1,3,11,33,5,15,55,165)


def verify_geometry(path):
    data=json.loads(Path(path).read_text())
    pts=data['points'];den=data['coordinate_denominator']
    assert len(pts)==509 and type(den)==int and den>0
    assert all(len(p)==2 and all(len(x)==8 and all(type(v)==int for v in x) for x in p) for p in pts)
    assert len({tuple(map(tuple,p)) for p in pts})==509
    product={}
    for i,j in combinations(range(8),2):
        g=math.gcd(RADICANDS[i],RADICANDS[j])
        product[i,j]=(RADICANDS.index(RADICANDS[i]*RADICANDS[j]//(g*g)),2*g)
    edges=[]
    for a,b in combinations(range(509),2):
        squared=[0]*8
        for axis in range(2):
            delta=[x-y for x,y in zip(pts[a][axis],pts[b][axis])]
            squared[0]+=sum(d*d*r for d,r in zip(delta,RADICANDS))
            nz=[i for i,x in enumerate(delta) if x]
            for i,j in combinations(nz,2):
                index,factor=product[i,j]
                squared[index]+=factor*delta[i]*delta[j]
        if squared==[den*den]+[0]*7:
            edges.append((a,b))
    assert edges==list(map(tuple,data['induced_edges'])) and len(edges)==2442
    reduced=set(map(tuple,data['reduced_edges']))
    assert len(reduced)==2259 and reduced<=set(edges)
    verify_coloring(data['five_coloring'],edges)
    assert all(tuple(sorted(e)) in reduced for e in combinations((0,149,152),2))
    return data,edges


def verify_coloring(colors,edges):
    assert len(colors)==509 and all(type(c)==int and 0<=c<5 for c in colors)
    assert all(colors[a]!=colors[b] for a,b in edges)


def verify_pairs(path,edges):
    data=json.loads(Path(path).read_text())
    agree=[set() for _ in range(509)]
    differ=[set() for _ in range(509)]
    for word in data['models']:
        colors=list(map(int,word))
        verify_coloring(colors,edges)
        classes=[{i for i,c in enumerate(colors) if c==label} for label in range(5)]
        for v,c in enumerate(colors):
            agree[v].update(classes[c])
            for other in range(5):
                if other!=c:
                    differ[v].update(classes[other])
    edge_set=set(edges)
    for a,b in combinations(range(509),2):
        assert b in differ[a]
        if (a,b) not in edge_set:
            assert b in agree[a]
    return dict(witness_colorings=len(data['models']),distinct_pairs=math.comb(509,2),
                nonunit_equal_pairs=math.comb(509,2)-len(edges))


def canonical(values):
    order=[]
    result=[]
    for x in values:
        if x not in order:
            order.append(x)
        result.append(order.index(x))
    return tuple(result)


def verify_ports(path,edges):
    data=json.loads(gzip.decompress(Path(path).read_bytes()))
    ports=data['ports']
    assert len(ports)==len(set(ports))==12 and all(type(v)==int and 0<v<509 for v in ports)
    edge_set=set(edges)
    assert all((0,v) in edge_set for v in ports)
    local=[(i,j) for i,j in combinations(range(12),2) if tuple(sorted((ports[i],ports[j]))) in edge_set]
    expected=sorted(tuple(sorted((6*b+i,6*b+(i+1)%6))) for b in range(2) for i in range(6))
    assert local==expected==list(map(tuple,data['port_edges']))
    observed=set()
    for word in data['models']:
        colors=list(map(int,word))
        verify_coloring(colors,edges)
        assert colors[0]==0
        boundary=canonical([colors[v] for v in ports])
        assert all(boundary[i]!=boundary[j] for i,j in local)
        assert max(boundary)<=3
        observed.add(boundary)
    # C6 has P(q)=(q-1)^6+(q-1). For two disjoint copies P(q)^2.
    # With up to four unlabelled colors, count is S2+S3+S4, where P(q)^2
    # = sum_{j<=q} (q)_j S_j. This independently gives 22327.
    labeled=lambda q:((q-1)**6+(q-1))**2
    s2=labeled(2)//2
    s3=(labeled(3)-6*s2)//6
    s4=(labeled(4)-12*s2-24*s3)//24
    assert s2+s3+s4==22327
    assert len(observed)==22327
    return dict(boundary_vertices=13,proper_partition_patterns=len(observed),
                all_patterns_extend=True,checked_models=len(data['models']))


def verify(root):
    data,edges=verify_geometry(root/'certificates/parts509_core.json')
    from verify_rup_lrat import verify_parts
    return dict(status='VERIFIED_FIVE_CHROMATIC_PARTS_CORE_AND_RELATIONS',vertices=509,
                induced_edges=len(edges),all_pairs_checked=math.comb(509,2),
                pairs=verify_pairs(root/'certificates/parts509_pairs.json',edges),
                double_wheel=verify_ports(root/'certificates/parts509_ports.json.gz',edges),
                four_color_refutation=verify_parts(data,root/'certificates/parts509_reduced.lrat.gz'),
                chromatic_number=5)


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
