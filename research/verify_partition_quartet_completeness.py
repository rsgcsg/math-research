"""Independent standard-library E098 certificate checker; no producer import.

Checks the entire support-cover refutation DAG, exact sharpness examples, and
all degree-two moment signatures of <=5-entry multisets on four points.
The arbitrary-size T127 assertion is proved in the accompanying document.
"""
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import gzip
import hashlib
import json


def normalize(values):
    # Canonical labels are the first positions of the respective blocks.
    first = {}
    return tuple(first.setdefault(v, i) for i, v in enumerate(values))


def all_partitions(n, k):
    # Independent generation by merging a new singleton into each old block.
    states = {()}
    for i in range(n):
        out = set()
        for old in states:
            for label in set(old) | {i}:
                q = old + (label,)
                if len(set(q)) <= k:
                    out.add(normalize(q))
        states = out
    return states


def restricted_law(words, weights, ids):
    result = Counter()
    for word, weight in zip(words, weights):
        result[normalize(word[i] for i in ids)] += weight
    return dict(result)


def check(data, exhaustive=True):
    if not __debug__:
        raise RuntimeError('Verification cannot run with disabled assertions')
    assert data['schema']=='partition-quartet-v1' and data['experiment']=='E098'
    assert (data['support_limit'],data['block_limit'],data['points'])==(5,5,6)
    ps=data['partitions']
    assert isinstance(ps,list) and len(ps)==202
    assert all(isinstance(p,list) and len(p)==6 and all(type(x) is int for x in p) for p in ps)
    canonical=[normalize(p) for p in ps]
    assert len(set(canonical))==202 and set(canonical)==all_partitions(6,5)
    nodes=data['nodes']; assert isinstance(nodes,list) and nodes
    fibers=defaultdict(set)
    for a,p in enumerate(ps):
        for deleted in range(6):
            fibers[deleted,normalize(p[i] for i in range(6) if i!=deleted)].add(a)
    states=[]; branches=leaves=arcs=0
    for index,node in enumerate(nodes):
        assert isinstance(node,list) and len(node)==6
        positive,negative,side,a,deleted,children=node
        for support in (positive,negative):
            assert isinstance(support,list) and len(support)<=5
            assert all(type(x) is int and 0<=x<202 for x in support)
            assert sorted(set(support))==support
        assert not set(positive).intersection(negative)
        assert type(side) is int and side in (-1,1)
        assert type(a) is int and type(deleted) is int and 0<=deleted<6
        chosen,opposite=(positive,negative) if side==1 else (negative,positive)
        assert a in chosen
        fiber=fibers[deleted,normalize(ps[a][i] for i in range(6) if i!=deleted)]
        assert not fiber.intersection(opposite)
        options=sorted(fiber.difference(chosen)) if len(opposite)<5 else []
        assert isinstance(children,list) and len(children)==len(options)
        for b,child in zip(options,children):
            assert type(child) is int and 0<=child<index
            expected=(tuple(positive),tuple(sorted(negative+[b]))) if side==1 else (tuple(sorted(positive+[b])),tuple(negative))
            assert states[child]==expected
        states.append((tuple(positive),tuple(negative)))
        branches+=bool(children);leaves+=not children;arcs+=len(children)
    expected_shapes={tuple(sorted(Counter(p).values(),reverse=True)) for p in ps}
    roots=data['roots'];assert isinstance(roots,list) and len(roots)==10
    assert {tuple(r['shape']) for r in roots}==expected_shapes
    for root in roots:
        a,index=root['atom'],root['node']
        assert type(a) is int and 0<=a<202 and type(index) is int and 0<=index<len(nodes)
        assert tuple(root['shape'])==tuple(sorted(Counter(ps[a]).values(),reverse=True))
        assert states[index]==((a,),())
    reached=set();stack=[r['node'] for r in roots]
    while stack:
        node=stack.pop()
        if node not in reached:
            reached.add(node);stack.extend(nodes[node][5])
    assert len(reached)==len(nodes)
    samples=data['sharpness'];assert set(samples)=={'four_points_necessary','unequal_weights_need_five','six_colors_defeat_four_points'}
    totals={}
    for name,s in samples.items():
        left,right=s['left'],s['right'];wl,wr=s['weights_left'],s['weights_right']
        n=len(left[0]);assert len(left)==len(right)==len(wl)==len(wr)==5
        assert all(isinstance(w,str) and len(w)==n for w in left+right)
        assert all(type(x) is int and x>0 for x in wl+wr) and sum(wl)==sum(wr)
        assert max(map(lambda w:len(set(w)),left+right))<=s['maximum_blocks']
        depth=s['equal_through_points'];assert 0<=depth<n
        for size in range(depth+1):
            for ids in combinations(range(n),size):
                assert restricted_law(left,wl,ids)==restricted_law(right,wr,ids)
        assert restricted_law(left,wl,range(n))!=restricted_law(right,wr,range(n))
        totals[name]=dict(points=n,equal_restrictions_through=depth,total_integer_mass=sum(wl))
    assert samples['four_points_necessary']['weights_left']==samples['four_points_necessary']['weights_right']==[1]*5
    assert samples['four_points_necessary']['equal_through_points']==3
    assert samples['unequal_weights_need_five']['equal_through_points']==4
    assert samples['unequal_weights_need_five']['maximum_blocks']==5
    assert samples['six_colors_defeat_four_points']['weights_left']==samples['six_colors_defeat_four_points']['weights_right']==[1]*5
    assert samples['six_colors_defeat_four_points']['equal_through_points']==5
    assert any(len(set(w))==6 for w in samples['six_colors_defeat_four_points']['left']+samples['six_colors_defeat_four_points']['right'])
    checked=0
    if exhaustive:
        small=sorted(all_partitions(4,5));pairs=list(combinations(range(4),2))
        vectors=[]
        for p in small:
            eq=[int(p[i]==p[j]) for i,j in pairs]
            vectors.append(tuple(eq[i]*eq[j] for i,j in combinations_with_replacement(range(6),2)))
        for m in range(1,6):
            signatures={}
            for atoms in combinations_with_replacement(range(len(small)),m):
                signature=tuple(sum(vectors[a][j] for a in atoms) for j in range(21))
                assert signature not in signatures
                signatures[signature]=atoms;checked+=1
    return dict(status='PASS',experiment='E098',partition_count=202,roots=10,
                support_cover_nodes=len(nodes),support_cover_branches=branches,
                support_cover_leaves=leaves,support_cover_arcs=arcs,
                exact_sharpness=totals,four_point_multisets_checked=checked,
                scope='DAG proves the finite six-point lemma used by T128; T127 uses the written arbitrary-size proof')


def verify(root):
    if not __debug__:raise RuntimeError('Verification cannot run with disabled assertions')
    raw=(Path(root)/'certificates/partition_quartet_completeness.json.gz').read_bytes()
    report=check(json.loads(gzip.decompress(raw)))
    report['certificate_sha256']=hashlib.sha256(raw).hexdigest()
    return report


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
