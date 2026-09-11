"""E053: add an explicit new radius to couple two nontorsion F directions."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
import json
import math
from quintic_bridge_contacts import km
from quintic_second_host import multiply,conjugate,add
from quintic_mixed_congruence_probe import subtract
from quintic_congruence_probe import embedding,norm2
from quintic_core_probe import digest,solve,mechanisms


def poses():
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:]
    a=(Q(13,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
    b=(Q(-49,62),Q(0),Q(0),Q(0),Q(-3,62),Q(0),Q(0),Q(0))
    r=tuple(-x-y for x,y in zip(a,b))+zero[:8]+b+zero[:8]
    twice_c=add(r,conjugate(r));assert not any(twice_c[8:])
    return [(zero,one),(twice_c,one),(zero,r),(multiply(r,twice_c),r)]


def run(root,budget=100000):
    raw=(root/'certificates/parts509_core.json').read_bytes();core=json.loads(raw)
    base=[tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    occurrences=[[add(t,multiply(r,p)) for p in base] for t,r in poses()]
    den=math.lcm(*(x.denominator for copy in occurrences for p in copy for x in p))
    raw_copies=[[tuple(int(x*den) for x in p) for p in copy] for copy in occurrences]
    points=sorted({p for copy in raw_copies for p in copy});index={p:i for i,p in enumerate(points)}
    copies=[[index[p] for p in copy] for copy in raw_copies]
    prime,images,bars=embedding(10**6);assert den%prime
    residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    edges=[]
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-den*den)%prime:continue
        if norm2(subtract(points[i],points[j]))==(2*den*den,)+(0,)*31:edges.append((i,j))
    internal={tuple(sorted((copy[i],copy[j]))) for copy in copies for i,j in core['induced_edges']}
    first=set(copies[0]+copies[1]);second=set(copies[2]+copies[3])
    nonpivot_cross=[e for e in edges if not(set(e)<=first or set(e)<=second)]
    summary=dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,induced_edges=len(edges),
                 copy_edges=len(internal),extra_edges=len(set(edges)-internal),
                 host_intersection=sorted(first&second),nonpivot_cross_edges=len(nonpivot_cross),
                 point_sha256=digest(points),edge_sha256=digest(edges))
    search=solve(points,copies,edges,budget)
    mechanism=mechanisms(points,copies,edges,core)
    print(json.dumps(dict(geometry=summary,search={k:v for k,v in search.items() if k!='five_coloring'},mechanism=mechanism)),flush=True)
    return dict(schema=1,experiment='E053',core_sha256=hashlib.sha256(raw).hexdigest(),
                construction='P, 2c+P, rP, 2cr+rP; r from T087 and c=Re(r)',
                coordinate_denominator=den,geometry=summary,search=search,mechanism=mechanism,
                scope='Four specified Parts copies, all actual unit pairs; no infinite coloring or lower bound')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();data=run(Path(__file__).resolve().parents[1])
    if args.output:args.output.write_text(json.dumps(data,indent=2)+'\n')
