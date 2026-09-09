"""Independent trace-sphere completeness and finite positive graph checker.

No SAT or search-module imports. All geometry uses gcd radical multiplication.
Sphere enumeration pairs (x,z) against (y,t), unlike the exporter's (x,y)/(z,t).
"""
from functools import lru_cache
from itertools import combinations,product
from pathlib import Path
from fractions import Fraction
import gzip
import hashlib
import json
import math

from verify_multicenter_cores import RAD, rotate_at, unit, split_projection
from verify_parts_core import verify_geometry

FREE={(0,0),(1,1),(0,8),(1,9)}


@lru_cache(None)
def integer_sphere(total,rx,ry,rz,rt,h):
    result=[]; sums={}
    # Plain bounded ranges followed by congruence tests avoid sharing the
    # exporter's congruent-range construction or its partition of the norm.
    for x in range(-math.isqrt(total),math.isqrt(total)+1):
        if x % (3*h) != rx:
            continue
        limit=math.isqrt((total-x*x)//13)
        for z in range(-limit,limit+1):
            if z % (3*h) == rz:
                sums.setdefault(x*x+13*z*z,[]).append((x,z))
    for y in range(-math.isqrt(total//3),math.isqrt(total//3)+1):
        if y % (3*h) != ry:
            continue
        limit=math.isqrt((total-3*y*y)//39)
        for t in range(-limit,limit+1):
            if t % h == rt:
                result.extend((x,y,z,t) for x,z in sums.get(total-3*y*y-39*t*t,()))
    return result


def to_center(A,B,h):
    m=(A-B)/(2*h);n=B/h
    if m.denominator != 1 or n.denominator != 1:
        return None
    return int(m),int(n)


def verify_quotient_observation(core,record,observation):
    kind=observation['center_code'];phases=9 if kind == 'm_n_mod3' else 3
    def index(sign,m,n,v):
        if phases == 9:
            state=3*(m % 3)+n % 3
        elif sign == 0:
            state=m % 3
        else:
            state=(n if kind == 'plus_m_minus_n_mod3' else m+n) % 3
        return 509*(1+phases*sign+state)+v
    edges={tuple(sorted((509*g+a,509*g+b))) for g in range(1+2*phases)
           for a,b in core['induced_edges']}
    for sign in (0,1):
        for m,n in product(range(3),repeat=2):
            edges.update(tuple(sorted((index(sign,m,n,v),index(sign,m+2,n+2,v)))) for v in range(509))
        edges.update(tuple(sorted((q,index(sign,m,n,v)))) for q,v,m,n in record['base_instances'])
    edges.update(tuple(sorted((index(0,m,n,q),index(1,a,b,v)))) for q,v,m,n,a,b in record['dual_instances'])
    equal=[(q,index(sign,m,n,v)) for sign in (0,1) for q,v,m,n in record['base_equal_instances']]
    equal += [(index(0,m,n,q),index(1,a,b,v)) for q,v,m,n,a,b in record['dual_equal_instances']]
    vertices=509*(1+2*phases)
    assert observation['quotient_variables'] == vertices
    assert observation['quotient_edges'] == len(edges)
    assert observation['equality_constraints'] == len(equal) == 549
    parent=list(range(vertices))
    def find(a):
        while a != parent[a]:
            parent[a]=parent[parent[a]];a=parent[a]
        return a
    for a,b in equal:
        parent[find(a)]=find(b)
    assert all(find(a) != find(b) for a,b in edges)
    assert observation['status'] == 'UNKNOWN' and observation['solver'] == 'cadical195'
    assert observation['conflict_budget'] == 500000


def verify_contacts(core,record):
    N=record['refinement']; assert N in (1,3);h=48//N;zero=((0,)*8,)*2
    base=[rotate_at(p,zero,0) for p in core['points']]
    plus=[rotate_at(p,zero,1) for p in core['points']]
    minus=[rotate_at(p,zero,-1) for p in core['points']]
    center=lambda m,n:((h*(2*m+n),)+(0,)*7,(0,h*n)+(0,)*6)
    direct=[[],[]]; equality=[[],[]]; budgets=[0,0]
    for q in range(509):
        X,Y=core['points'][q][0][0],core['points'][q][1][1]
        if all(a == 0 for j,axis in enumerate(core['points'][q]) for i,a in enumerate(axis)
               if (j,i) not in ((0,0),(1,1))):
            a=to_center(Fraction(X),Fraction(Y),h)
            if a is not None:
                equality[0].append((q,q,*a))
                assert base[q] == rotate_at(core['points'][q],center(*a),1)
        for r in range(509):
            U,V=core['points'][r][0][0],core['points'][r][1][1]
            fixed=sum(rad*(base[q][j][i]-plus[r][j][i])**2
                      for j in range(2) for i,rad in enumerate(RAD) if (j,i) not in FREE)
            remain=768**2-fixed-52*((X-U)**2+3*(Y-V)**2)
            if remain >= 0:
                budgets[0] += 1
                # Trace equation in center numerators, completed squares:
                # 12[(2A-X-U)^2+3(2B-Y-V)^2]=remain.
                if remain % 12 == 0:
                    radius=remain//12
                    for B in range(-math.isqrt(radius//3)-abs(Y+V)-1,
                                   math.isqrt(radius//3)+abs(Y+V)+2):
                        if B % h:
                            continue
                        residual=radius-3*(2*B-Y-V)**2
                        if residual < 0:
                            continue
                        s=math.isqrt(residual)
                        if s*s != residual:
                            continue
                        for sign_s in sorted({-s,s}):
                            a=to_center(Fraction(X+U+sign_s,2),Fraction(B),h)
                            if a is not None and unit(base[q],rotate_at(core['points'][r],center(*a),1),768):
                                direct[0].append((q,r,*a))
            fixed=sum(rad*(plus[q][j][i]-minus[r][j][i])**2
                      for j in range(2) for i,rad in enumerate(RAD) if (j,i) not in FREE)
            def centers_for(x,y,z,t):
                diffA=Fraction(x-5*(X-U),3);diffB=Fraction(y-5*(Y-V),3)
                sumA=Fraction(X+U-t);sumB=Fraction(Y+V)+Fraction(z,3)
                a=to_center((sumA+diffA)/2,(sumB+diffB)/2,h)
                b=to_center((sumA-diffA)/2,(sumB-diffB)/2,h)
                return None if a is None or b is None else (a,b)
            if fixed == 0:
                ab=centers_for(0,0,0,0)
                if ab is not None:
                    a,b=ab
                    assert rotate_at(core['points'][q],center(*a),1) == rotate_at(core['points'][r],center(*b),-1)
                    equality[1].append((q,r,*a,*b))
            if fixed > 768**2:
                continue
            budgets[1] += 1
            residues=(5*(X-U) % (3*h),5*(Y-V) % (3*h),-3*(Y+V) % (3*h),(X+U) % h)
            for values in integer_sphere(768**2-fixed,*residues,h):
                ab=centers_for(*values)
                if ab is None:
                    continue
                a,b=ab
                if unit(rotate_at(core['points'][q],center(*a),1),
                        rotate_at(core['points'][r],center(*b),-1),768):
                    direct[1].append((q,r,*a,*b))
        if q % 170 == 0:
            print(f'Independent trace spheres N={N}, core label {q}/509',flush=True)
    assert budgets == record['nonnegative_trace_budgets']
    for actual,key in zip(direct+equality,('base_instances','dual_instances','base_equal_instances','dual_equal_instances')):
        assert len(actual) == len(set(actual))
        assert sorted(actual) == list(map(tuple,record[key]))
    assert len(direct[0]) == record['base_unit_instances']
    assert len(direct[1]) == record['dual_unit_instances']
    for actual,key,wkey,dual in ((direct[0],'base_contacts','base_witnesses',False),
                                 (direct[1],'dual_contacts','dual_witnesses',True),
                                 (equality[0],'base_equalities','base_equality_witnesses',False),
                                 (equality[1],'dual_equalities','dual_equality_witnesses',True)):
        projected={(m % 3,q,a % 3,r) for q,r,m,n,a,b in actual} if dual else {(q,m % 3,r) for q,r,m,n in actual}
        assert sorted(projected) == list(map(tuple,record[key]))
        assert len(record[key]) == len(record[wkey])
        actual_set=set(actual)
        for edge,w in zip(record[key],record[wkey]):
            if dual:
                s,q,t,r=edge;a,b=w
                assert (q,r,*a,*b) in actual_set and a[0] % 3 == s and b[0] % 3 == t
            else:
                q,s,r=edge
                assert (q,r,*w) in actual_set and w[0] % 3 == s
    return direct,equality


def verify(root):
    core,edges=verify_geometry(root/'certificates/parts509_core.json')
    raw=(root/'certificates/parts509_core.json').read_bytes();sha=hashlib.sha256(raw).hexdigest()
    data=json.loads(gzip.decompress((root/'certificates/refined_center_arrays.json.gz').read_bytes()))
    assert data['schema'] == 1 and data['core_sha256'] == sha
    assert [c['refinement'] for c in data['cases']] == [1,3]
    # T060: all possible squared lattice lengths and rational square classes.
    lengths={m*m+m*n+n*n for m,n in product(range(-5,6),repeat=2)
             if 0 < m*m+m*n+n*n <= 14}
    assert lengths == {1,3,4,7,9,12,13}
    admitted=[]
    for k in sorted(lengths):
        discriminant=Fraction(576,k)-39
        if any((lambda x:math.isqrt(x.numerator)**2 == x.numerator and
                math.isqrt(x.denominator)**2 == x.denominator)(discriminant/r)
               for r in RAD[:8]):
            admitted.append(k)
    assert admitted == [9,12]
    points={tuple(map(tuple,p)) for p in core['points']}
    same_edges=[]
    for m,n in product(range(-5,6),repeat=2):
        k=m*m+m*n+n*n
        if k not in (9,12):
            continue
        # k=9: lambda=-1/4; k=12: lambda=3/4 must not occur.
        factor=-8 if k == 9 else 24
        d=((factor*m+factor*n//2,)+(0,)*7,(0,factor*n//2)+(0,)*6)
        assert all(tuple(tuple(a+b for a,b in zip(axis,delta)) for axis,delta in zip(p,d)) not in points
                   for p in points)
        if k == 9:
            assert m % 3 == n % 3 == 0
        else:
            assert m % 3 == n % 3 != 0
            same_edges.append((m,n))
    # Explicit three phase words: add phase in Z5 to any saved core coloring.
    words=[[ (color+s) % 5 for color in core['five_coloring']] for s in range(3)]
    assert all(word[a] != word[b] for word in words for a,b in edges)
    assert all(words[s][v] != words[(s+m)%3][v] for m,n in same_edges for s in range(3) for v in range(509))
    # C009: m-only code forces both displayed adjacent points to origin color.
    zero=((0,)*8,)*2
    center=lambda m,n:((32*m+16*n,)+(0,)*7,(0,16*n)+(0,)*6)
    assert rotate_at(zero,zero,1) == rotate_at(zero,zero,-1)
    assert unit(rotate_at(zero,center(0,-4),1),rotate_at(zero,center(0,1),-1),768)
    triangle=[rotate_at(zero,center(m,n),1) for m,n in ((0,0),(2,2),(-2,4))]
    assert all(unit(a,b,768) for a,b in combinations(triangle,2))
    reports=[]
    for case in data['cases']:
        direct,equality=verify_contacts(core,case)
        reports.append(dict(refinement=case['refinement'],unit_instances=list(map(len,direct)),
                            coincidences=list(map(len,equality))))
        if case['refinement'] == 1:
            previous=json.loads((root/'certificates/multicenter_cores.json').read_text())
            assert sorted({(q,r) for q,r,*_ in direct[0]}) == list(map(tuple,previous['single_array']['cross_edges']))
            assert sorted({(q,r) for q,r,*_ in direct[1]}) == list(map(tuple,previous['conjugate_array_contacts']['cross_edges']))
        else:
            # UNKNOWN is preserved as a search observation, never certified negative.
            assert case['coloring']['status'] == 'UNKNOWN'
            assert [s['center_code'] for s in case['asymmetric_searches']] == [
                'plus_m_minus_n_mod3','plus_m_minus_m_plus_n_mod3']
            assert all(s['status'] == 'UNKNOWN' and s['conflict_budget'] == 500000
                       for s in case['asymmetric_searches'])
            for observation in [case['coloring']]+case['asymmetric_searches']:
                verify_quotient_observation(core,case,observation)
    return dict(status='VERIFIED_REFINED_CENTER_GEOMETRY_AND_ONE_ORIENTATION_FIVE_COLORING',
                refinements=reports,one_orientation_infinite_chromatic_number=5,
                m_only_joint_code_impossible=True,nine_state_search='UNKNOWN',
                scope='Both-orientation infinite host undecided; no new plane bound')


def verify_finite(root):
    core,_=verify_geometry(root/'certificates/parts509_core.json')
    data=json.loads(gzip.decompress((root/'certificates/refined_center_finite.json.gz').read_bytes()))
    assert data['schema'] == 1 and data['core_sha256'] == hashlib.sha256((root/'certificates/parts509_core.json').read_bytes()).hexdigest()
    tri=[(0,0),(2,2),(-2,4)]
    specs=[[(0,0,0)]+[(m,n,1) for m,n in tri],
           [(0,0,0)]+[(m,n,s) for s in (1,-1) for m,n in tri],
           [(0,0,0)]+[(m,n,s) for s in (1,-1) for m,n in product(range(3),repeat=2)]]
    assert len(data['cases']) == 3
    prime,images=split_projection();target=768**2 % prime;report=[]
    for case,spec in zip(data['cases'],specs):
        assert list(map(tuple,case['copy_specifications'])) == spec
        pts=[];seen=set()
        for m,n,s in spec:
            center=((32*m+16*n,)+(0,)*7,(0,16*n)+(0,)*6)
            for p in core['points']:
                z=rotate_at(p,center,s)
                if z not in seen:
                    seen.add(z);pts.append(z)
        residues=[tuple(sum(a*b for a,b in zip(ax,images)) % prime for ax in p) for p in pts]
        edges=[]
        for i,(x,y) in enumerate(residues):
            for j,(u,v) in enumerate(residues[:i]):
                if ((x-u)**2+(y-v)**2) % prime == target and unit(pts[i],pts[j],768):
                    edges.append((j,i))
        edges.sort()
        assert len(pts) == case['vertices'] and len(edges) == case['edges']
        assert hashlib.sha256(json.dumps(edges,separators=(',',':')).encode()).hexdigest() == case['edge_sha256']
        word=case['five_coloring']
        assert case['status'] == 'SAT' and len(word) == len(pts) and set(word) <= set('01234')
        assert all(word[a] != word[b] for a,b in edges)
        report.append(dict(vertices=len(pts),edges=len(edges),pairs=math.comb(len(pts),2)))
        print(f'Independent refined finite graph verified: {len(pts)} points',flush=True)
    return dict(status='VERIFIED_REFINED_FINITE_INDUCED_FIVE_COLORINGS',cases=report)


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable assertions.')
    root=Path(__file__).resolve().parents[1]
    print(json.dumps(verify(root),indent=2))
    print(json.dumps(verify_finite(root),indent=2))
