"""Standalone integer checker for G27 full-partition distribution witnesses.

Does not import the search, its partial-isometry enumerator, or its field
arithmetic. Uses squared distances in Q(sqrt(33)) and three-anchor trilateration.
"""
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

# Original G27 manuscript coordinates in the basis 1,w,rho,w*rho.
COEFFS=[(1,4,2,0),(0,4,3,0),(2,3,0,1),(2,3,1,1),(1,3,2,1),
        (2,3,2,1),(1,4,2,1),(1,2,3,1),(1,3,3,1),(0,4,3,1),
        (3,3,0,2),(3,2,1,2),(1,3,1,2),(2,3,1,2),(2,2,2,2),
        (1,3,2,2),(0,2,3,2),(0,3,3,2),(0,2,4,2),(3,0,1,3),
        (2,1,1,3),(3,1,1,3),(1,1,2,3),(2,1,2,3),(1,2,2,3),
        (2,2,2,3),(3,1,0,4)]


def geometry():
    # 12*x = X0+X1*sqrt(33); 12*y = Y0*sqrt(3)+Y1*sqrt(11).
    pts=[(12*a+6*b+10*c+5*d,-d,6*b+5*d,2*c+d) for a,b,c,d in COEFFS]
    distances={}
    for i in range(27):
        for j in range(27):
            a,b,c,d=(x-y for x,y in zip(pts[i],pts[j]))
            distances[i,j]=(a*a+33*b*b+3*c*c+11*d*d,2*a*b+2*c*d)
    assert len(set(pts))==27
    edges=[(i,j) for i,j in combinations(range(27),2) if distances[i,j]==(144,0)]
    assert len(edges)==49
    return pts,distances,edges


def collinear(pts,i,j,k):
    a,b,c,d=(x-y for x,y in zip(pts[j],pts[i]))
    e,f,g,h=(x-y for x,y in zip(pts[k],pts[i]))
    # 144*oriented area = A*sqrt(3)+B*sqrt(11).
    return (a*g+11*b*h-c*e-11*d*f,a*h+3*b*g-d*e-3*c*f)==(0,0)


def all_test_maps(pts,d):
    """Cover every congruence by a checked map, with harmless redundant submaps."""
    pairs=defaultdict(list)
    pair_lookup={}
    for a in range(27):
        for b in range(27):
            if a==b:
                continue
            pairs[d[a,b]].append((a,b))
            lookup=defaultdict(list)
            for c in range(27):
                lookup[d[a,c],d[b,c]].append(c)
            pair_lookup[a,b]=lookup
    maps=set()
    def save(mapping):
        if any(a!=b for a,b in mapping):
            inv=tuple(sorted((b,a) for a,b in mapping))
            maps.add(min(tuple(mapping),inv))
    for i,j in combinations(range(27),2):
        line=[x for x in range(27) if collinear(pts,i,j,x)]
        for a,b in pairs[d[i,j]]:
            lookup=pair_lookup[a,b]
            # All collinear-domain congruences are restrictions of this map.
            line_map=[]
            for x in line:
                choices=lookup.get((d[i,x],d[j,x]),[])
                assert len(choices)<=1
                if choices:
                    line_map.append((x,choices[0]))
            save(line_map)
            # Every noncollinear domain has a sorted noncollinear triple.
            for k in range(j+1,27):
                if collinear(pts,i,j,k):
                    continue
                for c in lookup.get((d[i,k],d[j,k]),[]):
                    mapping=[]
                    for x in range(27):
                        choices=[y for y in lookup.get((d[i,x],d[j,x]),[]) if d[k,x]==d[c,y]]
                        assert len(choices)<=1
                        if choices:
                            mapping.append((x,choices[0]))
                    save(mapping)
    # Independent exact validation of every claimed partial isometry.
    for mapping in maps:
        assert len({b for a,b in mapping})==len(mapping)
        assert all(d[a,c]==d[b,e] for (a,b),(c,e) in combinations(mapping,2))
    return sorted(maps)


