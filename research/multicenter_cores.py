"""Exact full-graph search on multi-center, conjugate Parts rotations.

No boundary coloring is prescribed. Modular projection only rejects impossible
unit pairs; every surviving pair is squared in the multiquadratic field.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

from parts_core import clauses

RAD = (1, 3, 11, 33, 5, 15, 55, 165)
ALL_RAD = RAD + tuple(13*r for r in RAD)


def centers(den):
    zero = (0,)*8
    return [(zero, zero)] + [
        ((a*den//2,)+(0,)*7, (0,b*den//2)+(0,)*6)
        for a,b in ((2,0),(1,1),(-1,1),(-2,0),(-1,-1),(1,-1))]


def transform(point, center, sign):
    if sign == 0:
        return tuple(tuple(8*a for a in axis)+(0,)*8 for axis in point)
    x,y = [tuple(a-b for a,b in zip(axis,c)) for axis,c in zip(point,center)]
    axes = [list(5*a+8*b for a,b in zip(axis,c)) + [0]*8
            for axis,c in zip((x,y),center)]
    # R = (5 I +/- sqrt(39) J)/8.
    for i in range(8):
        j = (i ^ 1)+8
        factor = RAD[i & 1]
        axes[0][j] -= sign*factor*y[i]
        axes[1][j] += sign*factor*x[i]
    return tuple(map(tuple, axes))


def modular_data(prime=1009):
    # Choose a split prime by exact trial division and square-table tests.
    while True:
        if all(prime % d for d in range(2, int(prime**0.5)+1)):
            roots = {a*a % prime:a for a in range(prime)}
            if all(d in roots for d in (3,11,5,13)):
                generators = [roots[d] for d in (3,11,5,13)]
                images = [1]*16
                for mask in range(16):
                    for bit,g in enumerate(generators):
                        if mask & (1 << bit):
                            images[mask] = images[mask]*g % prime
                return prime, images
        prime += 1


def induced(points, den):
    prime, images = modular_data()
    residues = [tuple(sum(a*b for a,b in zip(axis,images)) % prime for axis in p)
                for p in points]
    target = den*den % prime
    edges=[]; survivors=0
    for j,(x,y) in enumerate(residues):
        for i,(u,v) in enumerate(residues[:j]):
            if ((x-u)**2+(y-v)**2) % prime != target:
                continue
            survivors += 1
            squared=[0]*16
            for a,b in zip(points[i],points[j]):
                delta=[c-d for c,d in zip(a,b)]
                nz=[(k,z) for k,z in enumerate(delta) if z]
                for k,z in nz:
                    squared[0] += z*z*ALL_RAD[k]
                for (k,z),(l,w) in combinations(nz,2):
                    squared[k ^ l] += 2*z*w*ALL_RAD[k & l]
            if squared == [den*den]+[0]*15:
                edges.append((i,j))
    return sorted(edges), survivors


def build(core, specifications):
    points=[]; index={}; copies=[]
    center_points=centers(core['coordinate_denominator'])
    for center,sign in specifications:
        ids=[]
        for point in core['points']:
            p=transform(point,center_points[center],sign)
            if p not in index:
                index[p]=len(points); points.append(p)
            ids.append(index[p])
        copies.append(ids)
    return points,copies


def infinite_array_quotient(core):
    """P plus all R(P-a)+a, a in the integer triangular lattice.

    The written proof reduces interactions with P to |a|^2 <= 196/3.
    Copy-copy contacts project to a unit difference or a quarter-unit
    difference. The latter are absent in this specific core.
    """
    from pysat.solvers import Solver
    den=core['coordinate_denominator']; target=(8*den)**2
    base=[transform(p,None,0) for p in core['points']]
    prime,images=modular_data()
    project=lambda p:tuple(sum(a*b for a,b in zip(axis,images)) % prime for axis in p)
    residues=[project(p) for p in base]
    edges=set(); identifications=set(); witnesses={}; total_contacts=0
    lattice=[(m,n) for m,n in product(range(-10,11),repeat=2)
             if 3*(m*m+m*n+n*n) <= 196]
    for m,n in lattice:
        a=((den*m+den*n//2,)+(0,)*7,(0,den*n//2)+(0,)*6)
        rotated=[transform(p,a,1) for p in core['points']]
        for q,point in enumerate(rotated):
            x,y=project(point)
            for p,(u,v) in enumerate(residues):
                if point == base[p]:
                    identifications.add((p,q))
                if ((x-u)**2+(y-v)**2) % prime != target % prime:
                    continue
                squared=[0]*16
                for pa,qa in zip(base[p],point):
                    nz=[(i,b-c) for i,(b,c) in enumerate(zip(pa,qa)) if b != c]
                    for i,b in nz:
                        for j,c in nz:
                            squared[i ^ j] += b*c*ALL_RAD[i & j]
                if squared == [target]+[0]*15:
                    total_contacts += 1
                    edges.add((p,q)); witnesses.setdefault((p,q),(m,n))
    cnf=clauses(1018,list(map(tuple,core['induced_edges']))+
                [(509+a,509+b) for a,b in core['induced_edges']]+
                [(p,509+q) for p,q in edges],5)
    for p,q in identifications:
        cnf.extend([-(5*p+c+1),5*(509+q)+c+1] for c in range(5))
    record=dict(lattice_centers_checked=len(lattice),cross_contact_instances=total_contacts,
                cross_edges=[list(e) for e in sorted(edges)],
                edge_center_witnesses=[list(witnesses[e]) for e in sorted(edges)],
                identifications=sorted(identifications))
    with Solver(name='cadical195',bootstrap_with=cnf) as solver:
        solver.conf_budget(500000)
        status=solver.solve_limited()
        record['status']='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'
        if status:
            model=set(solver.get_model())
            record['two_core_words']=[''.join(str(next(c for c in range(5)
                if 5*(509*g+v)+c+1 in model)) for v in range(509)) for g in range(2)]
    return record


def conjugate_array_contacts(core):
    """Finite exact cross interactions between the two infinite arrays.

    The written real-conjugate bound gives |a|, |b| < 10 for every
    cross-array unit pair or coincidence. Exact four-dimensional floor
    buckets (point and conjugate point) avoid a quadratic Cartesian scan.
    """
    den=8*core['coordinate_denominator']
    target=den*den
    lattice=[(m,n) for m,n in product(range(-12,13),repeat=2)
             if m*m+m*n+n*n <= 100]
    base_den=core['coordinate_denominator']
    center_points=[((base_den*m+base_den*n//2,)+(0,)*7,
                    (0,base_den*n//2)+(0,)*6) for m,n in lattice]
    zero=((0,)*8,)*2
    plus=[transform(p,zero,1) for p in core['points']]
    minus=[transform(p,zero,-1) for p in core['points']]
    shifts=[transform(zero,a,1) for a in center_points]
    conjugate=lambda p:tuple(tuple(axis[:8])+tuple(-x for x in axis[8:]) for axis in p)
    add=lambda p,q:tuple(tuple(a+b for a,b in zip(x,y)) for x,y in zip(p,q))
    scale=10**12
    low=[math.isqrt(r*scale*scale) for r in ALL_RAD]
    high=[a+(a*a != r*scale*scale) for a,r in zip(low,ALL_RAD)]
    def floor_axis(axis):
        if not any(axis[1:]):
            return axis[0]//den
        lower=sum(a*(l if a >= 0 else h) for a,l,h in zip(axis,low,high))
        upper=sum(a*(h if a >= 0 else l) for a,l,h in zip(axis,low,high))
        assert lower//(scale*den) == upper//(scale*den), 'Increase exact interval precision'
        return lower//(scale*den)
    key=lambda p:tuple(floor_axis(ax) for point in (p,conjugate(p)) for ax in point)
    prime,images=modular_data()
    residue=lambda p:tuple(sum(a*b for a,b in zip(ax,images)) % prime for ax in p)
    buckets={}
    for a,shift in enumerate(shifts):
        for q,p in enumerate(plus):
            point=add(p,shift)
            buckets.setdefault(key(point),[]).append((a,q,*residue(point)))
    offsets=list(product((-1,0,1),repeat=4))
    contacts=set(); equal=set(); witnesses={}; instances=0; candidates=0
    for b,shift in enumerate(shifts):
        conjugate_shift=conjugate(shift)
        for r,p in enumerate(minus):
            point=add(p,conjugate_shift); k=key(point); x,y=residue(point)
            for delta in offsets:
                for a,q,u,v in buckets.get(tuple(i+j for i,j in zip(k,delta)),()):
                    candidates += 1
                    norm=((x-u)**2+(y-v)**2) % prime
                    if norm != target % prime and (x != u or y != v):
                        continue
                    other=add(plus[q],shifts[a])
                    if other == point:
                        equal.add((q,r)); continue
                    squared=[0]*16
                    for ax,bx in zip(other,point):
                        nz=[(i,c-d) for i,(c,d) in enumerate(zip(ax,bx)) if c != d]
                        for i,c in nz:
                            for j,d in nz:
                                squared[i ^ j] += c*d*ALL_RAD[i & j]
                    if squared == [target]+[0]*15:
                        contacts.add((q,r)); instances += 1
                        witnesses.setdefault((q,r),(lattice[a],lattice[b]))
        if b % 60 == 0:
            print(json.dumps(dict(conjugate_centers_done=b,total=len(lattice),
                                  candidate_pairs=candidates,unit_instances=instances)),flush=True)
    return dict(lattice_centers_per_array=len(lattice),candidate_pairs=candidates,
                cross_contact_instances=instances,cross_edges=sorted(contacts),
                edge_center_witnesses=[witnesses[e] for e in sorted(contacts)],
                identifications=sorted(equal))


def solve_three_words(core,single,conjugate):
    from pysat.solvers import Solver
    edges=[(509*g+a,509*g+b) for g in range(3) for a,b in core['induced_edges']]
    edges += [(a,509*g+b) for g in (1,2) for a,b in single['cross_edges']]
    edges += [(509+a,1018+b) for a,b in conjugate['cross_edges']]
    equal=[(a,509*g+b) for g in (1,2) for a,b in single['identifications']]
    equal += [(509+a,1018+b) for a,b in conjugate['identifications']]
    cnf=clauses(1527,edges,5)
    for a,b in equal:
        cnf.extend([-(5*a+c+1),5*b+c+1] for c in range(5))
    with Solver(name='cadical195',bootstrap_with=cnf) as solver:
        solver.conf_budget(500000)
        status=solver.solve_limited()
        if status:
            model=set(solver.get_model())
            return dict(status='SAT',three_core_words=[''.join(str(next(c for c in range(5)
                if 5*(509*g+v)+c+1 in model)) for v in range(509)) for g in range(3)])
        return dict(status='UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN')


def five_edge_frame_obstruction(core,copies,edges):
    edge_set=set(edges); word=core['five_coloring']
    for color in range(5):
        examples={}
        for p,u in enumerate(copies[0]):
            if word[p] != color:
                continue
            for q,v in enumerate(copies[1]):
                if u != v and tuple(sorted((u,v))) in edge_set:
                    examples.setdefault(word[q],(p,q))
        if len(examples) == 5:
            return dict(status='FIVE_EDGE_FRAME_OBSTRUCTION',copy_pair=[0,1],
                        left_reference_color=color,
                        local_edges=[examples[c] for c in range(5)])
    raise AssertionError('No five-edge certificate found')


def run(root):
    from pysat.solvers import Solver
    raw=(root/'certificates/parts509_core.json').read_bytes()
    core=json.loads(raw)
    cases=[]
    specifications=[
        ('triangle_centers', [(0,0)]+[(i,1) for i in (0,1,2)]),
        ('wheel_centers', [(0,0)]+[(i,1) for i in range(7)]),
        ('conjugate_wheel_centers', [(0,0)]+[(i,s) for s in (1,-1) for i in range(7)])]
    for name,spec in specifications:
        points,copies=build(core,spec)
        edges,survivors=induced(points,8*core['coordinate_denominator'])
        within=set()
        for ids in copies:
            within.update(tuple(sorted((ids[u],ids[v]))) for u,v in core['induced_edges'])
        assert within <= set(edges)
        record=dict(name=name,copy_specifications=spec,vertices=len(points),
                    induced_edges=len(edges),additional_edges=len(set(edges)-within),
                    edge_sha256=hashlib.sha256(json.dumps(edges,separators=(',',':')).encode()).hexdigest(),
                    modular_survivors=survivors)
        print(json.dumps(record),flush=True)
        record['fixed_core_frame_test']=five_edge_frame_obstruction(core,copies,edges)
        with Solver(name='cadical195',bootstrap_with=clauses(len(points),edges,5)) as solver:
            solver.conf_budget(500000)
            status=solver.solve_limited()
            record['status']='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'
            if status:
                model=set(solver.get_model())
                colors=[next(c for c in range(5) if 5*v+c+1 in model) for v in range(len(points))]
                assert all(colors[u] != colors[v] for u,v in edges)
                record['five_coloring']=''.join(map(str,colors))
        print(json.dumps({k:v for k,v in record.items() if k != 'five_coloring'}),flush=True)
        cases.append(record)
    single=infinite_array_quotient(core)
    conjugate=conjugate_array_contacts(core)
    three=solve_three_words(core,single,conjugate)
    print(json.dumps(dict(single_array_status=single['status'],
                          conjugate_contact_types=len(conjugate['cross_edges']),
                          both_infinite_arrays_status=three['status'])),flush=True)
    return dict(schema=1,core_sha256=hashlib.sha256(raw).hexdigest(),cases=cases,
                single_array=single,conjugate_array_contacts=conjugate,
                both_arrays_coloring=three,
                scope='Specified finite graphs and the written infinite triangular-center array theorem; no whole number-field or plane coloring')


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    data=run(root)
    (root/'certificates/multicenter_cores.json').write_text(json.dumps(data,indent=2)+'\n')
