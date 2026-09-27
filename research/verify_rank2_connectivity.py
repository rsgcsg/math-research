"""Check a spanning tree and three generating walks in the certified gain graph."""
from collections import deque
import hashlib
import json
from pathlib import Path
from verify_rank2_rotation import read, verify


def check(host, certificate, raw):
    if not __debug__:raise RuntimeError('verification requires assertions')
    assert certificate['schema']=='rank2-connectivity-v1'
    assert hashlib.sha256(raw).hexdigest()==certificate['host_certificate_sha256']
    graph=host['graph'];contacts=graph['contacts'];n=len(graph['representatives'])
    root=certificate['root'];assert type(root) is int and root==0
    def edge(signed):
        assert type(signed) is int and 0<abs(signed)<=len(contacts)
        i,j,h,a,b=contacts[abs(signed)-1]
        return (i,j,(h,a,b)) if signed>0 else (j,i,(-h,-a,-b))
    tree=certificate['tree_edges'];assert len(tree)==n-1
    children=set();adj=[[] for _ in range(n)]
    for value in tree:
        i,j,g=edge(value);assert i!=j and j!=root and j not in children
        children.add(j);adj[i].append(j)
    seen={root};queue=deque([root])
    while queue:
        for v in adj[queue.popleft()]:
            assert v not in seen;seen.add(v);queue.append(v)
    assert len(seen)==n
    expected=[[1,0,0],[0,1,0],[0,0,1]];lengths=[]
    assert len(certificate['loops'])==3
    for row,want in zip(certificate['loops'],expected):
        assert row['gain']==want and all(type(x) is int for x in row['gain'])
        location=root;gain=[0,0,0]
        assert row['edges']
        for value in row['edges']:
            i,j,step=edge(value);assert location==i;location=j
            gain=[x+y for x,y in zip(gain,step)]
        gain[0]%=5
        assert location==root and gain==want
        lengths.append(len(row['edges']))
    assert graph['origin_neighbors']
    return dict(status='PASS',nonzero_orbits=n,spanning_tree_edges=len(tree),
                generating_loop_lengths=lengths,nonzero_infinite_host_connected=True,
                entire_infinite_host_connected=True,
                scope='Uses the separately verified complete contact table; no uniqueness of colorings is asserted.')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    verify(root,mutation_tests=False)
    path=root/'certificates/rank2_rotation_coloring.json.gz'
    result=check(read(path),read(root/'certificates/rank2_connectivity.json'),path.read_bytes())
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
