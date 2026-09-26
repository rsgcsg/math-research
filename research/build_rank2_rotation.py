"""Rebuild the complete rank-two orbit graph using 32-dimensional algebra.

The saved word is an input witness, not a trusted conclusion. Default mode
reconstructs its graph and checks its infinite equivariant coloring. --search
optionally reruns the original first palette candidate with a bounded SAT
query. Restricted UNSAT or UNKNOWN never implies a whole-host obstruction.
The independent checker is verify_rank2_rotation.py (16-dimensional algebra).
"""
import argparse
from collections import defaultdict, Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json
import math
import time
from verify_quintic_tau_union import verify as source_geometry
from verify_quintic_core_probe import product_twice, conjugate_twice, digest
from verify_rotation_orbit_contacts import (
    _quadratic_roots, _root_tables, _split_map as split_map,
)
from rotation_orbit_coloring import perm_power


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def graph32(root, progress=False):
    if not __debug__: raise RuntimeError('Reconstruction requires assertions')
    start=time.monotonic()
    def log(**kw):
        if progress: print(json.dumps(dict(seconds=round(time.monotonic()-start,2),**kw)),flush=True)
    report,ctx=source_geometry(root,geometry_context=True)
    den=math.lcm(*(v.denominator for p in ctx['points'] for v in p))
    points=[tuple(int(x*den) for x in p) for p in ctx['points']]
    table=ctx['ring']['table'];source_edges=ctx['edges']
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    u=tuple(Q({0:1,4:-3,9:-1,13:-1}.get(i,0),8) for i in range(32))
    tau=tuple(Q({0:-1,10:3}.get(i,0),10) for i in range(32))
    mul=lambda a,b:tuple(Q(x)/2 for x in product_twice(a,b,table))
    conj=lambda a:tuple(Q(x)/2 for x in conjugate_twice(a))
    def powers(z,b):
     assert mul(z,conj(z))==one
     d={0:one}
     for j in range(1,b+1):d[j]=mul(d[j-1],z);d[-j]=mul(d[1-j],conj(z))
     return d
    hu=powers(eta,5);up=powers(u,9);tp=powers(tau,4)
    gains={(h,n,k):mul(mul(hu[h],up[n]),tp[k]) for h in range(5) for n in range(-9,10) for k in range(-4,5)}
    assert len(set(gains.values()))==855
    integer={}
    for g,z in gains.items():
     d=math.lcm(*(v.denominator for v in z));integer[g]=(tuple(int(x*d) for x in z),d)
    maps=[split_map(table,s) for s in (100001,200001)];factors=[];residues=[]
    for prime,images,bars in maps:
     ev=lambda a,b:sum(v.numerator*pow(v.denominator,-1,prime)*x for v,x in zip(a,b))%prime
     factors.append({g:(ev(z,images),ev(z,bars)) for g,z in gains.items()})
     residues.append([(sum(v*x for v,x in zip(p,images))*pow(den,-1,prime)%prime,sum(v*x for v,x in zip(p,bars))*pow(den,-1,prime)%prime) for p in points])
     assert all(a*b%prime==1 for a,b in factors[-1].values())
    log(stage='gains',primes=[x[0] for x in maps])
    lookup=defaultdict(list)
    for i,z in enumerate(residues[0]):
     if any(points[i]):lookup[z].append(i)
    parent=list(range(len(points)))
    def find(i):
     while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
     return i
    def join(a,b):
     a,b=find(a),find(b)
     if a!=b:parent[max(a,b)]=min(a,b)
    records=[];exact_eq=0;prime=maps[0][0]
    for (h,n,k),(a,b) in factors[0].items():
     if abs(n)>6 or abs(k)>2:continue
     coeff,d=integer[h,n,k]
     for i,(x,y) in enumerate(residues[0]):
      if i==4641:continue
      candidates=lookup.get((a*x%prime,b*y%prime),())
      if not candidates:continue
      transformed=product_twice(coeff,points[i],table);exact_eq+=1
      for j in candidates:
       if transformed==[2*d*v for v in points[j]]:records.append([i,j,h,n,k]);join(i,j)
    reps=sorted({find(i) for i in range(len(points)) if i!=4641});rep_set=set(reps);coords=[None]*len(points)
    for i,j,h,n,k in records:
     if i in rep_set:
      assert coords[j] in (None,[i,h,n,k]);coords[j]=[i,h,n,k]
    assert all(coords[i] and coords[i][0]==find(i) for i in range(len(points)) if i!=4641)
    assert len(records)==sum(v*v for v in Counter(find(i) for i in range(len(points)) if i!=4641).values())
    for i,j,h,n,k in records:
     a,ah,an,ak=coords[i];b,bh,bn,bk=coords[j]
     assert (a,(ah+h)%5,an+n,ak+k)==(b,bh,bn,bk)
    log(stage='equalities',orbits=len(reps),returns=len(records),exact=exact_eq)
    pr=maps[0][0];inv,sqrt=_root_tables(pr);r=[residues[0][i] for i in reps];s=[residues[1][i] for i in reps];norms=[a*b%pr for a,b in r]
    by_root=defaultdict(list)
    for g,(a,b) in factors[0].items():by_root[a].append(g)
    def canon(i,j,h,n,k):return min((i,j,h%5,n,k),(j,i,(-h)%5,-n,-k))
    contacts=set();exact=0;trans={};p2=maps[1][0];degenerate=0
    for i,(x,xb) in enumerate(r):
     for j in range(i,len(r)):
      y,yb=r[j];A=xb*y%pr;B=x*yb%pr;C=(norms[i]+norms[j]-1)%pr
      roots=_quadratic_roots(A,B,C,pr,inv,sqrt)
      if roots is None:possible=gains.keys();degenerate+=1
      else:possible=[g for z in roots for g in by_root.get(z,())]
      for h,n,k in possible:
       xi,xbi=s[i];yj,ybj=s[j];g,gb=factors[1][h,n,k]
       if ((xi-g*yj)*(xbi-gb*ybj)-1)%p2:continue
       ijh=canon(i,j,h,n,k)
       if ijh in contacts:continue
       coeff,d=integer[h,n,k];key=(j,h,n,k)
       if key not in trans:trans[key]=product_twice(coeff,points[reps[j]],table)
       delta=[2*d*v-z for v,z in zip(points[reps[i]],trans[key])];exact+=1
       if product_twice(delta,conjugate_twice(delta),table)==[4*(2*d*den)**2]+[0]*31:contacts.add(ijh)
     if i%400==0:log(stage='contacts',row=i,total=len(r),edges=len(contacts),exact=exact)
    origin=[i for i,a in enumerate(reps) if product_twice(points[a],conjugate_twice(points[a]),table)==[4*den*den]+[0]*31]
    contacts=[list(e) for e in sorted(contacts)];ri={x:i for i,x in enumerate(reps)};cs=set(map(tuple,contacts))
    for a,b in source_edges:
     if a==4641 or b==4641:
      v=b if a==4641 else a;assert ri[coords[v][0]] in origin
     else:
      ra,h,n,k=coords[a];rb,hb,nb,kb=coords[b];assert canon(ri[ra],ri[rb],hb-h,nb-n,kb-k) in cs
    out=dict(schema=1,geometry=report['geometry'],representatives=reps,coordinates=coords,contacts=contacts,origin_neighbors=origin,returns_sha256=digest(sorted(records)),returns_count=len(records),contact_sha256=digest(contacts),modular_primes=[p[0] for p in maps],exact_checks=exact,degenerate=degenerate)
    log(stage='complete',orbits=len(reps),contacts=len(contacts),origin=len(origin),by_tau=sorted(Counter(e[-1] for e in contacts).items()),selfs=[e for e in contacts if e[0]==e[1]])
    fields=('geometry','representatives','coordinates','contacts','origin_neighbors','returns_sha256','returns_count','contact_sha256')
    return {k:out[k] for k in fields}


