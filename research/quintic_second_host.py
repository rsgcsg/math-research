"""E049: build a genuinely new K-plane bridge through a T086 contact.

No fixed old coloring is imposed. Host inequality is a geometric filter,
not evidence that the induced graph is non-five-colorable.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
from quintic_core_probe import geometry,digest
from quintic_bridge_family import build
from quintic_bridge_contacts import coordinates,km,ki
from quintic_mixed_congruence_probe import product2,conjugate2,subtract
from quintic_congruence_probe import embedding,norm2


def multiply(a,b): return tuple(Q(x)/2 for x in product2(a,b))
def conjugate(a): return tuple(Q(x)/2 for x in conjugate2(a))
def add(a,b): return tuple(x+y for x,y in zip(a,b))


def setup(root):
    core,raw,_,old_ids,_,den,_=build(root)
    points=[tuple(Q(x,den) for x in p) for p in raw]
    old=[points[i] for i in old_ids]
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    a,b=old[84],old[337];u,v=base[332],base[451]
    inverse=(Q(3,2),Q(0),Q(0),Q(0),Q(3,10))+(Q(0),)*27
    r=multiply(multiply(subtract(b,a),conjugate(subtract(v,u))),inverse)
    translation=subtract(a,multiply(r,u))
    records=coordinates(root)
    contacts=json.loads((root/'certificates/quintic_bridge_contacts.json').read_text())
    interface={records[i][0]+records[i][1]+(Q(0),)*16 for i in contacts['inside']}
    candidate_pairs=[]
    for i,root_vector in contacts['roots']:
        root_vector=tuple(Q(x) for x in root_vector)
        ax,ay,bx,by,e,q=records[i]
        assert km(root_vector,root_vector)==q
        scale=km(root_vector,ki(e));dx=km(scale,by);dy=km(scale,bx)
        for sign in (-1,1):
            point=tuple(x-sign*y for x,y in zip(ax,dx))+tuple(x+sign*y for x,y in zip(ay,dy))+(Q(0),)*16
            interface.add(point)
            physical=add(translation,multiply(r,point))
            direction=subtract(physical,old[i])
            assert norm2(direction)==(Q(2),)+(Q(0),)*31
            candidate_pairs.append((i,sign,old[i],direction))
    points=sorted(set(points)|{add(translation,multiply(r,p)) for p in interface})
    zero=(Q(0),)*32;one=(Q(1),)+(Q(0),)*31;eta=zero[:16]+one[:16]
    known=[(zero,one)]+[(subtract(base[i],multiply(eta,base[i])),eta) for i in (0,153,150)]+[(translation,r)]
    def same_host(pose,other):
        c,d=pose;t,r0=other
        return not any(multiply(d,conjugate(r0))[16:]) and not any(multiply(subtract(c,t),conjugate(r0))[16:])
    novel=[]
    for i,sign,c,d in candidate_pairs:
        if any(same_host((c,d),p) for p in known):continue
        if any(same_host((c,d),(cc,dd)) for _,_,cc,dd in novel):continue
        novel.append((i,sign,c,d))
    return core,base,points,novel,known


def run(root,number=0,budget=100000,conic=False):
    from pysat.solvers import Solver
    core,base,baseline,novel,known=setup(root)
    print(json.dumps(dict(stage='hosts',new_hosts=len(novel),representatives=[[i,s] for i,s,c,d in novel],baseline_vertices=len(baseline))),flush=True)
    if conic:
        zero=(Q(0),)*8
        aa=(Q(13,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
        bb=(Q(-49,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
        c=add(base[64],aa+(Q(0),)*24)
        r=tuple(-x-y for x,y in zip(aa,bb))+zero+bb+zero
        assert norm2(r)==(Q(2),)+(Q(0),)*31
        baseline=sorted(set(baseline)|{add(c,r)})
        bridge=[add(c,p) for p in base]+[add(c,multiply(r,p)) for p in base]
        construction=dict(construction='non_torsion_conic')
    else:
        i,sign,c,r=novel[number]
        bridge=[add(c,multiply(r,p)) for p in base]
        construction=dict(construction='contact_bridge',selected_contact=[i,sign])
    all_q=baseline+bridge
    den=math.lcm(*(x.denominator for p in all_q for x in p))
    def integer(p):return tuple(int(x*den) for x in p)
    points=sorted({integer(p) for p in all_q});index={p:i for i,p in enumerate(points)}
    old_set={index[integer(p)] for p in baseline};bridge_set={index[integer(p)] for p in bridge}
    prime,images,bars=embedding(10**6)
    assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for u,v in combinations(range(len(points)),2):
        if ((residues[u][0]-residues[v][0])*(residues[u][1]-residues[v][1])-den*den)%prime:continue
        if norm2(subtract(points[u],points[v]))==(2*den*den,)+(0,)*31:edges.append((u,v))
    summary=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,induced_edges=len(edges),
                 baseline_vertices=len(old_set),overlap=len(old_set&bridge_set),
                 nonshared_cross_edges=sum(not(set(e)<=old_set or set(e)<=bridge_set) for e in edges),
                 point_sha256=digest(points),edge_sha256=digest(edges))
    print(json.dumps(dict(stage='geometry',**summary)),flush=True)
    clauses=[[5*v+c+1 for c in range(5)] for v in range(len(points))]
    clauses += [[-5*v-a-1,-5*v-b-1] for v in range(len(points)) for a,b in combinations(range(5),2)]
    clauses += [[-5*a-c-1,-5*b-c-1] for a,b in edges for c in range(5)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited()
        search=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',stats=solver.accum_stats(),conflict_budget=budget)
        if answer is True:
            model=set(x for x in solver.get_model() if x>0)
            search['five_coloring']=''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(len(points)))
    return dict(schema=1,experiment='E050' if conic else 'E049',sources={name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
               for name in ('parts509_core.json','quintic_core_probe.json','quintic_bridge_contacts.json')},
                **construction,coordinate_denominator=den,geometry=summary,search=search,
                scope='Specified finite induced graph; not the whole two-host union or full joint laws')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--number',type=int,default=0)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--conic',action='store_true')
    args=parser.parse_args()
    result=run(Path(__file__).resolve().parents[1],args.number,conic=args.conic)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result['search'].items() if k!='five_coloring'}))
