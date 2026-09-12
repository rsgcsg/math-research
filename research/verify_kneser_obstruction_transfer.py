"""Independent direct disjointness/weight checks; no SAT or producer import."""
from pathlib import Path
from itertools import combinations
import hashlib
import json
from verify_mycielski_collision_refutation import verify as verify_obstruction


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads((certificate or root/'certificates/kneser_obstruction_transfer.json').read_text())
    assert data['schema']==1 and data['experiment']=='E068'
    assert data['obstruction_sha256']==hashlib.sha256((root/'certificates/mycielski_collision_refutation.json.gz').read_bytes()).hexdigest()
    verify_obstruction(root)
    edges=[]
    for i,j in combinations(range(11),2):
        if j==10:adjacent=i>=5
        elif j<5:adjacent=(j-i)%5 in (1,4)
        elif i<5:adjacent=(j-5-i)%5 in (1,4)
        else:adjacent=False
        if adjacent:edges.append((i,j))
    assert len(edges)==20
    assert [(m['n'],m['k']) for m in data['maps']]==[(6,2),(9,3)]
    for row in data['maps']:
        sets=row['sets'];assert len(sets)==11
        assert all(len(s)==row['k'] and len(set(s))==row['k'] and all(type(x) is int and 0<=x<row['n'] for x in s) for s in sets)
        assert all(set(sets[u]).isdisjoint(sets[v]) for u,v in edges)
    weights=data['independent_weight_numerators']
    assert weights==[3]*5+[2]*5+[4] and data['weight_denominator']==10
    independent=0
    for size in range(12):
        for subset in combinations(range(11),size):
            s=set(subset)
            if any(u in s and v in s for u,v in edges):continue
            independent+=1;assert sum(weights[v] for v in s)<=10
    assert independent==103 and sum(weights)==29
    # The next full graph is generated independently from its defining sets.
    subsets=[frozenset(s) for s in combinations(range(14),5)]
    edge_count=sum(a.isdisjoint(b) for a,b in combinations(subsets,2))
    assert len(subsets)==2002 and edge_count==126126
    return dict(status='PASS',theorem='T101',experiment='E068',checked_maps=2,
                independent_sets=independent,weight_bound='29/10',
                next_graph=dict(n=14,k=5,vertices=len(subsets),edges=edge_count),
                scope='Kneser obstruction transfer and limits of this filter; no unit realization or new HN bound')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
