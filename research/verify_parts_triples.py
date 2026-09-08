"""Independent three-port coverage verification using sets of witness indices.

The search keeps sets of covered third vertices. This checker instead constructs
the set of full-coloring witnesses realizing equality for each pair, then tests
every legal partition of every triple by Boolean intersections of witness sets.
"""
import gzip
import json
import math
from pathlib import Path
from verify_parts_core import verify_geometry, verify_coloring


def verify(root,edges=None):
    if edges is None:
        _,edges=verify_geometry(root/'certificates/parts509_core.json')
    data=json.loads(gzip.decompress((root/'certificates/parts509_triples.json.gz').read_bytes()))
    words=data['models']
    assert len(words)==len(set(words)) and words
    n=509
    color_models=[[0]*5 for _ in range(n)]
    for index,word in enumerate(words):
        colors=list(map(int,word))
        verify_coloring(colors,edges)
        bit=1<<index
        for v,c in enumerate(colors):
            color_models[v][c]|=bit
    equal=[[0]*n for _ in range(n)]
    adjacent=[[False]*n for _ in range(n)]
    for a,b in edges:
        adjacent[a][b]=adjacent[b][a]=True
    for a in range(n):
        for b in range(a+1,n):
            equal[a][b]=sum(color_models[a][c]&color_models[b][c] for c in range(5))
    all_models=(1<<len(words))-1
    monochromatic=two_blocks=distinct=0
    for a in range(n):
        for b in range(a+1,n):
            ab=equal[a][b]
            edge_ab=adjacent[a][b]
            for c in range(b+1,n):
                ac=equal[a][c];bc=equal[b][c]
                assert all_models&~(ab|ac|bc),(a,b,c,'all distinct')
                distinct+=1
                if not edge_ab:
                    assert ab&~ac,(a,b,c,'ab|c')
                    two_blocks+=1
                if not adjacent[a][c]:
                    assert ac&~ab,(a,b,c,'ac|b')
                    two_blocks+=1
                if not adjacent[b][c]:
                    assert bc&~ab,(a,b,c,'bc|a')
                    two_blocks+=1
                if not(edge_ab or adjacent[a][c] or adjacent[b][c]):
                    assert ab&ac,(a,b,c,'abc')
                    monochromatic+=1
        if a and a%100==0:
            print(f'Three-port independent verification: first vertex {a}/508',flush=True)
    assert distinct==math.comb(n,3)
    assert two_blocks==(math.comb(n,2)-len(edges))*(n-2)
    return dict(status='VERIFIED_ALL_THREE_PORT_PRECOLORINGS_EXTEND',
                vertices=n,colors=5,witness_colorings=len(words),
                vertex_triples=distinct,proper_monochromatic_patterns=monochromatic,
                proper_two_block_patterns=two_blocks,all_distinct_patterns=distinct,
                total_proper_partitions=monochromatic+two_blocks+distinct,
                graph_scope='induced Parts 509 graph, not arbitrary unit-distance graphs')


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