def formula(graph):
    U=[0,2,3,1,4];var=lambda i,c:5*i+c+1;clauses=[]
    for i in range(len(graph['representatives'])):
        clauses.append([var(i,c) for c in range(5)])
        clauses.extend([-var(i,c),-var(i,d)] for c,d in combinations(range(5),2))
    clauses.extend([[-var(i,0)] for i in graph['origin_neighbors']])
    for i,j,h,n,k in graph['contacts']:
        P=perm_power(U,n)
        clauses.extend([-var(i,P[c]),-var(j,c)] for c in range(5))
    return clauses


def build(root, search=False, budget=30000, progress=False):
    graph=graph32(root,progress)
    saved=json.loads((root/'certificates/rank2_rotation_search.json').read_text())
    query=saved['queries'][0];clauses=formula(graph)
    assert digest(clauses)==query['formula_sha256']
    U=[0,2,3,1,4]
    if search:
        from pysat.solvers import Solver
        with Solver(name='cadical195',bootstrap_with=clauses) as solver:
            solver.conf_budget(budget);answer=solver.solve_limited()
            result=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'RESTRICTED_UNSAT_UNCERTIFIED',
                        stats=solver.accum_stats(),conflict_budget=budget,formula_sha256=digest(clauses))
            if answer is not True:return None,result
            model=set(x for x in solver.get_model() if x>0)
            word=''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(len(graph['representatives'])))
        result['word']=word
    else:
        word=query['word'];result=dict(status='SAVED_WORD_REBUILT',fresh_search_executed=False)
    assert isinstance(word,str) and len(word)==len(graph['representatives']) and set(word)<=set('01234')
    assert all(word[i]!='0' for i in graph['origin_neighbors'])
    assert all(int(word[i])!=perm_power(U,n)[int(word[j])] for i,j,h,n,k in graph['contacts'])
    cert=dict(schema='rank2-rotation-coloring-v1',source_commit='482b53020f36900ab2fcceff801ee2eb84893d94',
              canonical_result='T138/E110',graph=graph,
              coloring=dict(word=word,eta=list(range(5)),u=U,tau=list(range(5)),origin=0))
    return cert,result


def main():
    if not __debug__:raise RuntimeError('Reconstruction requires assertions')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search',action='store_true')
    parser.add_argument('--budget',type=int,default=30000)
    parser.add_argument('--progress',action='store_true')
    parser.add_argument('--output',type=Path,help='Optional certificate output; defaults to repository certificate')
    parser.add_argument('--result',type=Path,help='Optional query/rebuild result JSON')
    args=parser.parse_args()
    if args.budget<1:parser.error('--budget must be positive')
    root=Path(__file__).resolve().parents[1]
    certificate,result=build(root,args.search,args.budget,args.progress)
    if certificate is not None:
        output=args.output or root/'certificates/rank2_rotation_coloring.json.gz'
        raw=bytearray(gzip.compress(canonical(certificate),mtime=0));raw[9]=255
        output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(raw)
        result['certificate_sha256']=hashlib.sha256(raw).hexdigest()
    if args.result:
        args.result.parent.mkdir(parents=True,exist_ok=True)
        args.result.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if certificate is None:raise SystemExit(2)


if __name__=='__main__':main()
