"""Search finite residue targets for entire translated K^2 sheets, not Parts copies."""
from itertools import combinations,product
from pathlib import Path
import argparse
import hashlib
import json

from parts_core import clauses

ROOT=Path(__file__).resolve().parents[1]


def graph(offset):
    points=list(product(range(2),range(11),range(11)));edges=[]
    for i,j in combinations(range(242),2):
        s,x,y=points[i];t,a,b=points[j]
        u,v=offset
        if (s==t and ((x-a)**2+(y-b)**2)%11==1) or (s!=t and ((x-a)%11,(y-b)%11) in ((u,v),(-u%11,-v%11))):
            edges.append((i,j))
    return edges


def build():
    from pysat.solvers import Solver
    records=[]
    offsets=[(0,r) for r in range(6)]+[(1,1),(1,4),(2,5),(2,2),(1,3)]
    for offset in offsets:
        edges=graph(offset)
        attempts=[]
        for pinned in (False,True):
            cnf=clauses(242,edges,5)
            if pinned:cnf += [[1],[5*11+2],[5*74+3]] # The actual unit triangle (0,0),(1,0),(6,8).
            with Solver(name='cadical195',bootstrap_with=cnf) as solver:
                solver.conf_budget(200000);status=solver.solve_limited()
                attempts.append(dict(pinned=pinned,status='SAT' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN'))
                record=dict(offset=offset,norm=sum(t*t for t in offset)%11,vertices=242,edges=len(edges),solver='cadical195',conflict_budget=200000,
                            status='SAT_CANDIDATE' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',attempts=attempts)
                if status:
                    model=set(solver.get_model())
                    record['word']=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(242))
            if status is not None:break
        records.append(record);print(json.dumps({k:v for k,v in record.items() if k!='word'}),flush=True)
    data=dict(schema=1,prime=11,cases=records,
                scope='Entire K^2 integer sheet stacks subject to stated height and integrality hypotheses; not the extension field or plane')
    if all(r['status']=='SAT_CANDIDATE' for r in records):data['finite_probe']=finite_probe(data)
    return data


def finite_probe(data):
    raw=(ROOT/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    points=[tuple(map(tuple,p)) for p in core['points']];ids={p:q for q,p in enumerate(points)}
    # Translation sqrt(6)/3 in x, cross displacement sqrt(3)/3 in y.
    cross=[]
    for q,(x,y) in enumerate(points):
        for sign in (-1,1):
            shift=list(y);shift[1]+=sign*32
            if (x,tuple(shift)) in ids:cross.append((q,ids[x,tuple(shift)]))
    edges={(509*n+q,509*n+r) for n in range(5) for q,r in core['induced_edges']}
    edges.update((509*n+q,509*(n+1)+r) for n in range(4) for q,r in cross)
    case=next(r for r in data['cases'] if r['norm']==4);assert case['offset']==(0,2)
    word=case['word'];images=(1,5,0,0,4,9,0,0);colors=[]
    for n in range(-2,3):
        for p in points:
            x,y=[sum(a*b for a,b in zip(ax,images))*pow(96,-1,11)%11 for ax in p]
            colors.append(int(word[121*(n%2)+11*(-x%11)+(-y%11)]))
    assert all(colors[a]!=colors[b] for a,b in edges)
    return dict(core_sha256=hashlib.sha256(raw).hexdigest(),layers=list(range(-2,3)),vertices=len(colors),
                edges=len(edges),cross_edges_per_interface=len(cross),word=''.join(map(str,colors)),
                edge_sha256=hashlib.sha256(json.dumps(sorted(edges),separators=(',',':')).encode()).hexdigest())


def triangular_probe():
    from pysat.solvers import Solver
    idx=lambda m,n,x,y:121*(2*(m%2)+n%2)+11*(x%11)+y%11
    edges=set()
    for m,n,x,y in product(range(2),range(2),range(11),range(11)):
        i=idx(m,n,x,y)
        for a,b in product(range(11),repeat=2):
            if (a*a+b*b)%11==1:edges.add(tuple(sorted((i,idx(m,n,x+a,y+b)))))
        for dm,dn,dx,dy in ((1,0,0,4),(0,1,1,2),(1,-1,10,2)):
            for sign in (1,-1):edges.add(tuple(sorted((i,idx(m+dm,n+dn,x+sign*dx,y+sign*dy)))))
    with Solver(name='cadical195',bootstrap_with=clauses(484,sorted(edges),5)) as solver:
        solver.conf_budget(200000);status=solver.solve_limited()
        result=dict(schema=1,vertices=484,edges=len(edges),conflict_budget=200000,solver='cadical195',
                    status='SAT_CANDIDATE' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                    scope='Parity quotient of K^2+(2sqrt(2)/3)Lambda only; no negative infinite claim')
        if status:
            model=set(solver.get_model())
            result['word']=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(484))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--triangular',action='store_true');args=parser.parse_args()
    data=triangular_probe() if args.triangular else build()
    name='translated_field_triangular.json' if args.triangular else 'translated_field_stack.json'
    (ROOT/'certificates'/name).write_text(json.dumps(data,indent=2)+'\n')
    if args.triangular:print(json.dumps(data),flush=True)
