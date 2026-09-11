"""E055--E057: fifth center, whole F interfaces, and four exceptional blocks."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
from quintic_second_host import multiply,conjugate,add
from quintic_mixed_congruence_probe import subtract
from quintic_congruence_probe import embedding,norm2
from quintic_core_probe import digest,solve
from quintic_bridge_contacts import km,ki,square_roots
from quintic_shifted_spectrum import split_maps


def geometry(copies_q):
    den=math.lcm(*(x.denominator for copy in copies_q for p in copy for x in p))
    raw=[[tuple(int(x*den) for x in p) for p in copy] for copy in copies_q]
    pts=sorted({p for copy in raw for p in copy});index={p:i for i,p in enumerate(pts)}
    copies=[[index[p] for p in copy] for copy in raw]
    prime,images,bars=embedding(10**6);assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in pts]
    edges=[]
    for i,j in combinations(range(len(pts)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        if norm2(subtract(pts[i],pts[j]))==(2*den*den,)+(0,)*31:edges.append((i,j))
    summary=dict(vertices=len(pts),actual_pairs=len(pts)*(len(pts)-1)//2,induced_edges=len(edges),
                 point_sha256=digest(pts),edge_sha256=digest(edges))
    return pts,copies,edges,den,summary


def case(root,sign,budget=100000):
    from pysat.solvers import Solver
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    r=tuple(-x for x in (multiply(eta,eta) if sign==1 else eta));A=add(r,conjugate(r));c=tuple(x/2 for x in A[:8])
    left=[base,[add(A,p) for p in base]];right=[[multiply(r,p) for p in copy] for copy in left]
    fifth=[add(base[64],p) for p in base]
    pts,copies,edges,den,summary=geometry(left+right+[fifth])
    old=set(sum(copies[:4],[]));new=set(copies[4]);left_ids=set(copies[0]+copies[1]);right_ids=set(copies[2]+copies[3])
    summary.update(fifth_overlap=len(old&new),fifth_cross_edges=sum(not(set(e)<=old or set(e)<=new) for e in edges),
                   new_fifth_to_right_edges=sum((i in new-old and j in right_ids-left_ids) or (j in new-old and i in right_ids-left_ids) for i,j in edges))
    finite=solve(pts,copies,edges,budget)
    print(json.dumps(dict(sign=sign,finite_geometry=summary,finite_status=finite['status'])),flush=True)
    qpoints=sorted(set(left[0]+left[1]));_,qcopies,qedges,qden,qsummary=geometry([qpoints])
    # Sorted rational and sorted integer orders agree because the scale is positive.
    assert qcopies==[list(range(len(qpoints)))]
    maps=split_maps();negative=[];roots=[];inside=[];neighbors={};h=tuple(x-y for x,y in zip(one[:8],km(c,c)))
    for i,p in enumerate(qpoints):
        n=tuple(x+y for x,y in zip(km(p[:8],p[:8]),km(p[8:16],p[8:16])))
        if not any(n):inside.append(i);continue
        delta=km(n,tuple(x-y for x,y in zip(one[:8],km(h,n))))
        for mi,(prime,f) in enumerate(maps):
            if any(x.denominator%prime==0 for x in delta):continue
            value=sum(x.numerator*pow(x.denominator,-1,prime)*y for x,y in zip(delta,f))%prime
            if pow(value,(prime-1)//2,prime)==prime-1:negative.append([i,mi]);break
        else:
            rr=square_roots(delta)
            assert rr,('UNKNOWN contact',sign,i)
            root_r=rr[0];roots.append([i,[str(x) for x in root_r]])
            neighbors[i]=[]
            for sgn in (-1,1):
                factor=tuple(x+sgn*y for x,y in zip(c,km(root_r,ki(n))))
                neighbors[i].append(km(factor,p[:8])+km(factor,p[8:16]))
    interface={zero[:16]}|{p for pair in neighbors.values() for p in pair}
    images=(1,5,0,0,4,9,0,0)
    def residue(p):
        assert all(x.denominator%11 for x in p)
        return tuple(sum(x.numerator*pow(x.denominator,-1,11)*y for x,y in zip(axis,images))%11 for axis in (p[:8],p[8:]))
    count=len(qpoints)
    contacts=sorted({(i,count+11*x+y) for i,pp in neighbors.items() for p in pp for x,y in [residue(p)]})
    target=[(count+i,count+j) for i,j in combinations(range(121),2) if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
    clauses=[[5*v+k+1 for k in range(5)] for v in range(count+121)]
    clauses += [[-5*v-k-1,-5*v-l-1] for v in range(count+121) for k,l in combinations(range(5),2)]
    clauses += [[-5*i-k-1,-5*j-k-1] for i,j in qedges+target+contacts for k in range(5)]
    clauses += [[s*(5*i+k+1),-s*(5*count+k+1)] for i in inside for k in range(5) for s in (-1,1)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited()
        search=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',stats=solver.accum_stats())
        if answer is True:
            model=set(solver.get_model());word=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(count+121))
            search.update(right_word=word[:count],residue_word=word[count:])
    used=sorted({m for i,m in negative});remap={m:j for j,m in enumerate(used)}
    contact=dict(q_geometry=qsummary,inside=inside,nonsquare=[[i,remap[m]] for i,m in negative],
                 roots=roots,maps=[maps[m] for m in used],interface_points=len(interface),contact_edges=len(contacts),search=search)
    print(json.dumps(dict(sign=sign,contact_counts=[len(negative),len(roots),len(interface),len(contacts)],extension=search['status'])),flush=True)
    return dict(sign=sign,coordinate_denominator=den,finite_geometry=summary,finite_search=finite,contacts=contact)


def orbit(root,cases,budget=100000):
    from pysat.solvers import Solver
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    eta_power=one;blocks=[];raw_contacts=[];raw_inside=[]
    f=(1,5,0,0,4,9,0,0)
    for power in (1,2,3,4):
        eta_power=multiply(eta_power,eta);r=tuple(-x for x in eta_power)
        A=add(r,conjugate(r));c=tuple(x/2 for x in A[:8])
        qpoints=sorted(set(base)|{add(A,p) for p in base})
        block=[multiply(r,p) for p in qpoints];blocks.append(block)
        source=next(item for item in cases if item['sign']==(1 if power in (2,3) else -1))['contacts']
        raw_inside.extend((power-1,i) for i in source['inside'])
        for i,rr in source['roots']:
            p=qpoints[i];root_r=tuple(Q(x) for x in rr)
            n=tuple(x+y for x,y in zip(km(p[:8],p[:8]),km(p[8:16],p[8:16])))
            for sgn in (-1,1):
                factor=tuple(x+sgn*y for x,y in zip(c,km(root_r,ki(n))))
                point=km(factor,p[:8])+km(factor,p[8:16])
                assert all(x.denominator%11 for x in point)
                x,y=[sum(a.numerator*pow(a.denominator,-1,11)*b for a,b in zip(axis,f))%11 for axis in (point[:8],point[8:])]
                raw_contacts.append((power-1,i,11*x+y))
    pts,ids,edges,den,summary=geometry(blocks);n=len(pts)
    contacts=sorted({(ids[block][i],n+label) for block,i,label in raw_contacts})
    inside=sorted({ids[block][i] for block,i in raw_inside});assert len(inside)==1
    target=[(n+i,n+j) for i,j in combinations(range(121),2) if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
    clauses=[[5*v+k+1 for k in range(5)] for v in range(n+121)]
    clauses += [[-5*v-k-1,-5*v-l-1] for v in range(n+121) for k,l in combinations(range(5),2)]
    clauses += [[-5*i-k-1,-5*j-k-1] for i,j in edges+target+contacts for k in range(5)]
    clauses += [[s*(5*i+k+1),-s*(5*n+k+1)] for i in inside for k in range(5) for s in (-1,1)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited()
        search=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',stats=solver.accum_stats())
        if answer is True:
            model=set(solver.get_model());word=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(n+121))
            search.update(right_word=word[:n],residue_word=word[n:])
    print(json.dumps(dict(orbit_geometry=summary,contacts=len(contacts),status=search['status'])),flush=True)
    return dict(experiment='E057',coordinate_denominator=den,geometry=summary,contact_edges=len(contacts),search=search)


def run(root):
    cases=[case(root,sign) for sign in (1,-1)]
    return dict(schema=1,experiments=['E055','E056','E057'],core_sha256=hashlib.sha256((root/'certificates/parts509_core.json').read_bytes()).hexdigest(),
                center=64,cases=cases,orbit=orbit(root,cases),
                scope='Finite fifth-copy probes and F union all four exceptional rotated blocks; not the whole E or full congruence laws')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=run(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
