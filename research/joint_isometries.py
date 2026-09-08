"""All maximal non-singleton partial isometries of a finite planar set.

An ordered pair of distinct anchors plus an orientation sign determines a
unique plane isometry. Equal squared distances to the two anchors determine
a point up to reflection; signed area selects the required side exactly.
"""
from collections import defaultdict
from itertools import combinations
from snail_geometry import sub, mul


def maximal_maps(points,distances):
    n=len(points)
    zero=tuple(0 for _ in points[0][0])
    def d(i,j):
        return zero if i==j else distances[tuple(sorted((i,j)))]
    signatures={}
    anchors=defaultdict(list)
    for i in range(n):
        for j in range(n):
            if i==j:
                continue
            anchors[d(i,j)].append((i,j))
            dx,dy=sub(points[j][0],points[i][0]),sub(points[j][1],points[i][1])
            sigs=[]
            for x in range(n):
                ux,uy=sub(points[x][0],points[i][0]),sub(points[x][1],points[i][1])
                area=sub(mul(dx,uy),mul(dy,ux))
                sigs.append((d(i,x),d(j,x),area))
            assert len(sigs)==len(set(sigs))
            signatures[i,j]=sigs
    maps=set()
    for i,j in combinations(range(n),2):
        for a,b in anchors[d(i,j)]:
            lookup={sig:x for x,sig in enumerate(signatures[a,b])}
            for orientation in (1,-1):
                pairs=[]
                for x,(di,dj,area) in enumerate(signatures[i,j]):
                    sig=di,dj,tuple(orientation*v for v in area)
                    if sig in lookup:
                        pairs.append((x,lookup[sig]))
                mapping=tuple(pairs)
                # Identity and inverse duplicates add no equations.
                if any(x!=y for x,y in mapping):
                    inverse=tuple(sorted((y,x) for x,y in mapping))
                    maps.add(min(mapping,inverse))
    return sorted(maps)


def pattern(coloring,indices):
    labels={}
    return tuple(labels.setdefault(coloring[v],len(labels)) for v in indices)


def distribution(colorings,weights,indices):
    result=defaultdict(int)
    for coloring,weight in zip(colorings,weights):
        result[pattern(coloring,indices)]+=weight
    return dict(result)
