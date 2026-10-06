"""Discovery only: finite LP with complete integer pricing on a fixed boundary."""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as F
import json,gzip,subprocess,math,time,sys
import numpy as np
from scipy.optimize import linprog
import sympy as sp
WORK=Path(__file__).resolve().parents[1];ROOT=WORK/'repo';OUT=WORK/'experiments'
def read(f):
 p=ROOT/'certificates'/f;raw=p.read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
g=read('Y_full_geometry.json.gz');old=read('q_joint_boundary_gap.json');bd=old['boundary'];law=read('q_defect_lifting.json')['local_22_law'];V=bd['order'];ix={v:i for i,v in enumerate(V)};E={tuple(e) for e in g['edges']};terms=bd['terms']
win=[[ix[v] for v in w] for w in bd['saturated_windows']]
kind={frozenset(z['pair']):z['type'] for z in terms}
tr=bd['PRR_triple']; centers=[o for o in tr if all(kind[frozenset((o,v))]=='R' for v in tr if v!=o)]
assert len(centers)==1
o=centers[0];a,b=sorted(set(tr)-{o});assert kind[frozenset((a,b))]=='P';tri=[ix[a],ix[o],ix[b]]
unit=[0]*22
for a,b in E:
 if a in ix and b in ix:
  a,b=sorted((ix[a],ix[b]));unit[b]|=1<<a
edges=[sorted((ix[t['pair'][0]],ix[t['pair'][1]])) for t in terms]
mem=[[j for j,w in enumerate(win) if i in w] for i in range(22)];cost=[[j for j,(a,b) in enumerate(edges) if b==i] for i in range(22)]
def init(x):return '{'+','.join(init(v) if isinstance(v,list) else str(v) for v in x)+'}'
code=r'''
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <set>
#include <algorithm>
#include <climits>
using namespace std;
const unsigned unitb[22]=UNIT;
const int edgep[89][2]=EDGES;
const vector<int> memberships[22]=MEM;
const vector<int> costs[22]=COST;
const int window_end[7]=ENDS;
const int tri[3]=TRI;
long long coeff[89],best=LLONG_MIN,nodes=0,leaves=0,maxcount=0;
int col[22],cnt[7][5]={},np[7]={};unsigned classes[5]={};
vector<array<int,22>> solutions;set<pair<unsigned long long,unsigned long long>> signatures;
void dfs(int i,int top,long long score){
 ++nodes;
 if(i==22){
  ++leaves;
  if(score>best){best=score;maxcount=0;solutions.clear();signatures.clear();}
  if(score==best){++maxcount;if(solutions.size()<40){
   unsigned long long lo=0,hi=0;for(int j=0;j<89;++j)if(col[edgep[j][0]]==col[edgep[j][1]]){if(j<64)lo|=1ULL<<j;else hi|=1ULL<<(j-64);}
   if(signatures.insert({lo,hi}).second){array<int,22>w;copy(col,col+22,w.begin());solutions.push_back(w);}
  }}return;
 }
 for(int c=0;c<min(5,top+2);++c){
  if(unitb[i]&classes[c])continue;col[i]=c;
  if(i==max({tri[0],tri[1],tri[2]}) && int(col[tri[0]]==col[tri[1]])+int(col[tri[2]]==col[tri[1]])-int(col[tri[0]]==col[tri[2]])!=1)continue;
  bool bad=false;for(int t:memberships[i])if(np[t]+cnt[t][c]>2||(window_end[t]==i&&np[t]+cnt[t][c]!=2)){bad=true;break;}if(bad)continue;
  for(int t:memberships[i]){np[t]+=cnt[t][c];++cnt[t][c];}classes[c]|=1u<<i;
  long long inc=0;for(int j:costs[i])if(col[edgep[j][0]]==c)inc+=coeff[j];dfs(i+1,max(top,c),score+inc);
  classes[c]^=1u<<i;for(int t:memberships[i]){--cnt[t][c];np[t]-=cnt[t][c];}
 }
}
int main(int argc,char**argv){if(argc!=2)return 2;ifstream f(argv[1]);for(auto &x:coeff)if(!(f>>x))return 3;dfs(0,-1,0);
 cout<<"{\"maximum\":"<<best<<",\"nodes\":"<<nodes<<",\"leaves\":"<<leaves<<",\"maximizers\":"<<maxcount<<",\"words\":[";
 for(size_t i=0;i<solutions.size();++i){if(i)cout<<',';cout<<'"';for(int c:solutions[i])cout<<c;cout<<'"';}cout<<"]}\n";
}
'''
for token,val in [('UNIT',unit),('EDGES',edges),('MEM',mem),('COST',cost),('ENDS',[max(w) for w in win]),('TRI',tri)]:code=code.replace(token,init(val))
(OUT/'local_oracle.cpp').write_text(code);subprocess.run(['g++','-O3','-std=c++17',str(OUT/'local_oracle.cpp'),'-o',str(OUT/'local_oracle')],check=True)
def oracle(coeff):
 assert all(type(x) is int for x in coeff) and sum(map(abs,coeff))<2**61
 (OUT/'oracle_coeff.txt').write_text(' '.join(map(str,coeff)))
 p=subprocess.run([str(OUT/'local_oracle'),str(OUT/'oracle_coeff.txt')],capture_output=True,text=True,check=True)
 d=json.loads(p.stdout);assert d['leaves']==5648160;return d
cal=oracle([t['coefficient'] for t in terms]);assert cal['maximum']==2
(OUT/'oracle_calibration.json').write_text(json.dumps(cal));print('ORACLE_CALIBRATED',flush=True)
def norm(w):
 labels={};return tuple(labels.setdefault(c,len(labels)) for c in w)