def restrict(blocks,indices):
    # Unlabelled partition encoded by membership masks on the ordered domain.
    return tuple(sorted(sum(1<<i for i,v in enumerate(indices) if block>>v&1)
                        for block in blocks if any(block>>v&1 for v in indices)))


def verify(path,interior=False):
    data=json.loads(Path(path).read_text())
    law=data['exact_kernel']['interior_witness'] if interior else data['witnesses'][-1]
    assert data['results'][-1]['stage']=='all_partial_isometry_full_partition_laws'
    weights=[F(item['weight']) for item in law]
    assert sum(weights)==1 and all(w>0 for w in weights)
    from math import lcm
    denominator=lcm(*(w.denominator for w in weights))
    integer_weights=[int(w*denominator) for w in weights]
    pts,d,edges=geometry()
    for item in law:
        blocks=item['blocks']
        assert len(blocks)==4 and all(type(b)==int and 0<b<1<<27 for b in blocks)
        assert sum(blocks)==(1<<27)-1
        assert all(a&b==0 for a,b in combinations(blocks,2))
        assert all(not(block>>a&1 and block>>b&1) for block in blocks for a,b in edges)
    if interior:
        tight=json.loads((Path(path).parent/'g27_replay.json').read_text())['tight_masks']
        assert len(tight)==len(set(tight))==168
        assert all(0<s<1<<27 and all(not(s>>a&1 and s>>b&1) for a,b in edges) for s in tight)
        expected=set()
        def cover(left,parts):
            if not left:
                expected.add(tuple(sorted(parts)))
                return
            if len(parts)==4:
                return
            bit=left&-left
            for s in tight:
                if s&bit and s&left==s:
                    cover(left^s,parts+[s])
        cover((1<<27)-1,[])
        supplied={tuple(sorted(item['blocks'])) for item in law}
        assert len(supplied)==len(law)==len(expected)==348 and supplied==expected
    maps=all_test_maps(pts,d)
    individual_failure=[None]*len(law)
    extremality_rows=[]
    for mapping in maps:
        left,right=zip(*mapping)
        lhs=defaultdict(int)
        rhs=defaultdict(int)
        for i,(item,weight) in enumerate(zip(law,integer_weights)):
            a,b=restrict(item['blocks'],left),restrict(item['blocks'],right)
            lhs[a]+=weight
            rhs[b]+=weight
            if a!=b and (individual_failure[i] is None or len(mapping)<len(individual_failure[i])):
                individual_failure[i]=mapping
        assert dict(lhs)==dict(rhs),mapping
        if not interior and len(extremality_rows)<2:
            for p in lhs:
                row=tuple(int(restrict(item['blocks'],left)==p)-int(restrict(item['blocks'],right)==p) for item in law)
                if not any(row):
                    continue
                if extremality_rows:
                    previous=extremality_rows[0]['row']
                    if all(row[i]*previous[j]==row[j]*previous[i] for i,j in combinations(range(3),2)):
                        continue
                extremality_rows.append(dict(mapping=mapping,pattern=p,row=row))
                if len(extremality_rows)==2:
                    break
    if not interior:
        assert all(m is not None for m in individual_failure)
        assert len(law)==3 and len(extremality_rows)==2
        assert all(sum(r['row'])==0 for r in extremality_rows)
    return dict(status='VERIFIED_FULL_PARTITION_INVARIANT_G27_LAW',
                vertices=27,induced_edges=len(edges),support_colorings=len(law),
                minimum_probability=str(min(weights)),denominator=denominator,
                congruence_maps_checked=len(maps),
                map_domain_sizes=dict(sorted(Counter(map(len,maps)).items())),
                individually_invariant_colorings=individual_failure.count(None),
                individual_failure_maps=individual_failure if not interior else 'omitted',
                extreme_three_atom_law_equations=extremality_rows if not interior else None,
                plane_coloring_claim=False)


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Do not disable assertions in an exact verifier.')
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--interior',action='store_true')
    args=parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1]/'certificates/joint_face_exact.json',args.interior),indent=2))
