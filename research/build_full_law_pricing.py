import sys,json,gzip,hashlib,itertools,argparse
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description='Run/pack E105 and exhaustively calibrate the small pricing encoding.')
ap.add_argument('--results-dir',type=Path,required=True)
ap.add_argument('--cache',type=Path,help='Run the three searches first; omit to pack existing result JSON files.')
args=ap.parse_args();p=args.results_dir;p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(r/'research'))
from full_law_pricing import canonical, column, propose_master, PatternCNF,run
from verify_joint_two_motion_counterexample import verify
from pysat.solvers import Solver
if args.cache:
 data=json.loads(gzip.decompress(args.cache.read_bytes()))
 expected=json.loads((r/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
 if hashlib.sha256(canonical(data)).hexdigest()!=expected:raise SystemExit('cache binding mismatch')
 for name,strategy,rounds in [('dense','dense',6),('sparse','sparse',16),('reuse','reuse8',8)]:
  run(data,strategy,rounds,30000,p/(name+'-final.json'))
maps=[[(0,0),(2,3)],[(0,1),(2,3)]];edges=[(0,1),(1,2)]
words=[''.join(map(str,w)) for w in itertools.product(range(2),repeat=4) if all(w[i]!=w[j] for i,j in edges)]
cols=[column(w,maps) for w in words]
checks=[]
# Two events per motion: equal(00) and different(01). Price every signed
# combination in {-1,0,1}^4 and every target from -2 to 2.
keys=[(j,bytes(pat)) for j in range(2) for pat in ((0,0),(0,1))]
for coefficients in itertools.product((-1,0,1),repeat=4):
 y={key:v for key,v in zip(keys,coefficients) if v}
 scores=[sum(v*(int(col[j][0]==pat)-int(col[j][1]==pat)) for (j,pat),v in y.items()) for col in cols]
 for target in range(-2,3):
  enc=PatternCNF(4,edges,2);enc.pricing(y,maps,target)
  with Solver(name='cadical195',bootstrap_with=enc.clauses) as solver:
   answer=solver.solve()
  assert answer==any(v<=target for v in scores)
  checks.append(dict(coefficients=coefficients,target=target,satisfiable=answer))
masters=[]
for subset in ([0],[1],[0,1]):
 c=[column(w,[maps[j] for j in subset]) for w in words]
 m=propose_master(c)
 masters.append(dict(motions=subset,kind=m['kind'],weights=m.get('weights'),values=m.get('values')))
assert [x['kind'] for x in masters]==['EXACT_POSITIVE_LAW','EXACT_POSITIVE_LAW','EXACT_POOL_SEPARATOR']
inputs=json.loads((r/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']
data=dict(schema='full-law-pricing-v1',experiment='E105',date='2026-09-22',base_commit='53feae233ab7d781b3ca32242fabfabfb9cde3d4',
          input_semantic_sha256=inputs['semantic_sha256'],geometry=inputs['geometry'],motions=[x['motion'] for x in inputs['motions']],
          runs=[json.loads((p/(name+'-final.json')).read_text()) for name in ('dense','sparse','reuse')],
          counterexample=verify(),search_calibration=dict(checks=checks,masters=masters),
          scope='New pricing rounds and minimal two-motion calibration; no new ordinary HN bound.')
raw=bytearray(gzip.compress(canonical(data),mtime=0));raw[9]=255
(r/'certificates/full_law_pricing.json.gz').write_bytes(raw)
print(len(raw),hashlib.sha256(raw).hexdigest(),masters)
