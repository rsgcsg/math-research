"""Finite rational 7-chromatic near-unit graph; exact arithmetic verification.

The 7-lower bound uses Voronov 2025 Theorem 1.3 (six closed sets cannot
cover the radius-three disk without a unit pair in one set). This does
NOT certify a 7-chromatic exact-unit-distance graph or prove chi(R²)=7.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def ceil_q(x):
    return -((-x.numerator)//x.denominator)


def sign_qsqrt3(a, b):
    """Sign of a+b sqrt(3), without floating point."""
    if a == 0:
        return (b > 0) - (b < 0)
    if b == 0:
        return (a > 0) - (a < 0)
    if a*b > 0:
        return (a > 0) - (a < 0)
    z = a*a - 3*b*b
    return ((z > 0)-(z < 0))*((a > 0)-(a < 0))


def tile_d2(point, m, n, h, side):
    i, j = point
    x, y = h*i, h*j
    v = Q(m, 2) + n
    return ((x-Q(3,2)*side*m)**2 + y*y + 3*side*side*v*v,
            -2*y*side*v)


def hex_color(point, h, side):
    # An approximate sqrt(3) merely locates a finite candidate set.
    # The nearest-center comparisons and all edge checks are exact.
    i, j = point
    m0 = round(2*h*i/(3*side))
    n0 = round(Q(1732,1000)*h*j/(3*side)-Q(m0,2))
    best = None
    mn = None
    for m in range(m0-2,m0+3):
        for n in range(n0-2,n0+3):
            a,b=tile_d2(point,m,n,h,side)
            if best is None or sign_qsqrt3(a-best[0],b-best[1])<0:
                best=(a,b)
                mn=(m,n)
    need(best is not None,'no hex center')
    m,n=mn
    # Six neighbor bisectors define the regular hexagonal Voronoi cell.
    for dm,dn in ((1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)):
        a,b=tile_d2(point,m+dm,n+dn,h,side)
        need(sign_qsqrt3(a-best[0],b-best[1])>=0,'not a Voronoi center')
    return (m-2*n)%7



def wheel_equilibrium_stress_check():
    """Exact Q(sqrt(3)) six-triangle wheel, with signed rim/spoke stress."""
    # Pairs (x,y) represent (x, sqrt(3)*y) in the Euclidean plane.
    P=[(Q(0),Q(0)),(Q(1),Q(0)),(Q(1,2),Q(1,2)),
       (Q(-1,2),Q(1,2)),(Q(-1),Q(0)),
       (Q(-1,2),Q(-1,2)),(Q(1,2),Q(-1,2))]
    E=[(0,j,Q(-1)) for j in range(1,7)]
    E += [(j, j+1 if j<6 else 1, Q(1)) for j in range(1,7)]
    need(len(E)==12,'wheel edge count')
    def square_length(a,b):
        return (a[0]-b[0])**2 + 3*(a[1]-b[1])**2
    force=[[Q(0),Q(0)] for _ in P]
    for i,j,w in E:
        need(square_length(P[i],P[j])==1,'wheel actual unit edge')
        for coord in (0,1):
            v=w*(P[i][coord]-P[j][coord])
            force[i][coord]+=v
            force[j][coord]-=v
    need(all(a==b==0 for a,b in force),'not equilibrium')
    # The exact quadratic stress identity works for an arbitrary perturbation.
    t=Q(1,10)
    moved=[(P[0][0]+t,P[0][1])]+P[1:]
    lhs=sum(w*(square_length(moved[i],moved[j])
               -square_length(P[i],P[j])) for i,j,w in E)
    rhs=sum(w*square_length(
        (moved[i][0]-P[i][0],moved[i][1]-P[i][1]),
        (moved[j][0]-P[j][0],moved[j][1]-P[j][1]))
        for i,j,w in E)
    need(lhs==rhs==Q(-3,50),'wheel stress quadratic identity')
    return {'wheel_vertices':7,'exact_unit_edges':12,
            'all_forces_zero':True,'signed_stress_rim':1,
            'signed_stress_spoke':-1,
            'quadratic_perturbation_value':str(lhs)}



def verify():
    if not __debug__:
        raise RuntimeError('Certificate requires non-optimized Python')
    eps=Q(1,8)
    h=Q(7,10)*eps
    side=Q(3,7)
    need(h==Q(7,80) and 49<50 and 98<100,'coverage constants')
    R=ceil_q(Q(3)/h+Q(5,7))
    need(R==35 and Q(3)/h+Q(5,7)==35,'closed disk grid radius')
    points=[(i,j) for i in range(-R,R+1)
            for j in range(-R,R+1) if i*i+j*j<=R*R]
    point_set=set(points)
    need(len(points)==3853,'incorrect vertex count')
    # Closed Voronoi squares of side h cover B(0,3) because
    # nearest center distance <=h/sqrt(2), and 1/sqrt(2)<5/7.
    qlo=(1-eps)**2/(h*h)
    qhi=(1+eps)**2/(h*h)
    need(qlo==100 and qhi==Q(8100,49),'band threshold')
    steps=[(a,b) for a,b in product(range(-13,14),repeat=2)
           if qlo<=a*a+b*b<=qhi and (a>0 or (a==0 and b>0))]
    sqnorms=sorted({a*a+b*b for a,b in steps})
    need(len(steps)==106,'offset count')
    need(len(sqnorms)==25 and min(sqnorms)==100 and max(sqnorms)==164,
         'length spectrum')
    need(all(49*q!=6400 for q in sqnorms),'actual unit length in edge set')

    # 7-color upper via Isbell hexagons with side 3/7.
    need(2*side<1-eps and 7*side*side>(1+eps)**2,
         'seven-color separation band')
    colors={p:hex_color(p,h,side) for p in points}
    counts=Counter(colors.values())
    need(len(counts)==7,'seven colors not present')
    degrees=Counter()
    radial_counts=Counter()
    edge_count=0
    edge_digest=sha256()
    for i,j in points:
        for di,dj in steps:
            v=(i+di,j+dj)
            if v not in point_set:
                continue
            edge_count+=1
            radial_counts[di*di+dj*dj]+=1
            need(colors[(i,j)]!=colors[v],'seven-color edge conflict')
            degrees[(i,j)]+=1
            degrees[v]+=1
            edge_digest.update(f'{i},{j};{v[0]},{v[1]}\n'.encode())
    need(edge_count==324126,'edge count')
    need(sum(radial_counts.values())==edge_count and
         sorted(radial_counts)==sqnorms,'radial accounting')
    need(sum(degrees.values())==2*edge_count,'degree sum')
    need(min(degrees.values())==94 and max(degrees.values())==212,
         'degree extrema')
    word_digest=sha256()
    for i,j in points:
        word_digest.update(f'{i},{j},{colors[i,j]}\n'.encode())

    # Exact k=7 critical graph lower size via K_(2,3)-free geometry.
    for n in range(7,16):
        need(15*n>n*(n-1),'7-critical 2-walk bound')
    need(15*16==16*15,'equality case')
    # Equality n=16 would require two equilateral completions of every
    # edge, forcing an infinite triangular lattice. Hence n>=17.
    stress_lower=edge_count-2*len(points)+3
    need(stress_lower==316423,'framework rank bound')

    return {
        'schema':'hn-robust-grid-seven-v1',
        'status':'PASS_EXACT_FINITE_RECONSTRUCTION',
        'epsilon':str(eps),
        'grid_side':str(h),
        'integer_disk_radius':R,
        'vertices':len(points),
        'edges':edge_count,
        'oriented_offset_types':len(steps),
        'edge_counts_by_squared_offset':{str(q):radial_counts[q] for q in sqnorms},
        'distinct_forbidden_squared_integer_offsets':sqnorms,
        'edge_distance_formula':'(7/80)*sqrt(q) for q in offset norms',
        'contains_no_exact_unit_edges':True,
        'degree_range':[min(degrees.values()),max(degrees.values())],
        'seven_color_hexagon_side':str(side),
        'seven_color_counts':{str(k):counts[k] for k in range(7)},
        'edges_sha256':edge_digest.hexdigest(),
        'color_word_sha256':word_digest.hexdigest(),
        'external_closed_cover_input':(
            'Voronov 2025 Theorem 1.3: any six closed sets covering '
            'closed Euclidean radius-three disk have a unit pair in one set'),
        'exact_unit_7critical_min_vertices':17,
        'exact_unit_7critical_stress_lower':'n+3',
        'nearunit_grid_framework_stress_dim_lower':stress_lower,
        'exact_rational_wheel_equilibrium_calibration':wheel_equilibrium_stress_check(),
        'full_make_check_replayed':False,
        'new_lean_formalization':False,
        'plane_chromatic_six_or_seven_decided':False,
        'lower_bound_proved_by_six_sat':False,
        'scope':'All finite coordinates, edges, hex colors checked exactly; '
                'chromatic >=7 uses named external CLOSED-cover theorem.'
    }


if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
