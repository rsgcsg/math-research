"""E058--E060: root changes and a moved pivot, with complete F interfaces."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse
import hashlib
import json
from quintic_independent_center import geometry
from quintic_second_host import multiply,conjugate,add
from quintic_bridge_contacts import km,square_roots
from quintic_shifted_spectrum import split_maps


def run(root):
    from pysat.solvers import Solver
    raw=(root/'certificates/parts509_core.json').read_bytes()
    P=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in json.loads(raw)['points']]
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    shifted=[tuple(x-y for x,y in zip(p,P[64])) for p in P]
    powers=[];rpower=one;blocks=[];neighbors=[];classifications=[]
    maps=split_maps()
    for j in range(1,5):
        rpower=multiply(rpower,eta);r=tuple(-x for x in rpower);powers.append(r)
        A=add(r,conjugate(r));qpoints=P+[add(A,p) for p in P]
        blocks.append([multiply(r,p) for p in qpoints])
        unit=[i for i,p in enumerate(P) if multiply(p,conjugate(p))==one]
        neighbors.append({i:[zero,multiply(A,P[i])] for i in unit})
        neighbors[-1][509]=[one,A]
        if j not in (1,2):continue
        c=tuple(x/2 for x in A[:8]);h=tuple(x-y for x,y in zip(one[:8],km(c,c)))
        negative=[];roots=[];inside=[]
        for i,p in enumerate(shifted):
            n=multiply(p,conjugate(p))[:8]
            if not any(n):inside.append(i);continue
            delta=km(n,tuple(x-y for x,y in zip(one[:8],km(h,n))))
            for m,(prime,f) in enumerate(maps):
                if any(x.denominator%prime==0 for x in delta):continue
                v=sum(x.numerator*pow(x.denominator,-1,prime)*y for x,y in zip(delta,f))%prime
                if pow(v,(prime-1)//2,prime)==prime-1:negative.append([i,m]);break
            else:
                rr=square_roots(delta);assert rr,('UNKNOWN',j,i)
                roots.append([i,[str(x) for x in rr[0]]])
        used=sorted({m for i,m in negative});remap={m:k for k,m in enumerate(used)}
        classifications.append(dict(power=j,inside=inside,nonsquare=[[i,remap[m]] for i,m in negative],
                                    roots=roots,maps=[maps[m] for m in used]))
    units=[i for i,p in enumerate(shifted) if multiply(p,conjugate(p))==one]
    assert all({i for i,rr in row['roots']}==set(units) for row in classifications)
    f=(1,5,0,0,4,9,0,0)
    def label(p):
        assert not any(p[16:]) and all(x.denominator%11 for x in p[:16])
        x,y=[sum(a.numerator*pow(a.denominator,-1,11)*b for a,b in zip(axis,f))%11 for axis in (p[:8],p[8:16])]
        return 11*x+y
    cases=[]
    for extra,offset in (((1,),0),((1,2,3,4),0),((1,),1)):
        anchor=one if offset else zero
        bs=blocks+[[add(anchor,multiply(powers[j-1],p)) for p in shifted] for j in extra]
        ns=neighbors+[{i:[anchor,add(anchor,multiply(add(powers[j-1],conjugate(powers[j-1])),shifted[i]))] for i in units} for j in extra]
        pts,ids,edges,den,summary=geometry(bs);n=len(pts)
        old=set(sum(ids[:4],[]));new=set(sum(ids[4:],[]))-old
        outside={i for i in new if any(pts[i][16:])}
        boundaries=[((set(ids[4+k])-old)&outside,set(sum([ids[h] for h in range(4) if h!=j-1],[]))-{ids[0][0]}) for k,j in enumerate(extra)]
        cross=sum(any((i in a and v in b) or (v in a and i in b) for a,b in boundaries) for i,v in edges)
        summary.update(new_vertices=len(new),new_outside_H=len(outside),overlap=len(set(sum(ids[4:],[]))&old),new_to_other_old_blocks=cross)
        contacts=sorted({(ids[b][i],n+label(p)) for b,nn in enumerate(ns) for i,pp in nn.items() for p in pp})
        interface={zero,anchor}|{p for nn in ns for pp in nn.values() for p in pp}
        target=[(n+i,n+j) for i,j in combinations(range(121),2) if ((i//11-j//11)**2+(i%11-j%11)**2)%11==1]
        clauses=[[5*v+k+1 for k in range(5)] for v in range(n+121)]
        clauses += [[-5*v-k-1,-5*v-l-1] for v in range(n+121) for k,l in combinations(range(5),2)]
        clauses += [[-5*i-k-1,-5*j-k-1] for i,j in edges+target+contacts for k in range(5)]
        origin=pts.index((0,)*32)
        clauses += [[s*(5*origin+k+1),-s*(5*n+k+1)] for k in range(5) for s in (-1,1)]
        for i,p in enumerate(pts):
            if not any(p[16:]):
                target_id=n+label(tuple(Q(x,den) for x in p))
                clauses += [[s*(5*i+k+1),-s*(5*target_id+k+1)] for k in range(5) for s in (-1,1)]
        with Solver(name='cd19',bootstrap_with=clauses) as solver:
            solver.conf_budget(100000);answer=solver.solve_limited()
            search=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY')
            if answer is True:
                model=set(solver.get_model());word=''.join(str(next(k for k in range(5) if 5*v+k+1 in model)) for v in range(n+121))
                search.update(right_word=word[:n],residue_word=word[n:])
        case=dict(extra_powers=list(extra),offset=offset,geometry=summary,denominator=den,interface_points=len(interface),contact_edges=len(contacts),search=search)
        cases.append(case);print(json.dumps({k:v for k,v in case.items() if k!='search'}),search['status'],flush=True)
    return dict(schema=1,experiments=['E058','E059','E060'],center=64,core_sha256=hashlib.sha256(raw).hexdigest(),
                predecessor_sha256=hashlib.sha256((root/'certificates/quintic_independent_center.json').read_bytes()).hexdigest(),
                classifications=classifications,cases=cases)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    data=run(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
