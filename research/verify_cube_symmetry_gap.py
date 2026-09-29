"""Exact rational unit-cube calibration: geometric symmetry is not graph EPPA.

No search package or prior HN certificate is imported. The finite calculations
check the explicit Q6 geometry, binary extension witnesses, distance-parity law,
and every integer used by the self-contained probability contradiction.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import hashlib
import json
import subprocess
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def norm2(p):
    return p[0]*p[0]+p[1]*p[1]


def parity(q):
    require(q.denominator % 2 == 1, 'even denominator')
    return q.numerator % 2


def run():
    params = (2,4,6,10,14,16)
    directions = [(F(m*m-1,m*m+1),F(2*m,m*m+1)) for m in params]
    require(all(norm2(v)==1 for v in directions),'direction length')
    points = [(sum((v[0] for j,v in enumerate(directions) if mask>>j&1),F(0)),
               sum((v[1] for j,v in enumerate(directions) if mask>>j&1),F(0)))
              for mask in range(64)]
    require(len(set(points))==64,'vertex collision')
    edges = []
    distances = {}
    colors = [mask.bit_count()%2 for mask in range(64)]
    for i in range(64):
        require(parity(points[i][0]+points[i][1])==colors[i],'vertex parity')
        for j in range(i+1,64):
            distance = norm2((points[i][0]-points[j][0],points[i][1]-points[j][1]))
            require(distance>0,'zero pair distance')
            require((distance==1)==((i^j).bit_count()==1),'induced unit cube mismatch')
            if distance==1:
                edges.append((i,j))
            require(parity(distance)==(colors[i]^colors[j]),'distance-parity identity')
            if distance in distances:
                require(distances[distance]==(colors[i]==colors[j]),'congruent pair mismatch')
            distances[distance] = colors[i]==colors[j]
    require(len(edges)==192,'edge count')
    adjacency = [set() for _ in range(64)]
    for i,j in edges:
        adjacency[i].add(j);adjacency[j].add(i)
    require(all(len(a)==6 for a in adjacency),'regular degree')
    f = [1 if not mask&1 else -1 for mask in range(64)]
    require(sum(f)==0,'character mean')
    require(all(sum(f[j] for j in adjacency[i])==4*f[i] for i in range(64)),
            'exact adjacency eigenvector')
    nonedges = comb(64,2)-len(edges)
    balanced = [13,13,13,13,12]
    minimum_same = sum(comb(a,2) for a in balanced)
    require(nonedges==1824 and minimum_same==378,'pigeonhole constants')
    # Exhaust all sorted class-size choices, not 5^64 assignments. Exchange
    # of a vertex between imbalanced classes proves the same bound in the text.
    minimum = comb(64,2)
    class_size_cases = 0
    def parts(total, count, low=0):
        if count==1:
            if total>=low:
                yield (total,)
            return
        for a in range(low,total//count+1):
            for tail in parts(total-a,count-1,a):
                yield (a,)+tail
    for sizes in parts(64,5):
        minimum = min(minimum,sum(comb(a,2) for a in sizes))
        class_size_cases += 1
    require(minimum==378,'class-size minimum')
    lower,upper = F(minimum,nonedges),F(1,5)
    require(lower==F(63,304) and lower>upper,'strict probability contradiction')
    # Every locally proper equality type has an explicit proper <=3 coloring.
    pair_witnesses = 0
    for i in range(64):
        for j in range(i+1,64):
            for same in (False,True):
                if same and j in adjacency[i]:
                    continue
                w = colors.copy()
                if same and w[i]!=w[j]:
                    w[i]=w[j]=2
                elif not same and w[i]==w[j]:
                    w[i]=2
                require((w[i]==w[j])==same,'pair requirement')
                require(all(w[a]!=w[b] for a,b in edges),'pair witness not proper')
                pair_witnesses += 1
    bad_source = norm2(points[3])
    bad_target = norm2(points[7])
    require(3 not in adjacency[0] and 7 not in adjacency[0],'nonedge map')
    require(bad_source!=bad_target and colors[3]!=colors[7],'nongeometric pair witness')
    encoded = [[str(x),str(y)] for x,y in points]
    digest = hashlib.sha256(json.dumps(encoded,separators=(',',':')).encode()).hexdigest()
    return dict(status='PASS', parameters=list(params),vertices=64,unit_edges=192,
                exact_pair_checks=2016,nonedges=nonedges,pair_extension_witnesses=pair_witnesses,
                class_size_cases=class_size_cases,minimum_same_pairs=minimum,
                probability_lower=str(lower),probability_upper=str(upper),
                ordinary_colors=2,geometric_joint_support=1,
                graph_partial_symmetry_five_law=False,points_sha256=digest,
                nongeometric_pair_map=dict(source=[0,3],target=[0,7],
                    source_squared_length=str(bad_source),target_squared_length=str(bad_target)),
                scope='Explicit induced rational planar Q6. Full Euclidean partial-isometry law exists; '
                      'a five-color law invariant under all abstract graph partial isomorphisms does not. '
                      'The latter is an intentionally stronger, invalid substitute for geometric symmetry. '
                      'No ordinary six-color lower bound.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    report = run()
    proc = subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],
                          text=True,capture_output=True,timeout=10)
    require(proc.returncode!=0 and 'requires assertions' in proc.stderr,'optimized mode accepted')
    report['optimized_mode_rejected'] = True
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
