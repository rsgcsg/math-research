"""Search exact center-dependent colorings, using positive trace spheres.

Centers are in Lambda/N; supported N divide 48. Search is NOT a verifier.
The complete geometry reduction is proved in refined_center_arrays.md.
"""
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import hashlib
import gzip
import json
import math

from multicenter_cores import ALL_RAD, transform, induced
from parts_core import clauses

FREE=((0,0),(1,1),(0,8),(1,9))
FIXED=[(a,i,r) for a in range(2) for i,r in enumerate(ALL_RAD) if (a,i) not in FREE]


def congruent_range(limit,residue,step):
    return range(-limit+(residue+limit) % step,limit+1,step)


@lru_cache(None)
def sphere(budget,residues,h):
    left={}
    for x in congruent_range(math.isqrt(budget),residues[0],3*h):
        for y in congruent_range(math.isqrt((budget-x*x)//3),residues[1],3*h):
            left.setdefault(x*x+3*y*y,[]).append((x,y))
    result=[]
    for z in congruent_range(math.isqrt(budget//13),residues[2],3*h):
        for t in congruent_range(math.isqrt((budget-13*z*z)//39),residues[3],h):
            rest=budget-13*z*z-39*t*t
            result.extend((x,y,z,t) for x,y in left.get(rest,()))
    return tuple(result)


@lru_cache(None)
def ellipse(budget,residues,h):
    if budget % 12:
        return ()
    radius=budget//12; result=[]
    for t in congruent_range(math.isqrt(radius//3),residues[1],2*h):
        rest=radius-3*t*t; z=math.isqrt(rest)
        if z*z != rest:
            continue
        result.extend((a,t) for a in sorted({-z,z}) if a % (2*h) == residues[0])
    return tuple(result)


def unit_delta(delta):
    squared=[0]*16
    for axis in delta:
        nz=[(i,a) for i,a in enumerate(axis) if a]
        for i,a in nz:
            squared[0] += a*a*ALL_RAD[i]
        for (i,a),(j,b) in combinations(nz,2):
            squared[i ^ j] += 2*a*b*ALL_RAD[i & j]
    return squared == [768**2]+[0]*15


def decode(x,y,z,t,X,Y,U,V,h):
    if (x-5*(X-U)) % 3 or (y-5*(Y-V)) % 3 or z % 3:
        return None
    sa=(x-5*(X-U))//3; sb=(y-5*(Y-V))//3
    ta=X+U-t; tb=Y+V+z//3
    if (sa+ta) % 2 or (sb+tb) % 2:
        return None
    A,C=(sa+ta)//2,(ta-sa)//2
    B,D=(sb+tb)//2,(tb-sb)//2
    if any(a % h or b % h or (a-b) % (2*h) for a,b in ((A,B),(C,D))):
        return None
    return ((A-B)//(2*h),B//h),((C-D)//(2*h),D//h)


def contacts(core,N):
    assert 48 % N == 0 and core['coordinate_denominator'] == 96
    h=48//N; zero=((0,)*8,)*2
    base=[transform(p,zero,0) for p in core['points']]
    plus=[transform(p,zero,1) for p in core['points']]
    minus=[transform(p,zero,-1) for p in core['points']]
    old={}; dual={}; old_equal={}; dual_equal={}; counts=[0,0]
    old_instances=[]; dual_instances=[]; old_equal_instances=[]; dual_equal_instances=[]
    rank_observations=[0,0]; center_sets=[set(),set()]
    for q in range(509):
        X,Y=core['points'][q][0][0],core['points'][q][1][1]
        if all(not a for axis in range(2) for i,a in enumerate(core['points'][q][axis])
               if (axis,i) not in ((0,0),(1,1))):
            if X % h == Y % h == 0 and (X-Y) % (2*h) == 0:
                m,n=(X-Y)//(2*h),Y//h
                old_equal[q,m % 3,q]=(m,n)
                old_equal_instances.append((q,q,m,n))
        for r in range(509):
            U,V=core['points'][r][0][0],core['points'][r][1][1]
            # Original q versus plus-copy r: two-variable positive ellipse.
            delta=[[a-b for a,b in zip(ax,bx)] for ax,bx in zip(base[q],plus[r])]
            budget=768**2-sum(rad*delta[a][i]**2 for a,i,rad in FIXED)
            budget -= 52*((X-U)**2+3*(Y-V)**2)
            if budget >= 0:
                rank_observations[0] += 1
                for z,t in ellipse(budget,(-(X+U) % (2*h),-(Y+V) % (2*h)),h):
                    A,B=(z+X+U)//2,(t+Y+V)//2
                    if A % h or B % h or (A-B) % (2*h):
                        continue
                    m,n=(A-B)//(2*h),B//h
                    delta[0][0]=8*X-5*U-3*A
                    delta[1][1]=8*Y-5*V-3*B
                    delta[0][8]=3*(V-B)
                    delta[1][9]=A-U
                    if unit_delta(delta):
                        counts[0] += 1; center_sets[0].add((m,n))
                        old_instances.append((q,r,m,n))
                        old.setdefault((q,m % 3,r),(m,n))
            # Plus-copy q versus minus-copy r: four-variable positive sphere.
            delta=[[a-b for a,b in zip(ax,bx)] for ax,bx in zip(plus[q],minus[r])]
            fixed=sum(rad*delta[a][i]**2 for a,i,rad in FIXED)
            budget=768**2-fixed
            if fixed == 0:
                centers=decode(0,0,0,0,X,Y,U,V,h)
                if centers is not None:
                    a,b=centers; dual_equal[a[0] % 3,q,b[0] % 3,r]=centers
                    dual_equal_instances.append((q,r,*a,*b))
            if budget < 0:
                continue
            rank_observations[1] += 1
            residues=(5*(X-U) % (3*h),5*(Y-V) % (3*h),-3*(Y+V) % (3*h),(X+U) % h)
            for values in sphere(budget,residues,h):
                centers=decode(*values,X,Y,U,V,h)
                if centers is None:
                    continue
                for (axis,i),value in zip(FREE,values):
                    delta[axis][i]=value
                if unit_delta(delta):
                    a,b=centers; counts[1] += 1; center_sets[1].update((a,b))
                    dual_instances.append((q,r,*a,*b))
                    dual.setdefault((a[0] % 3,q,b[0] % 3,r),centers)
    return dict(refinement=N,base_unit_instances=counts[0],dual_unit_instances=counts[1],
                base_contacts=sorted(old),base_witnesses=[old[e] for e in sorted(old)],
                dual_contacts=sorted(dual),dual_witnesses=[dual[e] for e in sorted(dual)],
                base_equalities=sorted(old_equal),base_equality_witnesses=[old_equal[e] for e in sorted(old_equal)],
                dual_equalities=sorted(dual_equal),dual_equality_witnesses=[dual_equal[e] for e in sorted(dual_equal)],
                nonnegative_trace_budgets=rank_observations,
                contact_center_counts=list(map(len,center_sets)),
                base_instances=sorted(old_instances),dual_instances=sorted(dual_instances),
                base_equal_instances=sorted(old_equal_instances),dual_equal_instances=sorted(dual_equal_instances))


def solve(core,record,full_phase=False,asymmetric=None):
    from pysat.solvers import Solver
    phases=9 if full_phase else 3
    def code(sign,m,n):
        if full_phase:
            return 3*(m % 3)+n % 3
        return (n+asymmetric*m) % 3 if sign == 1 and asymmetric is not None else m % 3
    index=lambda sign,phase,v:509*(1+phases*sign+phase)+v
    vertices=509*(1+2*phases)
    edges=set(tuple(sorted((509*g+a,509*g+b))) for g in range(1+2*phases) for a,b in core['induced_edges'])
    for sign in (0,1):
        edges.update(tuple(sorted((index(sign,code(sign,m,n),v),index(sign,code(sign,m+2,n+2),v))))
                     for m,n in product(range(3),repeat=2) for v in range(509))
        edges.update(tuple(sorted((q,index(sign,code(sign,m,n),r)))) for q,r,m,n in record['base_instances'])
    edges.update(tuple(sorted((index(0,code(0,m,n),q),index(1,code(1,a,b),r))))
                 for q,r,m,n,a,b in record['dual_instances'])
    equal=[(q,index(sign,code(sign,m,n),r)) for sign in (0,1) for q,r,m,n in record['base_equal_instances']]
    equal += [(index(0,code(0,m,n),q),index(1,code(1,a,b),r)) for q,r,m,n,a,b in record['dual_equal_instances']]
    cnf=clauses(vertices,sorted(edges),5)
    for a,b in equal:
        cnf.extend([-(5*a+c+1),5*b+c+1] for c in range(5))
    with Solver(name='cadical195',bootstrap_with=cnf) as solver:
        solver.conf_budget(500000)
        status=solver.solve_limited()
        result=dict(status='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                    quotient_variables=vertices,quotient_edges=len(edges),equality_constraints=len(equal),
                    center_code='m_n_mod3' if full_phase else 'm_mod3' if asymmetric is None
                                else 'plus_m_minus_n_mod3' if asymmetric == 0 else 'plus_m_minus_m_plus_n_mod3',
                    solver='cadical195',conflict_budget=500000)
        if status:
            model=set(solver.get_model())
            result['core_words']=[''.join(str(next(c for c in range(5)
                if 5*(509*g+v)+c+1 in model)) for v in range(509)) for g in range(1+2*phases)]
        return result


def run(root):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    records=[]
    for N in (1,3):
        record=contacts(core,N)
        print(json.dumps({k:v for k,v in record.items() if not isinstance(v,list) or k in
                         ('nonnegative_trace_budgets','contact_center_counts')}),flush=True)
        if N == 3:
            record['coloring']=solve(core,record,full_phase=True)
            print(json.dumps({k:v for k,v in record['coloring'].items() if k != 'core_words'}),flush=True)
            record['asymmetric_searches']=[solve(core,record,asymmetric=a) for a in (0,1)]
            print(json.dumps(record['asymmetric_searches']),flush=True)
        records.append(record)
    return dict(schema=1,core_sha256=hashlib.sha256(raw).hexdigest(),cases=records,
                scope='All centers of the specified Lambda/3 host only; periodic negative answers never imply an infinite obstruction')


def finite_probes(root):
    from pysat.solvers import Solver
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    triangle=[(0,0),(2,2),(-2,4)]
    cases=[]
    specifications=[('unit_center_triangle',[(0,0,0)]+[(m,n,1) for m,n in triangle]),
                    ('conjugate_center_triangle',[(0,0,0)]+[(m,n,s) for s in (1,-1) for m,n in triangle]),
                    ('conjugate_three_by_three',[(0,0,0)]+[(m,n,s) for s in (1,-1)
                                                        for m,n in product(range(3),repeat=2)])]
    for name,spec in specifications:
        points=[];ids={};copies=[]
        for m,n,sign in spec:
            center=((32*m+16*n,)+(0,)*7,(0,16*n)+(0,)*6)
            word=[]
            for p in core['points']:
                q=transform(p,center,sign)
                if q not in ids:
                    ids[q]=len(points);points.append(q)
                word.append(ids[q])
            copies.append(word)
        edges,_=induced(points,768)
        record=dict(name=name,copy_specifications=spec,vertices=len(points),edges=len(edges),
                    edge_sha256=hashlib.sha256(json.dumps(edges,separators=(',',':')).encode()).hexdigest())
        print(json.dumps(record),flush=True)
        with Solver(name='cadical195',bootstrap_with=clauses(len(points),edges,5)) as solver:
            solver.conf_budget(500000);status=solver.solve_limited()
            record['status']='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'
            if status:
                model=set(solver.get_model())
                colors=[next(c for c in range(5) if 5*v+c+1 in model) for v in range(len(points))]
                assert all(colors[a] != colors[b] for a,b in edges)
                record['five_coloring']=''.join(map(str,colors))
        print(record['name'],record['status'],flush=True);cases.append(record)
    return dict(schema=1,core_sha256=hashlib.sha256(raw).hexdigest(),cases=cases,
                scope='Only these three finite induced graphs; no inference of an infinite negative result')


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--finite-only',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    data=finite_probes(root) if args.finite_only else run(root)
    name='refined_center_finite.json.gz' if args.finite_only else 'refined_center_arrays.json.gz'
    (root/'certificates'/name).write_bytes(
        gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
