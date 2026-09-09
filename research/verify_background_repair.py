"""Replay list exclusions using direct radical geometry, without search code."""
from collections import defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json

from verify_multicenter_cores import rotate_at, unit


def verify(root,proof_override=None):
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    proof=proof_override if proof_override is not None else json.loads(gzip.decompress((root/'certificates/finite_background_obstruction.json.gz').read_bytes()))
    assert proof['input_sha256']=={name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
                                 for name in ('parts509_core.json','refined_center_arrays.json.gz','multicenter_cores.json')}
    contact=json.loads(gzip.decompress((root/'certificates/refined_center_arrays.json.gz').read_bytes()))['cases'][1]
    words=json.loads((root/'certificates/multicenter_cores.json').read_text())['both_arrays_coloring']['three_core_words']
    assert proof['schema']==1 and proof['layers']==2 and proof['background_words']==words
    corepoints=[tuple(map(tuple,p)) for p in core['points']];pointids={p:q for q,p in enumerate(corepoints)}
    adj=defaultdict(set)
    for q,r in core['induced_edges']:adj[q].add(r);adj[r].add(q)
    shifts=defaultdict(list)
    for dm,dn in ((3,0),(0,3),(-3,3),(-3,0),(0,-3),(3,-3)):
        dx,dy=16*(2*dm+dn),16*dn
        for q,p in enumerate(corepoints):
            a,b=map(list,p);a[0]+=dx;b[1]+=dy
            r=pointids.get((tuple(a),tuple(b)))
            if r is not None:shifts[q].append((dm,dn,r))
    steps=[(m,n) for m in range(-4,5) for n in range(-4,5) if m*m+m*n+n*n==12]
    def neighbors(v):
        s,m,n,q=v
        yield from ((s,m,n,r) for r in adj[q])
        if s:
            yield from ((s,m+dm,n+dn,r) for dm,dn,r in shifts[q])
            yield from ((s,m+dm,n+dn,q) for dm,dn in steps)
    patch={(0,0,0,q) for q in range(509)}
    for name in ('base_instances','base_equal_instances'):
        for q,r,m,n in contact[name]:patch.update(((1,m,n,r),(-1,m,n,r)))
    for name in ('dual_instances','dual_equal_instances'):
        for q,r,m,n,a,b in contact[name]:patch.update(((1,m,n,q),(-1,a,b,r)))
    parent={};merge_rank=0
    def find(v):
        parent.setdefault(v,v)
        if parent[v]!=v:parent[v]=find(parent[v])
        return parent[v]
    equalities=[((0,0,0,q),(s,m,n,r)) for q,r,m,n in contact['base_equal_instances'] for s in (-1,1)]
    equalities += [((1,m,n,q),(-1,a,b,r)) for q,r,m,n,a,b in contact['dual_equal_instances']]
    for a,b in equalities:
        a,b=find(a),find(b)
        if a!=b:parent[a]=b;merge_rank+=1
    assert len(equalities)==549 and merge_rank==506
    for _ in range(2):patch |= {w for v in patch for w in neighbors(v)}
    assert len(patch)==proof['patch_vertices']==419763
    @lru_cache(None)
    def point(v):
        s,m,n,q=v
        assert s in (0,1,-1) and 0<=q<509 and (s or (m,n)==(0,0))
        center=((16*(2*m+n),)+(0,)*7,(0,16*n)+(0,)*6)
        return rotate_at(core['points'][q],center,s)
    def background(v):
        s,m,n,q=v
        return (int(words[0 if s==0 else 1 if s==1 else 2][q])+(m%3 if s else 0))%5
    facts=[];seen=set();geometry=set();boundary=set()
    for i,row in enumerate(proof['proof']):
        v=tuple(row['vertex']);w=tuple(row['neighbor']);c=row['color'];parents=row['parents']
        assert v in patch and c in range(5) and (v,c) not in seen
        assert all(type(p)==int and 0<=p<i for p in parents)
        if row['kind']=='boundary':
            assert not parents and w not in patch and background(w)==c
            assert unit(point(v),point(w),768);boundary.add(w)
        elif row['kind']=='equality':
            assert len(parents)==1 and facts[parents[0]]==(w,c)
            assert point(v)==point(w)
        elif row['kind']=='edge':
            assert len(parents)==4 and {facts[p] for p in parents}=={(w,d) for d in range(5) if d!=c}
            assert unit(point(v),point(w),768)
        else:raise AssertionError(row['kind'])
        geometry.add(tuple(sorted((v,w))));facts.append((v,c));seen.add((v,c))
    conclusion=tuple(proof['conclusion_vertex'])
    assert all((conclusion,c) in seen for c in range(5))
    finite=proof['finite_graph']
    labels=sorted({tuple(row[k]) for row in proof['proof'] for k in ('vertex','neighbor')})
    assert list(map(list,labels))==finite['labels']
    points=[];pointids={};aliases=[]
    for v in labels:
        p=point(v)
        if p not in pointids:pointids[p]=len(points);points.append(p)
        aliases.append(pointids[p])
    assert aliases==finite['aliases'] and len(points)==finite['vertices']
    edges={(a,b) for a,b in combinations(range(len(points)),2) if unit(points[a],points[b],768)}
    assert len(edges)==finite['edges']
    colors=list(map(int,finite['three_coloring']))
    assert len(colors)==len(points) and set(colors)<=set(range(3))
    assert all(colors[a]!=colors[b] for a,b in edges)
    adjacency=defaultdict(set)
    for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
    assert any(adjacency[a]&adjacency[b] for a,b in edges),'Need an actual triangle for chi=3'
    boundary_ids={pointids[point(v)]:background(v) for v in boundary}
    assert len(boundary_ids)==len(boundary)
    assert all(boundary_ids[a]!=boundary_ids[b] for a,b in edges if a in boundary_ids and b in boundary_ids)
    return dict(status='PASS',scope='Specified radius-two graph-neighborhood patch and fixed background only',
                patch_vertices=len(patch),deletion_steps=len(facts),geometric_relations=len(geometry),
                patch_physical_vertices=len(patch)-merge_rank,
                boundary_vertices=len(boundary),proof_vertices=len({v for v,c in seen}),
                finite_induced_vertices=len(points),finite_induced_edges=len(edges),
                all_finite_pairs_checked=len(points)*(len(points)-1)//2,unconditioned_chromatic_number=3)


if __name__=='__main__':
    if not __debug__:raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
