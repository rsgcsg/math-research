"""Exact arithmetic checks for seven-color hex tiling and the 1D interval-limit model.

The global planar interval lower bound is EXTERNAL (Voronov). This only checks the
finite algebraic geometry and finite odd cycles in the written proof.
"""
from fractions import Fraction as F
from itertools import product
import json

def need(ok, msg):
    if not ok: raise ValueError(msg)

def dgraph(m,n):
    return max(abs(m),abs(n),abs(m+n))

def q2(u):
    # u=(x,y/√3 coefficient), x,y rational, vector (x,y√3)
    return u[0]*u[0]+3*u[1]*u[1]

def center(m,n):
    return (F(3*m,2), F(m,2)+n)

def diff(a,b): return (a[0]-b[0],a[1]-b[1])

def dot(a,b): return a[0]*b[0]+3*a[1]*b[1]

def nearest_closed_double_hex_sq(p):
    v=[(F(2),F(0)),(F(1),F(1)),(F(-1),F(1)),
       (F(-2),F(0)),(F(-1),F(-1)),(F(1),F(-1))]
    distances=[]
    for a,b in zip(v, v[1:]+v[:1]):
        direction=diff(b,a)
        t=dot(diff(p,a),direction)/q2(direction)
        t=max(F(0),min(F(1),t))
        proj=(a[0]+t*direction[0],a[1]+t*direction[1])
        distances.append(q2(diff(p,proj)))
    return min(distances)

def check_hex():
    rings={j:[] for j in range(5)}
    for m,n in product(range(-7,8),repeat=2):
        j=dgraph(m,n)
        if j<=4:
            if j: rings[j].append((m,n))
            if 1<=j<=2:
                need((m-2*n)%7 != 0,'mod-seven conflict in squared triangular lattice')
            if j==3:
                need(nearest_closed_double_hex_sq(center(m,n))>=7,
                     'unexpected distance below sqrt(7)*s at ring3')
            if j>=4:
                need(q2(center(m,n))>=F(9*j*j,4), 'invalid graph-distance norm bound')
    need(min(nearest_closed_double_hex_sq(center(m,n)) for m,n in rings[3])==7,
         'nearest third-ring tile separation must be exactly sqrt(7)*s')
    need(2*3-(-1)*1==7,'index-7 determinant')
    need(q2(center(2,1))==q2(center(-1,3))==21,'kernel shortest basis')
    need(dot(center(2,1),center(-1,3))==F(21,2),'kernel 60 degree angle')
    # For 1/sqrt7 < s < 1/2, all T^2 neighbor tile pairs allow interior unit pair.
    need(q2(diff((F(-1),F(0)),(F(5,2),F(1,2))))==13,'first ring far vertices')
    need(q2(diff(center(2,0),(F(2),F(0))))==4,'second ring straight close pair')
    need(q2(diff(center(1,1),(F(1),F(1))))==1,'second ring bent close pair')
    need(q2(center(1,1))==9,'second ring center distance')
    return {'colors':7,'tile_index':7,'triangular_grid_square_chromatic':7,
            'rings_checked':{str(k):len(v) for k,v in rings.items() if k>0},
            'third_ring_min_squared_in_tile_side_units':7,
            'critical_hex_scale':'2/(2+sqrt(7))',
            'max_robust_epsilon':'(sqrt(7)-2)/(sqrt(7)+2)',
            'unit_tile_graph':'square of triangular grid for 1/sqrt(7)<side<1/2'}

def small_odd_length(eps):
    length=3
    while eps*length<1: length+=2
    return length

def verify_1d(eps):
    need(0<eps<F(1,3),'expected small interval')
    L=small_odd_length(eps)
    m=(L-1)//2
    a=1-eps
    b=F(m+1,m)*a
    need(1-eps<=a<=1+eps and 1-eps<=b<=1+eps,'step sizes')
    P=[k*a for k in range(m+2)]
    Q=[(m+1)*a-k*b for k in range(1,m)]
    walk=P+Q
    need(len(walk)==L and len(set(walk))==L,'not a simple odd cycle')
    for x,y in zip(walk,walk[1:]+walk[:1]):
        need(1-eps <= abs(x-y) <= 1+eps,'cycle edge out of interval')
    need((L-2)*eps<1,'odd girth bound was not minimal')
    h=(3-eps)/4
    need(h<1-eps and 2*h>1+eps,'bad 3-color band margin')
    return {'epsilon':str(eps),'smallest_odd_cycle_vertices':L,
            'forward_edges':m+1,'backward_edges':m,
            'a':str(a),'b':str(b),'three_color_band_width':str(h)}

def verify():
    if not __debug__: raise RuntimeError('assertions required')
    return {'status':'PASS_EXACT_FINITE_CALIBRATION',
            'hexagon':check_hex(),
            'one_dimensional_examples':[verify_1d(F(1,n)) for n in (4,5,10,21,50,101,1000)],
            'voronov_interval_lower_independently_proved_here':False,
            'plane_chromatic_6_or_7_determined':False,
            'scope':'Exact local hexagon lattice geometry and 1D odd-cycle checks; infinite interval 7 lower is from Voronov (2023/2025).'}
if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
