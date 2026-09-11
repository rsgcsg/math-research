"""Check all collision branches by direct rational linear combinations; no elimination."""
from fractions import Fraction as Q
from pathlib import Path
import gzip
import json


def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    data=json.loads(gzip.decompress((certificate or root/'certificates/mycielski_collision_refutation.json.gz').read_bytes()))
    assert data['schema']==1 and data['experiment']=='E066' and data['vertices']==11
    edges=[]
    for i in range(11):
        for j in range(i+1,11):
            if j==10:yes=5<=i<10
            elif i<5 and j<5:yes=(j-i)%5 in (1,4)
            elif i<5<=j:yes=(j-5-i)%5 in (1,4)
            else:yes=False
            if yes:edges.append([i,j])
    assert len(edges)==20 and data['edges']==edges
    edge_set=set(map(tuple,edges));cycles=data['cycles']
    assert len(cycles)==10
    equations=[]
    for pairs in cycles:
        (a,c),(b,d)=pairs
        assert len({a,b,c,d})==4 and all(type(i) is int and 0<=i<11 for i in (a,b,c,d))
        assert all(tuple(sorted(e)) in edge_set for e in ((a,b),(b,c),(c,d),(d,a)))
        rows=[]
        for terms in (((a,1),(c,-1)),((b,1),(d,-1)),((a,1),(c,1),(b,-1),(d,-1))):
            r=[0]*11
            for i,v in terms:r[i]+=v
            rows.append(r)
        equations.append(rows)
    nodes=0;leaves=0;depth_max=0
    def check(node,path):
        nonlocal nodes,leaves,depth_max
        nodes+=1;depth_max=max(depth_max,len(path))
        if 'children' in node:
            assert set(node)=={'cycle','children'} and len(node['children'])==3
            c=node['cycle'];assert type(c) is int and 0<=c<len(equations)
            for child,row in zip(node['children'],equations[c]):check(child,path+[row])
        else:
            assert set(node)=={'edge','weights'}
            idx=node['edge'];assert type(idx) is int and 0<=idx<len(edges)
            weights=[Q(s) for s in node['weights']];assert len(weights)==len(path)
            a,b=edges[idx];target=[int(i==a)-int(i==b) for i in range(11)]
            assert all(sum(w*r[i] for w,r in zip(weights,path))==target[i] for i in range(11))
            leaves+=1
    check(data['tree'],[])
    assert nodes==data['nodes']==3208 and leaves==2139
    return dict(experiment='E066',vertices=11,listed_edges=20,branch_nodes=nodes-leaves,
                linear_identity_leaves=leaves,total_nodes=nodes,max_depth=depth_max,
                scope='No planar unit homomorphism of Groetzsch graph; no HN lower bound')


if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
