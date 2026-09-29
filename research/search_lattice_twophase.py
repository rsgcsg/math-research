"""Positive search beyond globally affine triangular-lattice color actions.
A positive word is a complete two-phase formula; failure is restricted only.
"""
from pathlib import Path
from itertools import combinations
import argparse,gzip,hashlib,json,time
from pysat.solvers import Solver

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--geometry',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--increments',default='1,0,2');p.add_argument('--budget',type=int,default=60000);p.add_argument('--period',type=int,default=2)
 a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);g=json.loads(gzip.decompress(a.geometry.read_bytes()));Q=g['representatives'];edges=g['gains'];N=len(Q);r=a.period
 for B in map(int,a.increments.split(',')):
  clauses=[]
  def var(i,s,c):return (i*r+s)*5+c+1
  for i in range(N):
   for s in range(r):
    vs=[var(i,s,c) for c in range(5)];clauses.append(vs)
    for x,y in combinations(vs,2):clauses.append([-x,-y])
  for i,j,m,n in edges:
   for s in range(r):
    wrap,t=divmod(s+n,r);d=(m+wrap*B)%5
    for c in range(5):clauses.append([-var(i,s,c),-var(j,t,(c-d)%5)])
  clauses.append([var(0,0,0)])
  t0=time.monotonic()
  with Solver(name='cadical195',bootstrap_with=clauses) as solver:
   solver.conf_budget(a.budget);ans=solver.solve_limited()
   out=dict(schema='mixed-triangular-multiphase-v1',levels=g['levels'],period=r,increment=B,
    representative_sha256=g['representative_sha256'],gain_sha256=g['gain_sha256'],
    variables=N*r*5,clauses=len(clauses),budget=a.budget,stats=solver.accum_stats(),seconds=time.monotonic()-t0,
    status='SAT_UNCHECKED' if ans else 'UNSAT_UNCERTIFIED' if ans is False else 'UNKNOWN_MULTIPHASE_MODEL')
   if ans:
    vals=set(solver.get_model());w=''.join(str(next(c for c in range(5) if var(i,s,c) in vals)) for i in range(N) for s in range(r));out['word']=w
    assert all(int(w[i*r+s])!=(int(w[j*r+(s+n)%r])+m+((s+n)//r)*B)%5 for i,j,m,n in edges for s in range(r))
    out['word_sha256']=hashlib.sha256(w.encode()).hexdigest()
  (a.out/f'period{r}-B{B}.json').write_text(json.dumps(out,indent=2)+'\n');print('RESULT',json.dumps({k:v for k,v in out.items() if k!='word'}),flush=True)
  del clauses
  if ans:break
if __name__=='__main__':main()
