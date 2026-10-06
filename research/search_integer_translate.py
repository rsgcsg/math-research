"""Producer only: exact algebraic contacts and a restricted positive search.

The independent standard-library checker enumerates every contact again and
verifies the formula. A failed clock model has no ordinary coloring implication.
"""
import sys,json,gzip,time,math
from pathlib import Path
import numpy as np
def isprime(n):
 return n>=2 and all(n%j for j in range(2,math.isqrt(n)+1))
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
from pysat.solvers import Solver
from verify_quintic_core_probe import RAD,multiplication_twice,conjugate_twice,product_twice,digest
from legacy_full15_support_cnf import PackedClauses
def main():
 import argparse,hashlib
 from audit_full_law_preparation import canonical
 ap=argparse.ArgumentParser(description='Untrusted search for a clock coloring of every integer translate of Y.')
 ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True)
 ap.add_argument('--budget',type=int,default=100000)
 args=ap.parse_args();out=args.out_dir;out.mkdir(parents=True,exist_ok=True)
 data=json.loads(gzip.decompress(args.cache.read_bytes()))
 expected=json.loads((Path(__file__).resolve().parents[1]/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
 if hashlib.sha256(canonical(data)).hexdigest()!=expected:raise ValueError('input cache binding')
 d=data['denominator'];start=time.monotonic()
 Q=sorted({(p[0]%d,*p[1:]) for p in data['points']});N=len(Q)
 B=max((sum(abs(x)*(math.isqrt(RAD[j%8])+(math.isqrt(RAD[j%8])**2<RAD[j%8])) for j,x in enumerate(p))+d-1)//d for p in Q);M=2*B+1
 p=10000001
 while not (p%20==1 and isprime(p) and all(pow(r,(p-1)//2,p)==1 for r in (3,11))):p+=20
 eta=next(pow(x,(p-1)//5,p) for x in range(2,100) if pow(x,(p-1)//5,p)!=1)
 roots={r:int(sqrt_mod(r,p)) for r in (3,11,-1)};roots[5]=(2*(eta+pow(eta,-1,p))+1)%p
 field=[]
 for imag in range(2):
  for rad in RAD:
   x=roots[-1] if imag else 1
   for r in (3,5,11):
    if rad%r==0:x=x*roots[r]%p
   field.append(x)
 images=field+[eta*x%p for x in field];tab=multiplication_twice();bars=[]
 for i in range(32):bars.append(sum(a*b for a,b in zip(conjugate_twice([int(i==j) for j in range(32)]),images))*pow(2,-1,p)%p)
 assert all(sum(c*images[k] for k,c in row)%p==2*images[i]*images[j]%p for (i,j),row in tab.items())
 res=np.array([(sum(a*b for a,b in zip(q,images))%p,sum(a*b for a,b in zip(q,bars))%p) for q in Q],dtype=np.int64)
 sqrt=np.full(p,-1,dtype=np.int32);xx=np.arange((p+1)//2,dtype=np.int64);sqrt[(xx*xx)%p]=xx;del xx
 invd=pow(2*d,-1,p);gains=[(i,i,1) for i in range(N)];candidates=0
 for i in range(N):
  dx=res[i,0]-res[i+1:,0];dy=res[i,1]-res[i+1:,1];rr=sqrt[((dx-dy)**2+4*d*d)%p]
  for sign in (1,-1):
   ns=((dx+dy+sign*rr)*invd)%p;valid=np.flatnonzero((rr>=0)&((ns<=M)|(ns>=p-M)))
   for v in valid:
    j=i+1+int(v);n=int(ns[v]);n=n if n<=M else n-p;candidates+=1
    delta=[x-y for x,y in zip(Q[i],Q[j])];delta[0]-=n*d
    if product_twice(delta,conjugate_twice(delta),tab)==[4*d*d]+[0]*31:gains.append((i,j,n))
  if i%2000==0:print('ROWS',i,'gains',len(gains),flush=True)
 gains=sorted(set(gains));geometry=dict(N=N,bound=B,offset_bound=M,prime=p,images=images,bars=bars,gains=gains,q_sha256=digest(Q),gain_sha256=digest(gains),candidates=candidates,seconds=time.monotonic()-start)
 (out/'integer-strip-gains.json').write_text(json.dumps(geometry,separators=(',',':'))+'\n');print('COMPILED',N,len(gains),M,time.monotonic()-start,flush=True)
 geometry.update(schema='integer-translate-kernel-v1',input_semantic_sha256=expected,denominator=d)
 raw=bytearray(gzip.compress((json.dumps(geometry,separators=(',',':'))+'\n').encode(),mtime=0));raw[9]=255
 (out/'integer_translate_kernel.json.gz').write_bytes(raw)
 C=PackedClauses()
 for i in range(N):
  C.append(list(range(5*i+1,5*i+6)))
  for a in range(5):
   for b in range(a+1,5):C.append([-5*i-a-1,-5*i-b-1])
 for a,b,n in geometry['gains']:
  for c in range(5):C.append([-5*a-c-1,-5*b-(c-n)%5-1])
 C.append([1]);t=time.monotonic()
 with Solver(name='cadical195',bootstrap_with=C) as s:
  s.conf_budget(args.budget);ans=s.solve_limited();r=dict(schema='integer-strip-clock-search-v1',status='UNKNOWN' if ans is None else 'UNSAT_UNCERTIFIED' if not ans else 'SAT_UNCHECKED',gain_sha256=geometry['gain_sha256'],stats=s.accum_stats(),seconds=time.monotonic()-t)
  if ans:
   model=set(s.get_model());w=[next(c for c in range(5) if 5*i+c+1 in model) for i in range(N)]
   assert all(w[a]!=(w[b]+n)%5 for a,b,n in geometry['gains']);r['word']=''.join(map(str,w))
 (out/'integer-strip-clock.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='word'}),flush=True)

 if r['status']=='SAT_UNCHECKED':
  cert=dict(schema='integer-translate-five-coloring-v1',base_commit='a885b67c172726e14884cb43cd37b965dbb32575',q_sha256=geometry['q_sha256'],gain_sha256=geometry['gain_sha256'],color_shift=1,word=r['word'],word_sha256=hashlib.sha256(r['word'].encode()).hexdigest(),search={k:v for k,v in r.items() if k!='word'},scope='Candidate only until independent replay.')
  (out/'integer_translate_five_coloring.json').write_text(json.dumps(cert,indent=2)+'\n')

if __name__=='__main__':main()
