"""Search the actual finite graph Y union (1+Y); independent replay is separate."""
import sys,json,gzip,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research'))
import numpy as np
from pysat.solvers import Solver
from full15_support_cnf import PackedClauses
from verify_quintic_core_probe import multiplication_twice,filter_map,product_twice,conjugate_twice,digest
import argparse
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
root=ROOT;data=json.loads(gzip.decompress(args.cache.read_bytes()));d=data['denominator'];start=time.monotonic()
base=[tuple(p) for p in data['points']];shift=[(p[0]+d,*p[1:]) for p in base];first=set(base);second=set(shift);points=sorted(first|second);ids={p:i for i,p in enumerate(points)}
copy0=[ids[p] for p in base];copy1=[ids[p] for p in shift]
edges={tuple(sorted((copy0[a],copy0[b]))) for a,b in data['edges']}|{tuple(sorted((copy1[a],copy1[b]))) for a,b in data['edges']}
table=multiplication_twice();prime,images,bars=filter_map(table)
residues=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
left=sorted(ids[p] for p in first-second);right=sorted(ids[p] for p in second-first)
ra=np.array([residues[j][0] for j in right],dtype=np.int64);rb=np.array([residues[j][1] for j in right],dtype=np.int64)
new=[];candidates=0
for i in left:
 a,b=residues[i];js=np.flatnonzero(((a-ra)*(b-rb)-d*d)%prime==0);candidates+=len(js)
 for k in js:
  j=right[int(k)];delta=[x-y for x,y in zip(points[i],points[j])]
  if product_twice(delta,conjugate_twice(delta),table)==[4*d*d]+[0]*31:
   edge=tuple(sorted((i,j)));edges.add(edge);new.append(edge)
edges=sorted(edges);print('GEOMETRY',len(points),len(edges),len(new),candidates,time.monotonic()-start,flush=True)
clauses=PackedClauses()
for i in range(len(points)):
 choices=list(range(5*i+1,5*i+6));clauses.append(choices)
 for a in range(5):
  for b in range(a+1,5):clauses.append([-choices[a],-choices[b]])
for a,b in edges:
 for c in range(5):clauses.append([-5*a-c-1,-5*b-c-1])
# Only one global color naming, on an actual triangle transported from Y.
for c,v in enumerate([4641,231,875]):clauses.append([5*copy0[v]+c+1])
with Solver(name='cadical195',bootstrap_with=clauses) as s:
 s.conf_budget(100000);ans=s.solve_limited();report=dict(status='UNKNOWN' if ans is None else 'UNSAT_UNCERTIFIED' if not ans else 'SAT_UNCHECKED',stats=s.accum_stats())
 if ans:
  model=set(s.get_model());word=''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(len(points)));assert all(word[a]!=word[b] for a,b in edges);report['word']=word
cert=dict(schema='actual-unit-translate-v1',base_commit='a885b67c172726e14884cb43cd37b965dbb32575',input_semantic_sha256='90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957',translation=[d]+[0]*31,denominator=d,geometry=dict(vertices=len(points),overlap=len(first&second),induced_edges=len(edges),new_cross_edges=len(new),point_sha256=digest(points),edge_sha256=digest(edges),cross_pairs_examined=len(left)*len(right)),search=report,scope='Exactly Y union (1+Y), not all integer translates or any invariant joint law.')
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(cert,indent=2)+'\n');print('RESULT',json.dumps({k:v for k,v in cert.items() if k!='search'}),report['status'],report['stats'],flush=True)
