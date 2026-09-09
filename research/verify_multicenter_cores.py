"""Independent integer checker for finite and infinite Parts-center arrays.

No search imports or SAT dependency. Products use squarefree-radicand gcds.
Exact rational intervals, not floating coordinates, certify spatial rejection.
The infinite cutoff and same-orientation classification require the written
T058/T059 proof; this checks every finite obligation used there.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

from verify_parts_core import RADICANDS, verify_geometry

RAD = RADICANDS + tuple(13*r for r in RADICANDS)
PRODUCTS = {(i,j):(RAD.index(r*s//math.gcd(r,s)**2),2*math.gcd(r,s))
            for i,r in enumerate(RAD) for j,s in enumerate(RAD) if i < j}


def point_add(p,q):
    return tuple(tuple(a+b for a,b in zip(x,y)) for x,y in zip(p,q))


def conjugate(p):
    return tuple(tuple(a if i < 8 else -a for i,a in enumerate(axis)) for axis in p)


def rotate_at(point,center,sign):
    if sign == 0:
        return tuple(tuple(8*a for a in axis)+(0,)*8 for axis in point)
    x,y=point; u,v=center
    result=[list(5*a+3*b for a,b in zip(x,u))+[0]*8,
            list(5*a+3*b for a,b in zip(y,v))+[0]*8]
    for i,r in enumerate(RADICANDS):
        g=math.gcd(r,3)
        index=RAD.index(39*r//(g*g))
        result[0][index] -= sign*g*(y[i]-v[i])
        result[1][index] += sign*g*(x[i]-u[i])
    return tuple(map(tuple,result))


def unit(p,q,den):
    coefficients=[0]*16
    for x,y in zip(p,q):
        delta=[a-b for a,b in zip(x,y)]
        coefficients[0] += sum(a*a*r for a,r in zip(delta,RAD))
        for i,j in combinations((i for i,a in enumerate(delta) if a),2):
            k,factor=PRODUCTS[i,j]
            coefficients[k] += factor*delta[i]*delta[j]
    return coefficients == [den*den]+[0]*15


def split_projection():
    p=2029
    while True:
        if all(p % d for d in range(2,math.isqrt(p)+1)):
            roots={a*a % p:a for a in range(p)}
            if all(r in roots for r in (3,5,11,13)):
                images=[]
                for r in RAD:
                    image=1
                    for factor in (3,5,11,13):
                        if r % factor == 0:
                            image=image*roots[factor] % p
                    images.append(image)
                for i,r in enumerate(RAD):
                    for j,s in enumerate(RAD):
                        g=math.gcd(r,s); k=RAD.index(r*s//(g*g))
                        assert images[i]*images[j] % p == g*images[k] % p
                return p,images
        p += 1


def interval(axis,scale):
    lo=hi=0
    for a,r in zip(axis,RAD):
        lower=math.isqrt(r*scale*scale)
        upper=lower+(lower*lower != r*scale*scale)
        lo += a*(lower if a >= 0 else upper)
        hi += a*(upper if a >= 0 else lower)
    return lo,hi


def verify(root,geometry=None):
    raw=(root/'certificates/parts509_core.json').read_bytes()
    core,core_edges=geometry or verify_geometry(root/'certificates/parts509_core.json')
    data=json.loads((root/'certificates/multicenter_cores.json').read_text())
    assert data['schema'] == 1 and data['core_sha256'] == hashlib.sha256(raw).hexdigest()
    assert core['coordinate_denominator'] == 96 and 5*5+39 == 64
    den=768; prime,images=split_projection(); target=den*den % prime
    project=lambda p:tuple(sum(a*b for a,b in zip(axis,images)) % prime for axis in p)
    lattice_point=lambda m,n:((96*m+48*n,)+(0,)*7,(0,48*n)+(0,)*6)
    zero=lattice_point(0,0)
    center_ids=[(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]
    centers=[lattice_point(m,n) for m,n in center_ids]
    expected_specs=[[(0,0)]+[(i,1) for i in range(3)],
                    [(0,0)]+[(i,1) for i in range(7)],
                    [(0,0)]+[(i,s) for s in (1,-1) for i in range(7)]]
    assert len(data['cases']) == 3
    points=[]; point_ids={}; copies=[]
    for center,sign in expected_specs[-1]:
        ids=[]
        for p in core['points']:
            q=rotate_at(p,centers[center],sign)
            if q not in point_ids:
                point_ids[q]=len(points); points.append(q)
            ids.append(point_ids[q])
        assert len(set(ids)) == 509
        copies.append(ids)
    residues=list(map(project,points)); all_edges=[]; survivors=0
    for i,(x,y) in enumerate(residues):
        for j,(u,v) in enumerate(residues[:i]):
            if ((x-u)**2+(y-v)**2) % prime == target:
                survivors += 1
                if unit(points[i],points[j],den):
                    all_edges.append((j,i))
    all_edges.sort(); report=[]
    for case,spec in zip(data['cases'],expected_specs):
        assert list(map(tuple,case['copy_specifications'])) == spec
        count=max(max(ids) for ids in copies[:len(spec)])+1
        assert count == case['vertices']
        edges=[e for e in all_edges if e[1] < count]
        assert len(edges) == case['induced_edges']
        assert hashlib.sha256(json.dumps(edges,separators=(',',':')).encode()).hexdigest() == case['edge_sha256']
        within={tuple(sorted((ids[u],ids[v]))) for ids in copies[:len(spec)] for u,v in core_edges}
        assert within <= set(edges) and len(set(edges)-within) == case['additional_edges']
        word=case['five_coloring']
        assert case['status'] == 'SAT' and len(word) == count and set(word) <= set('01234')
        assert all(word[u] != word[v] for u,v in edges)
        frame=case['fixed_core_frame_test']
        assert frame['status'] == 'FIVE_EDGE_FRAME_OBSTRUCTION' and frame['copy_pair'] == [0,1]
        examples=frame['local_edges']; assert len(examples) == 5
        assert {core['five_coloring'][u] for u,v in examples} == {frame['left_reference_color']}
        assert {core['five_coloring'][v] for u,v in examples} == set(range(5))
        assert all(tuple(sorted((copies[0][u],copies[1][v]))) in set(edges) for u,v in examples)
        report.append(dict(vertices=count,edges=len(edges),additional_edges=case['additional_edges']))
    print('Independent finite multi-center graphs and five-edge frame obstruction verified',flush=True)

    # Strict |q|<3 for every core point, with rational radical enclosures.
    scale=10**6
    for p in core['points']:
        bounds=[max(map(abs,interval(tuple(axis)+(0,)*8,scale))) for axis in p]
        assert sum(b*b for b in bounds) < 9*(96*scale)**2
    # No quarter-lattice-unit differences: the only extra T058 edge type.
    scaled={tuple(tuple(4*a for a in axis) for axis in p) for p in core['points']}
    for p in core['points']:
        for w in centers[1:]:
            shifted=tuple(tuple(4*a+b for a,b in zip(axis,d)) for axis,d in zip(p,w))
            assert shifted not in scaled
    # An explicit scope boundary: w=(1,sqrt(3)/3) in Lambda/3 produces
    # an actual unit edge between the SAME local label at different centers.
    refined=((96,)+(0,)*7,(0,32)+(0,)*6)
    assert unit(rotate_at(zero,refined,1),rotate_at(zero,zero,0),den)

    # Enumerate the larger proved window for BOTH base-array and cross-array
    # relations. The exporter's base-array search uses the smaller 241 window.
    lattice=[(m,n) for m,n in product(range(-12,13),repeat=2) if m*m+m*n+n*n <= 100]
    assert len(lattice) == data['conjugate_array_contacts']['lattice_centers_per_array'] == 367
    assert sum(3*(m*m+m*n+n*n) <= 196 for m,n in lattice) == data['single_array']['lattice_centers_checked'] == 241
    shifts=[rotate_at(zero,lattice_point(m,n),1) for m,n in lattice]
    plus=[rotate_at(p,zero,1) for p in core['points']]
    base=[rotate_at(p,zero,0) for p in core['points']]
    minus=list(map(conjugate,plus))
    floor_scale=10**10
    bounds=[(math.isqrt(r*floor_scale**2),math.isqrt(r*floor_scale**2)+1) for r in RAD]
    bounds[0]=(floor_scale,floor_scale)
    def floor_axis(axis):
        if not any(axis[1:]):
            return axis[0]//den
        lower=sum(a*(l if a >= 0 else h) for a,(l,h) in zip(axis,bounds))
        upper=sum(a*(h if a >= 0 else l) for a,(l,h) in zip(axis,bounds))
        assert lower//(floor_scale*den) == upper//(floor_scale*den)
        return lower//(floor_scale*den)
    def cell(p):
        return tuple(floor_axis(axis) for z in (p,conjugate(p)) for axis in z)
    buckets={}
    for q,p in enumerate(base):
        buckets.setdefault(cell(p),[]).append((-1,q,*project(p)))
    for a,shift in enumerate(shifts):
        for q,p in enumerate(plus):
            point=point_add(p,shift)
            buckets.setdefault(cell(point),[]).append((a,q,*project(point)))
    offsets=list(product((-1,0,1),repeat=4))
    contacts=[set(),set()]; equal=[set(),set()]; instances=[0,0]; candidates=0
    for b,shift in enumerate(shifts):
        shift=conjugate(shift)
        for r,p in enumerate(minus):
            point=point_add(p,shift); k=cell(point); x,y=project(point)
            for delta in offsets:
                neighbor=tuple(i+j for i,j in zip(k,delta))
                for a,q,u,v in buckets.get(neighbor,()):
                    candidates += 1
                    norm=((x-u)**2+(y-v)**2) % prime
                    if norm != target and (x != u or y != v):
                        continue
                    group=int(a >= 0)
                    other=point_add(plus[q],shifts[a]) if group else base[q]
                    if point == other:
                        equal[group].add((q,r))
                    elif unit(point,other,den):
                        contacts[group].add((q,r)); instances[group] += 1
        if b % 90 == 0:
            print(f'Independent infinite-array contact window: {b}/{len(lattice)} centers',flush=True)
    for g,key in enumerate(('single_array','conjugate_array_contacts')):
        record=data[key]
        assert sorted(contacts[g]) == list(map(tuple,record['cross_edges']))
        assert sorted(equal[g]) == list(map(tuple,record['identifications']))
        assert instances[g] == record['cross_contact_instances']
        assert len(record['edge_center_witnesses']) == len(record['cross_edges'])
        for (q,r),w in zip(record['cross_edges'],record['edge_center_witnesses']):
            if g == 0:
                left=base[q]; right=rotate_at(core['points'][r],lattice_point(*w),1)
            else:
                left=rotate_at(core['points'][q],lattice_point(*w[0]),1)
                right=rotate_at(core['points'][r],lattice_point(*w[1]),-1)
            assert unit(left,right,den)
    single=data['single_array']; both=data['both_arrays_coloring']
    assert single['status'] == both['status'] == 'SAT'
    for words in (single['two_core_words'],both['three_core_words']):
        assert len(words) in (2,3)
        for word in words:
            assert len(word) == 509 and set(word) <= set('01234')
            assert all(word[a] != word[b] for a,b in core_edges)
        for word in words[1:]:
            assert all(words[0][a] != word[b] for a,b in contacts[0])
            assert all(words[0][a] == word[b] for a,b in equal[0])
        if len(words) == 3:
            assert all(words[1][a] != words[2][b] for a,b in contacts[1])
            assert all(words[1][a] == words[2][b] for a,b in equal[1])
    assert len(single['two_core_words']) == 2 and len(both['three_core_words']) == 3
    return dict(status='VERIFIED_MULTICENTER_FINITE_AND_INFINITE_ARRAY_OBLIGATIONS',
                finite_cases=report,finite_distinct_pairs=math.comb(len(points),2),
                quarter_direction_checks=6*509,core_radius_checks=509,
                third_lattice_same_label_unit_edge=True,
                array_centers_per_orientation=367,base_array_unit_instances=instances[0],
                conjugate_array_unit_instances=instances[1],
                contact_types=list(map(len,contacts)),coincidence_types=list(map(len,equal)),
                exact_bucket_candidate_pairs=candidates,
                scope='T058/T059 supply infinite completeness; five-color lower bound inherited from separately RUP-verified Parts core; no E^2 or plane coloring')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
