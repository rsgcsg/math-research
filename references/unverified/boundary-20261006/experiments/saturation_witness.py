"""Full-Y positive calibration of all selected equality-face identities."""
from pathlib import Path
from itertools import combinations
import json,gzip,hashlib,subprocess,sys,zipfile,time
W=Path(__file__).resolve().parents[1];R=W/'repo'
def read(name):
 p=R/'certificates'/name;z=p.read_bytes();return json.loads(gzip.decompress(z) if z[:2]==b'\x1f\x8b' else z)
g=read('Y_full_geometry.json.gz');b=read('g14_pair_orbit_basis.json.gz');rr=read('g14_r_pair_orbit_basis.json.gz')
P=set(map(tuple,b['orbit_nodes_by_grade']['1/sqrt3']));Q=set(map(tuple,b['orbit_nodes_by_grade']['2']));Rr=set(map(tuple,rr['orbit_nodes']));E=set(map(tuple,g['edges']));n=len(g['points']);assert (n,len(E),len(P),len(Q),len(Rr))==(10077,49858,1860,780,1472)
adj=[set() for _ in range(n)];pn=[set() for _ in range(n)];rn=[set() for _ in range(n)]
for pairs,d in [(E,adj),(P,pn),(Rr,rn)]:
 for a,b in pairs:d[a].add(b);d[b].add(a)
wins=set()
for o in range(n):
 ns=pn[o]
 if len(ns)<6:continue
 ts=[]
 for a in sorted(ns):
  for b in sorted((ns&adj[a])-{x for x in ns if x<=a}):
   for c in ns&adj[a]&adj[b]:
    if c>b:ts.append((a,b,c))
 for a,b in combinations(ts,2):
  if set(a)&set(b):continue
  vs=tuple(sorted((o,*a,*b)));ps=set(combinations(vs,2))
  if len(ps&E)==6 and len(ps&P)==12 and len(ps&Rr)==3:wins.add(vs)
tri=set()
for o in range(n):
 for a,b in combinations(sorted(rn[o]),2):
  if (a,b) in P:tri.add((a,o,b))
wins=sorted(wins);tri=sorted(tri);assert (len(wins),len(tri))==(380,68)
site=W/'deps/site';site.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(site))
try:from pysat.solvers import Solver
except ImportError:
 archive=Path('/mnt/data/full-law-inputs-audit-20260921.zip')
 with zipfile.ZipFile(archive) as z:
  names=[x for x in z.namelist() if x.endswith('.whl') and 'cp313' in x];assert len(names)==1;z.extract(names[0],W/'deps');wheel=W/'deps'/names[0]
 subprocess.run([sys.executable,'-m','pip','install','--no-index','--no-deps','--target',str(site),str(wheel)],check=True)
 from pysat.solvers import Solver
from pysat.card import CardEnc,EncType
clauses=[];v=lambda a,c:5*a+c+1
for a in range(n):
 clauses.append([v(a,c) for c in range(5)])
 clauses.extend([-v(a,c),-v(a,d)] for c,d in combinations(range(5),2))
for a,b in sorted(E):clauses.extend([-v(a,c),-v(b,c)] for c in range(5))
top=5*n;eq={}
for a,b in sorted(P|Rr):
 top+=1;eq[a,b]=top
 for c in range(5):clauses.extend([[-v(a,c),-v(b,c),top],[-top,-v(a,c),v(b,c)]])
for vs in wins:
 ids=[eq[p] for p in combinations(vs,2) if p in eq]
 ce=CardEnc.atmost(ids,bound=2,top_id=top,encoding=EncType.seqcounter);top=ce.nv;clauses.extend(ce.clauses)
for a,o,b in tri:
 x=eq[tuple(sorted((a,o)))];y=eq[tuple(sorted((b,o)))];z=eq[a,b];clauses.extend([[x,y],[-z,x],[-z,y],[-x,-y,z]])
clauses.extend([[v(877,0)],[v(5535,1)],[v(7479,2)]])
start=time.monotonic()
with Solver(name='cadical195',bootstrap_with=clauses) as s:
 s.conf_budget(50000);ans=s.solve_limited(expect_interrupt=True);stats=s.accum_stats();assert ans is True,'SAT search not completed; not a negative theorem'
 model=set(x for x in s.get_model() if x>0);word=[next(c for c in range(5) if v(a,c) in model) for a in range(n)]
assert all(word[a]!=word[b] for a,b in E)
assert all(sum(word[a]==word[b] for a,b in combinations(vs,2))==2 for vs in wins)
assert all(int(word[a]==word[o])+int(word[b]==word[o])-int(word[a]==word[b])==1 for a,o,b in tri)
report={'schema':'pr-boundary-saturation-witness-v1','base_commit':'91849ffc04cc1e21193fbe3fddae2947072f7093','geometry_sha256':hashlib.sha256((R/'certificates/Y_full_geometry.json.gz').read_bytes()).hexdigest(),'word':''.join(map(str,word)),'seven_point_windows':wins,'PRR_triangles':tri,'counts':{s:sum(word[a]==word[b] for a,b in ps) for s,ps in [('P',P),('Q',Q),('R',Rr)]},'solver_stats':stats,'variables':top,'clauses':len(clauses),'elapsed_seconds':time.monotonic()-start,'scope':'An actual full-Y coloring satisfying every enumerated zero-slack identity; not a P/R mean law, not full15, not a new HN bound.'}
(R/'certificates/pr_boundary_saturation_witness.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
(W/'verification/saturation-search.json').write_text(json.dumps({'status':'SAT_POSITIVE_WORD_CHECKED','summary':{k:v for k,v in report.items() if k not in ['word','seven_point_windows','PRR_triangles']}},indent=2))
print(json.dumps({'status':'SAT_POSITIVE_WORD_CHECKED','counts':report['counts'],'windows':len(wins),'triangles':len(tri)}),flush=True)
