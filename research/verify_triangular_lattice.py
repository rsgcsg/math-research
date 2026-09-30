"""Independent standard-library proof check for eta-closed triangular saturations.
Rebuild every representative with rational interval arithmetic and all contacts
with two different finite-field maps, not the searcher's quadratic-root table.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse, gzip, hashlib, json, math, sys, time
from audit_full_law_preparation import reconstruct, unique_keys
from verify_quintic_core_probe import RAD, multiplication_twice, product_twice, conjugate_twice, digest

def require(ok, message):
 if not ok:raise ValueError(message)

def interval_basis(bits):
 s=1<<bits
 roots=[]
 for rad in RAD:
  q=math.isqrt(rad*s*s);roots.append((q,q+(q*q!=rad*s*s)))
 f=roots[4];co=((f[0]-s)//4,(f[1]-s+3)//4)
 low=math.isqrt((10*s+2*f[0])*s);high=math.isqrt((10*s+2*f[1])*s)+1
 si=(low//4,(high+3)//4)
 def mul(a,b):
  v=[a[i]*b[j] for i in (0,1) for j in (0,1)]
  return min(v)//s,(max(v)+s-1)//s
 return roots+[(0,0)]*8+[mul(co,r) for r in roots]+[(-mul(si,r)[1],-mul(si,r)[0]) for r in roots]

def floor_real(coeff,den,bases):
 require(den>0,'positive denominator')
 if all(x==0 for x in coeff[1:]):return coeff[0]//den
 for bits,intervals in bases:
  lo=sum(c*(v[0] if c>=0 else v[1]) for c,v in zip(coeff,intervals))
  hi=sum(c*(v[1] if c>=0 else v[0]) for c,v in zip(coeff,intervals))
  a,b=lo//(den*(1<<bits)),hi//(den*(1<<bits))
  if a==b:return a
 raise ValueError('floor not separated within certified precision budget')

def exact_representatives(data,levels,table):
 require(type(levels) is int and 1<=levels<=5,'eta levels')
 scale=16;den=data['denominator']*scale
 current=[tuple(scale*x for x in p) for p in data['points']];seen=set(current)
 eta=[int(j==16) for j in range(32)]
 for _ in range(levels-1):
  nxt=[]
  for p in current:
   v=product_twice(eta,p,table);require(all(x%2==0 for x in v),'integral eta step');nxt.append(tuple(x//2 for x in v))
  seen.update(nxt);current=nxt
 divisor=den
 for p in seen:divisor=math.gcd(divisor,*p)
 den//=divisor;points=sorted(tuple(x//divisor for x in p) for p in seen)
 require(den%2==0,'even common denominator')
 e9=[int(j==9) for j in range(32)];bases=[(b,interval_basis(b)) for b in (64,128,256)]
 reps=set();positions=[]
 for p in points:
  bar=conjugate_twice(p)
  cross=product_twice(e9,[2*x-y for x,y in zip(p,bar)],table)
  beta=[-x for x in cross]
  alpha=[6*(2*x+y)+z for x,y,z in zip(p,bar,cross)]
  require(conjugate_twice(beta)==[2*x for x in beta] and conjugate_twice(alpha)==[2*x for x in alpha],'real lattice coordinates')
  m=floor_real(alpha,24*den,bases);n=floor_real(beta,12*den,bases)
  q=list(p);q[0]-=den*m+den*n//2;q[9]-=den*n//2;q=tuple(q)
  reps.add(q);positions.append((p,q,m,n))
 Q=sorted(reps);index={q:i for i,q in enumerate(Q)}
 return Q,den,points,[(p,index[q],m,n) for p,q,m,n in positions]

def small_prime_map(p,table):
 require(p>=3 and all(p%d for d in range(2,math.isqrt(p)+1)),'prime')
 e=next(pow(a,(p-1)//5,p) for a in range(2,p) if pow(a,(p-1)//5,p)!=1)
 root={r:next(a for a in range(p) if a*a%p==r%p) for r in (3,11,-1)}
 root[5]=(2*(e+pow(e,-1,p))+1)%p
 require(root[5]*root[5]%p==5,'root-five')
 images=[]
 for power in (0,1):
  for imag in (0,1):
   for rad in RAD:
    val=pow(e,power,p)*(root[-1] if imag else 1)
    for r in (3,5,11):
     if rad%r==0:val=val*root[r]%p
    images.append(val%p)
 require(all(sum(c*images[z] for z,c in row)%p==2*images[i]*images[j]%p for (i,j),row in table.items()),'all basis products')
 bars=[sum(c*v for c,v in zip(conjugate_twice([int(i==j) for j in range(32)]),images))*pow(2,-1,p)%p for i in range(32)]
 return images,bars

def all_contacts(Q,den,table,primes=(181,421)):
 projected=[];maps=[]
 for p in primes:
  require(den%p!=0,'denominator invertible')
  im,ba=small_prime_map(p,table);maps.append((im,ba))
  projected.append([(sum(a*b for a,b in zip(q,im))%p,sum(a*b for a,b in zip(q,ba))%p) for q in Q])
 p,p2=primes;bucket=defaultdict(list)
 for i,key in enumerate(projected[0]):bucket[key].append(i)
 offsets=[]
 for m in range(-2,3):
  for n in range(-2,3):
   residues=[( (den*m*im[0]+den*n//2*(im[0]+im[9]))%r,
               (den*m*ba[0]+den*n//2*(ba[0]+ba[9]))%r) for r,(im,ba) in zip(primes,maps)]
   offsets.append((m,n,*residues))
 directions=[(v,den*den*pow(v,-1,p)%p) for v in range(1,p)]
 gains=[(i,i,m,n) for i in range(len(Q)) for m,n in [(1,0),(0,1),(1,-1)]]
 target=[4*den*den]+[0]*31;first=second=0
 for i,((x,y),(x2,y2)) in enumerate(zip(*projected)):
  for m,n,(dx,dy),(dx2,dy2) in offsets:
   xx=(x-dx)%p;yy=(y-dy)%p
   for v,vbar in directions:
    for j in bucket.get(((xx-v)%p,(yy-vbar)%p),()):
     if j<=i:continue
     first+=1;u2,w2=projected[1][j]
     if ((x2-u2-dx2)*(y2-w2-dy2)-den*den)%p2:continue
     second+=1
     diff=[u-v for u,v in zip(Q[i],Q[j])];diff[0]-=den*m+den*n//2;diff[9]-=den*n//2
     if product_twice(diff,conjugate_twice(diff),table)==target:gains.append((i,j,m,n))
 return sorted(set(gains)),dict(first_filter_candidates=first,exact_norm_checks=second,basis_products_checked=2*1024)

def check_word(cert,Q,gains):
 require(cert.get('schema')=='mixed-triangular-clock-v1','certificate schema')
 require(cert.get('representative_sha256')==digest(Q),'representative hash')
 require(cert.get('gain_sha256')==digest(gains),'contact hash')
 slope=cert.get('slope');require(type(slope) is int and slope in (2,3,4),'slope')
 w=cert.get('word');require(type(w) is str and len(w)==len(Q) and set(w)<=set('01234'),'complete color word')
 require(all(int(w[i])!=(int(w[j])+m+slope*n)%5 for i,j,m,n in gains),'all infinite contact inequalities')
 return dict(representatives=len(Q),contact_types=len(gains),slope=slope,word_sha256=hashlib.sha256(w.encode()).hexdigest())

def main():
 if not __debug__:raise RuntimeError('verification requires assertions')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--certificate',type=Path,default=Path(__file__).resolve().parents[1]/'certificates/triangular_lattice_five_coloring.json');ap.add_argument('--write-geometry',type=Path)
 args=ap.parse_args();root=Path(__file__).resolve().parents[1];t=time.monotonic()
 cert=json.loads(args.certificate.read_text(),object_pairs_hook=unique_keys)
 data,summary=reconstruct(root);table=multiplication_twice();Q,den,pts,pos=exact_representatives(data,cert.get('levels'),table)
 gains,filters=all_contacts(Q,den,table);word=check_word(cert,Q,gains)
 # Original Y edges must be recovered with the correct displacement convention.
 key={p:(i,m,n) for p,i,m,n in pos};mult=den//data['denominator'];require(den%data['denominator']==0,'Y scale')
 old=[key[tuple(mult*x for x in p)] for p in data['points']];edges=set(gains)
 for a,b in data['edges']:
  i,m,n=old[a];j,s,t1=old[b];h,k=s-m,t1-n
  if i>j:i,j,h,k=j,i,-h,-k
  if i==j and (h,k) not in ((1,0),(0,1),(1,-1)):h,k=-h,-k
  require((i,j,h,k) in edges,'original actual edge recovered')
 report=dict(status='PASS',input_semantic_sha256=summary['semantic_sha256'],levels=cert['levels'],denominator=den,seed_points=len(pts),**word,**filters,Y_edges_recovered=len(data['edges']),seconds=time.monotonic()-t,scope='Complete infinite lattice host upper bound from exact representatives and every displacement; no general HN bound.')
 if args.write_geometry:
  args.write_geometry.write_bytes(gzip.compress(json.dumps(dict(Q=Q,den=den,gains=gains,report=report),separators=(',',':')).encode(),mtime=0))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
