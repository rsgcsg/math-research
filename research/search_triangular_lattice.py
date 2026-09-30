"""Search-only producer: finite eta closure, then complete triangular translations.
Floating embeddings only propose representatives; all reported contacts use exact
field arithmetic. A separate checker must certify representative floors and edges.
"""
import argparse, gzip, hashlib, json, math, time
from pathlib import Path
import numpy as np
from pysat.solvers import Solver
from verify_quintic_core_probe import RAD, multiplication_twice, product_twice, conjugate_twice, digest
from audit_full_law_preparation import canonical

def sqrt_mod(a,p):
 a%=p
 if a==0:return 0
 if pow(a,(p-1)//2,p)!=1:raise ValueError('not square')
 q=p-1;s=0
 while q%2==0:q//=2;s+=1
 z=2
 while pow(z,(p-1)//2,p)!=p-1:z+=1
 c=pow(z,q,p);x=pow(a,(q+1)//2,p);t=pow(a,q,p);m=s
 while t!=1:
  i=1;u=t*t%p
  while u!=1:u=u*u%p;i+=1
  b=pow(c,1<<(m-i-1),p);x=x*b%p;t=t*b*b%p;c=b*b%p;m=i
 return min(x,p-x)

def split(prime, table):
 e=next(pow(x,(prime-1)//5,prime) for x in range(2,prime) if pow(x,(prime-1)//5,prime)!=1)
 roots={r:sqrt_mod(r,prime) for r in (3,11,-1)};roots[5]=(2*(e+pow(e,-1,prime))+1)%prime
 field=[]
 for imag in range(2):
  for rad in RAD:
   x=roots[-1] if imag else 1
   for r in (3,5,11):
    if rad%r==0:x=x*roots[r]%prime
   field.append(x)
 imgs=field+[e*x%prime for x in field]
 assert all(sum(c*imgs[t] for t,c in row)%prime==2*imgs[i]*imgs[j]%prime for (i,j),row in table.items())
 bars=[sum(x*y for x,y in zip(conjugate_twice([int(i==j) for j in range(32)]),imgs))*pow(2,-1,prime)%prime for i in range(32)]
 return imgs,bars

def points_for(data,levels,table):
 d=data['denominator']*16;eta=[int(j==16) for j in range(32)]
 now=[tuple(x*16 for x in p) for p in data['points']];points=set(now)
 for _ in range(1,levels):
  new=[]
  for p in now:
   q=product_twice(eta,p,table);assert all(x%2==0 for x in q);new.append(tuple(x//2 for x in q))
  points.update(new);now=new
 gcd=math.gcd(d,*(x for p in points for x in p));return sorted(tuple(x//gcd for x in p) for p in points),d//gcd

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True);ap.add_argument('--levels',type=int,choices=range(1,6),default=1)
 ap.add_argument('--budget',type=int,default=50000);ap.add_argument('--slopes',default='2,3,4')
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);t0=time.monotonic()
 data=json.loads(gzip.decompress(a.cache.read_bytes()));h=hashlib.sha256(canonical(data)).hexdigest()
 assert h==json.loads((Path(__file__).resolve().parents[1]/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
 tab=multiplication_twice();pts,d=points_for(data,a.levels,tab)
 emb=np.array([complex(0,1)**imag*math.sqrt(r) for imag in range(2) for r in RAD]);eta=complex(math.cos(2*math.pi/5),math.sin(2*math.pi/5));emb=np.r_[emb,eta*emb]
 proposals=[]
 for p in pts:
  z=sum(x*y for x,y in zip(p,emb))/d;beta=2*z.imag/math.sqrt(3);alpha=z.real-z.imag/math.sqrt(3)
  # Proposal only. Snap close integral values; the independent checker uses exact arithmetic.
  def fl(x):return round(x) if abs(x-round(x))<1e-9 else math.floor(x)
  m,n=fl(alpha),fl(beta);q=list(p);q[0]-=d*m+d*n//2;q[9]-=d*n//2;proposals.append(tuple(q))
 Q=sorted(set(proposals));N=len(Q);assert d%2==0
 prime=10000741;imgs,bars=split(prime,tab);res=np.array([(sum(x*y for x,y in zip(q,imgs))%prime,sum(x*y for x,y in zip(q,bars))%prime) for q in Q],dtype=np.int64)
 sqrt=np.full(prime,-1,dtype=np.int32);xx=np.arange((prime+1)//2,dtype=np.int64);sqrt[xx*xx%prime]=xx;del xx
 omega=(imgs[0]+imgs[9])*pow(2,-1,prime)%prime;baromega=(bars[0]+bars[9])*pow(2,-1,prime)%prime
 inv=pow(2*d,-1,prime);target=[4*d*d]+[0]*31;gains=[(i,i,m,n) for i in range(N) for m,n in [(1,0),(0,1),(1,-1)]];cand=0
 for i in range(N):
  delta=res[i]-res[i+1:]
  for n in range(-2,3):
   x=(delta[:,0]-n*d*omega)%prime;y=(delta[:,1]-n*d*baromega)%prime;roots=sqrt[((x-y)*(x-y)+4*d*d)%prime]
   for sign in [1,-1]:
    ms=((x+y+sign*roots)*inv)%prime
    valid=np.flatnonzero((roots>=0)&((ms<=2)|(ms>=prime-2)))
    for v in valid:
     j=i+1+int(v);m=int(ms[v]);m=m if m<=2 else m-prime;cand+=1
     diff=[x-y for x,y in zip(Q[i],Q[j])];diff[0]-=d*m+d*n//2;diff[9]-=d*n//2
     if product_twice(diff,conjugate_twice(diff),tab)==target:gains.append((i,j,m,n))
  if i%3000==0:print('ROW',i,N,'contacts',len(gains),'elapsed',time.monotonic()-t0,flush=True)
 gains=sorted(set(gains));geom=dict(schema='mixed-triangular-contacts-v1',input_semantic_sha256=h,levels=a.levels,denominator=d,seed_points=len(pts),representatives=Q,gains=gains,representative_sha256=digest(Q),gain_sha256=digest(gains),proposal_prime=prime,proposal_candidates=cand)
 raw=bytearray(gzip.compress(json.dumps(geom,separators=(',',':')).encode(),mtime=0));raw[9]=255;(a.out/'contacts.json.gz').write_bytes(raw)
 print('GEOMETRY',len(pts),N,len(gains),'elapsed',time.monotonic()-t0,flush=True)
 for slope in map(int,a.slopes.split(',')):
  clauses=[]
  for i in range(N):
   choices=list(range(5*i+1,5*i+6));clauses.append(choices)
   for c in range(5):
    for e in range(c+1,5):clauses.append([-choices[c],-choices[e]])
  for i,j,m,n in gains:
   offset=(m+slope*n)%5
   for c in range(5):clauses.append([-5*i-c-1,-5*j-(c-offset)%5-1])
  clauses.append([1]);start=time.monotonic()
  with Solver(name='cadical195',bootstrap_with=clauses) as s:
   s.conf_budget(a.budget);ans=s.solve_limited();out=dict(schema='mixed-triangular-clock-v1',levels=a.levels,slope=slope,status='SAT_UNCHECKED' if ans else 'UNSAT_UNCERTIFIED' if ans is False else 'UNKNOWN_AFFINE_MODEL',budget=a.budget,stats=s.accum_stats(),seconds=time.monotonic()-start,representative_sha256=digest(Q),gain_sha256=digest(gains))
   if ans:
    model=set(s.get_model());w=''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(N));out['word']=w
    assert all(int(w[i])!=(int(w[j])+m+slope*n)%5 for i,j,m,n in gains)
  (a.out/f'slope{slope}.json').write_text(json.dumps(out,indent=2)+'\n');print('SOLVE',json.dumps({k:v for k,v in out.items() if k!='word'}),flush=True)
  del clauses
  if ans:break
if __name__=='__main__':main()