def features(w):return tuple(int(w[a]==w[b]) for a,b in edges)
def validate_word(w):
 assert len(w)==22 and max(w)<5 and min(w)>=0
 assert all(w[i]!=w[j] for i in range(22) for j in range(i) if (unit[i]>>j)&1)
 assert all(sum(w[i]==w[j] for i,j in combinations(vs,2))==2 for vs in win)
 a,o,b=tri;assert int(w[a]==w[o])+int(w[b]==w[o])-int(w[a]==w[b])==1
words=[];seen=set();order=law['vertices'];li={v:i for i,v in enumerate(order)}
for a in law['atoms']:
 possible=[v for v in a.values() if isinstance(v,(str,list,tuple)) and len(v)==22]
 assert len(possible)==1,(a.keys(),possible)
 z=possible[0];w=norm([z[li[v]] for v in V]);validate_word(w)
 ft=features(w)
 if ft not in seen:seen.add(ft);words.append(w)
Qidx=[i for i,t in enumerate(terms) if t['type']=='Q']
bv=[sp.Rational(1)]+[sp.Rational(1,27) if t['type']=='P' else sp.Rational(14,27) if t['type']=='R' else sp.Rational(0) for t in terms]
qcol=np.array([0]+[-int(t['type']=='Q') for t in terms],dtype=float)
start=time.monotonic();history=[]
for sense in [-1,1]:
 result={'sense':sense,'status':'RUNNING','history':history}
 for it in range(180):
  M=np.array([features(w) for w in words],dtype=np.int8).T
  A=np.column_stack([np.vstack([np.ones(len(words)),M]),qcol])
  ans=linprog(np.r_[np.zeros(len(words)),sense],A_eq=A,b_eq=np.array(bv,dtype=float).reshape(-1),bounds=(0,None),method='highs')
  assert ans.success,ans.message
  y=ans.eqlin.marginals;active=[i for i,x in enumerate(ans.x[:-1]) if x>1e-9]
  coeff=np.rint(y[1:]*1000000).astype(np.int64).tolist();od=oracle(coeff)
  numeric_gap=od['maximum']/1000000+y[0]
  history.append({'sense':sense,'iteration':it,'pool':len(words),'q':ans.x[-1],'gap':numeric_gap})
  print('ITER',sense,it,'pool',len(words),'q',ans.x[-1],'gap',numeric_gap,'t',round(time.monotonic()-start,2),flush=True)
  # At convergence reconstruct dual by solving only equations, with exact integers.
  if numeric_gap<1e-4:
   cols=[i for i,x in enumerate(y) if abs(x)>1e-8]
   mat=[[1]+list(features(words[i])) for i in active]
   mat.append([0]+[int(t['type']=='Q') for t in terms]);rhs=[0]*len(active)+[-sense]
   mat=sp.Matrix([[row[j] for j in cols] for row in mat]);rhs=sp.Matrix(rhs)
   try:
    sol,params=mat.gauss_jordan_solve(rhs);sol=sol.subs({s:0 for s in params});yy=[sp.Rational(0)]*90
    for j,x in zip(cols,sol):yy[j]=x
    den=sp.ilcm(*[x.q for x in yy]);iv=[int(x*den) for x in yy];gg=math.gcd(*iv);iv=[x//gg for x in iv]
    odexact=oracle(iv[1:]);gap=odexact['maximum']+iv[0]
    print('EXACT_DUAL',gap,'coefficient_size',max(map(abs,iv)),flush=True)
   except (ValueError,ZeroDivisionError) as err:gap=None;print('DUAL_RECOVERY',str(err),flush=True)
   if gap is not None and gap<=0:
    sums={t:sum(iv[i+1] for i,z in enumerate(terms) if z['type']==t) for t in 'PQR'}
    qq=(sp.Rational(-iv[0])-sp.Rational(sums['P'],27)-sp.Rational(14*sums['R'],27))/sums['Q']
    # Exact primal on the positive LP support; every individual moment is imposed.
    AA=sp.Matrix([[1]*len(active)]+[[features(words[j])[i] for j in active] for i in range(89)])
    BB=sp.Matrix([1]+[sp.Rational(1,27) if t['type']=='P' else sp.Rational(14,27) if t['type']=='R' else qq for t in terms])
    ww,params=AA.gauss_jordan_solve(BB);ww=ww.subs({s:0 for s in params});assert all(x>=0 for x in ww) and sum(ww)==1 and AA*ww==BB
    dd=int(sp.ilcm(*[x.q for x in ww]));atoms=[{'word':list(words[i]),'numerator':int(x*dd)} for i,x in zip(active,ww) if x]
    result.update(status='EXACT_CANDIDATE_REQUIRES_INDEPENDENT_REPLAY',q=[int(qq.p),int(qq.q)],denominator=dd,atoms=atoms,coefficients=iv[1:],rhs=-iv[0],coefficient_sums=sums,oracle={k:v for k,v in odexact.items() if k!='words'},order=V)
    (OUT/('endpoint_'+('max' if sense==-1 else 'min')+'.json')).write_text(json.dumps(result,separators=(',',':')))
    print('ENDPOINT',sense,qq,'atoms',len(atoms),'den',dd,flush=True);break
   if gap is not None and gap>0:od=odexact
  added=0
  for s in od['words']:
   w=tuple(map(int,s));validate_word(w);ft=features(w)
   if ft not in seen:seen.add(ft);words.append(w);added+=1
  (OUT/'local_search_checkpoint.json').write_text(json.dumps({'sense':sense,'words':words,'history':history},separators=(',',':')))
  if not added:
   print('STAGNATION_UNCERTIFIED',sense,flush=True);break
 else:print('ROUND_LIMIT',sense,flush=True)
