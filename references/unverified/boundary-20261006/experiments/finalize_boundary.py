"""Independent exact replay and durable research checkpoint."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import hashlib,json,gzip,time,subprocess,sys,traceback,platform
W=Path(__file__).resolve().parents[1];R=W/'repo';OUT=W/'verification';OUT.mkdir(exist_ok=True)

def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def insist(x,m):
 if not x:raise ValueError(m)
def run():
 start=time.monotonic();bd=read(R/'certificates/q_joint_boundary_gap.json')['boundary'];V=bd['order'];ix={v:i for i,v in enumerate(V)}
 g=read(R/'certificates/Y_full_geometry.json.gz');terms=bd['terms'];pairs=[tuple(ix[v] for v in t['pair']) for t in terms];E=[(ix[a],ix[b]) for a,b in g['edges'] if a in ix and b in ix];insist(len(E)==34,'E count')
 win=[[ix[v] for v in t] for t in bd['saturated_windows']]
 kind={frozenset(t['pair']):t['type'] for t in terms};tr=bd['PRR_triple'];o=next(o for o in tr if all(kind[frozenset((o,v))]=='R' for v in tr if v!=o));a,b=sorted(set(tr)-{o});tri=[ix[a],ix[o],ix[b]]
 insist(len(V)==22 and len(terms)==89 and len(win)==7,'instance shape')
 ends=[max(x) for x in win];members=[[t for t,x in enumerate(win) if i in x] for i in range(22)]
 unit=[set() for _ in V]
 for a,b in E:a,b=sorted((a,b));unit[b].add(a)
 finals=[]
 for name in ('max','min'):
  f=W/'experiments'/('endpoint_'+name+'.json');insist(f.is_file(),'Unfinished search: missing '+f.name);d=read(f)
  insist(d['order']==V,'word ordering');qq=F(*d['q']);den=d['denominator'];atoms=d['atoms'];cf=d['coefficients'];rhs=d['rhs'];insist(type(den) is int and den>0,'denominator')
  insist(all(type(x) is int for x in cf) and len(cf)==89 and type(rhs) is int,'integer dual')
  insist(sum(a['numerator'] for a in atoms)==den and all(type(a['numerator']) is int and a['numerator']>0 for a in atoms),'positive mass')
  for a in atoms:
   word=a['word'];insist(len(word)==22 and all(type(x) is int and 0<=x<5 for x in word),'word')
   insist(all(word[i]!=word[j] for i,j in E),'improper')
   insist(all(sum(word[i]==word[j] for i,j in combinations(z,2))==2 for z in win),'seven point saturation')
   a0,o,b0=tri;insist(int(word[a0]==word[o])+int(word[b0]==word[o])-int(word[a0]==word[b0])==1,'triangle saturation')
  for z,(a,b) in zip(terms,pairs):
   target=F(1,27) if z['type']=='P' else F(14,27) if z['type']=='R' else qq
   insist(F(sum(t['numerator'] for t in atoms if t['word'][a]==t['word'][b]),den)==target,'individual moment')
  sums={t:sum(x for z,x in zip(terms,cf) if z['type']==t) for t in 'PQR'}
  insist(sums['Q']>0 if name=='max' else sums['Q']<0,'dual orientation')
  insist(F(sums['P'],27)+F(14*sums['R'],27)+sums['Q']*qq==rhs,'matching dual value')
  finals.append(d)
 # Independently enumerate restricted-growth words; not the C++ producer and no LP/SAT library.
 coefficients=[d['coefficients'] for d in finals];costs=[[] for _ in V]
 for j,(a,b) in enumerate(pairs):a,b=sorted((a,b));costs[b].append((a,coefficients[0][j],coefficients[1][j]))
 color=[-1]*22;window_counts=[[0]*5 for _ in win];window_pairs=[0]*7;nodes=leaves=0;maxima=[None,None]
 def visit(i,used,s0,s1):
  nonlocal nodes,leaves
  nodes+=1
  if i==22:
   leaves+=1
   if maxima[0] is None or s0>maxima[0]:maxima[0]=s0
   if maxima[1] is None or s1>maxima[1]:maxima[1]=s1
   insist(s0<=finals[0]['rhs'] and s1<=finals[1]['rhs'],'dual counterexample')
   return
  forbidden={color[j] for j in unit[i]}
  for c in range(min(used+1,5)):
   if c in forbidden:continue
   color[i]=c
   if i==max(tri):
    a,o,b=tri
    if int(color[a]==color[o])+int(color[b]==color[o])-int(color[a]==color[b])!=1:continue
   if any(window_pairs[t]+window_counts[t][c]>2 or ends[t]==i and window_pairs[t]+window_counts[t][c]!=2 for t in members[i]):continue
   for t in members[i]:window_pairs[t]+=window_counts[t][c];window_counts[t][c]+=1
   n0,n1=s0,s1
   for j,u,v in costs[i]:
    if color[j]==c:n0+=u;n1+=v
   visit(i+1,max(used,c+1),n0,n1)
   for t in members[i]:window_counts[t][c]-=1;window_pairs[t]-=window_counts[t][c]
   color[i]=-1
 visit(0,0,0,0)
 insist(leaves==5648160,'complete boundary count')
 # Only after every certificate succeeds write any result into the tracked tree.
 cert={'schema':'exact-local-pr-boundary-interval-v1','research_base':'91849ffc04cc1e21193fbe3fddae2947072f7093','geometry_sha256':sha(R/'certificates/Y_full_geometry.json.gz'),'prior_certificate_sha256':sha(R/'certificates/q_joint_boundary_gap.json'),'order':V,'terms':[{'pair':t['pair'],'type':t['type']} for t in terms],'windows':bd['saturated_windows'],'PRR_triple':bd['PRR_triple'],'endpoints':[{k:d[k] for k in ('sense','q','denominator','atoms','coefficients','rhs','coefficient_sums')} for d in finals],'scope':'Exact q interval for this 22-point P/Q/R marginal model at p=1/27,r=14/27. Neither full Y extension nor full15 feasibility nor a new ordinary HN bound.'}
 cp=R/'certificates/exact_local_pr_boundary_interval.json';cp.write_text(json.dumps(cert,ensure_ascii=False,indent=2)+'\n')
 report={'status':'PASS','python':platform.python_version(),'recursion_nodes':nodes,'complete_boundary_partitions':leaves,'maximum_dual_scores':maxima,'certificate_sha256':sha(cp),'endpoint_atom_counts':[len(d['atoms']) for d in finals],'elapsed_seconds':round(time.monotonic()-start,3),'scope':cert['scope'],'verification':'Fresh independent Python integer enumeration and every atom/edge/individual moment checked; this invocation did not rerun whole-repository make check or regenerate all Y geometry.'}
 (R/'certificates/exact_local_pr_boundary_interval_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 lo=F(*finals[1]['q']);hi=F(*finals[0]['q'])
 text=f'''# 固定22点P/R尖点的精确Q区间\n\n2026-10-06。基于已发布研究提交 `91849ffc04cc1e21193fbe3fddae2947072f7093`。\n此处只研究T163的固定22点全部34条单位边及47P/11Q/31R均值义务，\n不冻结支持数，不声称整个Y可延拓，也不声称原始full15或普通HN已解决。\n\n## 精确结果\n\n在p=1/27、r=14/27上，q的全部可行值恰好为 **[{lo}, {hi}]**。\n下、上端点分别有{len(finals[1]['atoms'])}、{len(finals[0]['atoms'])}个正权合法划分；\n公分母、全部色词、逐事件约束和整数对偶见 `certificates/exact_local_pr_boundary_interval.json`。\n任意两个端点律的凸组合实现整个区间。\n\n## 证明\n\n每个七点窗口至多五色，故其同色点对计数N至少为2。\n这些窗口各有6条单位边、12个P对和3个R对，故期望N=12/27+42/27=2。\n非负随机变量N-2期望为0，要求每个正质量划分在全部七个窗口上同时取等。\n三点传递性给T=e(a,o)+e(b,o)-e(a,b)至多为1；期望2r-p=1，\n故相同的每个正质量划分还必须使T=1。没有据此假定任何具体支持原子。\n\n在这组必要条件下，用restricted-growth字符串逐一枚举全部proper至多五块划分，\n共{leaves}项。整数对偶分别在每一项上成立。将其中P/Q/R系数分类求和并取期望，\n得到q的上下界；每端点与相应有理正律相等。独立检查不用浮点LP或SAT，\n而从实际边、窗口及整数对偶重做枚举，并逐项验证每个原子的实际边和所有89个均值。\n\n## 不能推出的结论\n\n这只是固定22点局部边际空间的精确截面，不保证每个局部原子或该概率律可延拓到Y，\n更不保证不同窗口的这些边际可拼成同一个全15域共同律。对偶仅在p/r尖点上有效，\n除非另给非负缺陷提升证明，不得把它当成无条件全词不等式。\n完整Y自由运输延拓仍是下一项实质缺口；同一固定局部截面上的调权优化可停止。\n'''
 (R/'docs/proofs/exact_local_pr_boundary_interval.md').write_text(text)
 # Save exact replay implementation as a research asset. Input geometry provenance remains explicit.
 (OUT/'completion.json').write_text(json.dumps({'status':'PASS','minimum_q':str(lo),'maximum_q':str(hi),'report':report},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':'PASS','q_interval':[str(lo),str(hi)],'leaves':leaves},ensure_ascii=False),flush=True)
if __name__=='__main__':
 try:run()
 except Exception:
  (OUT/'completion.json').write_text(json.dumps({'status':'NOT_COMPLETED','traceback':traceback.format_exc()},indent=2));raise
