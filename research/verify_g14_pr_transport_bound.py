#!/usr/bin/env python3
"""Portable solver-free verification of the local P/R pair-component obstruction."""
import argparse,copy,gzip,hashlib,json,sys
if not __debug__:
 raise RuntimeError('Verification requires assertions; run without -O')
from collections import Counter,deque
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def unique_keys(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('duplicate JSON key '+k)
  out[k]=v
 return out
def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw,object_pairs_hook=unique_keys)
def rgs(n,k):
 out=[]
 def rec(p,top):
  if len(p)==n:out.append(tuple(p));return
  for x in range(min(top+2,k)):rec(p+[x],max(top,x))
 rec([0],0);return out
def pair(a,b):return tuple(sorted((a,b)))
def d2(p,q,table,den):
 d=[x-y for x,y in zip(p,q)]
 return tuple(F(x,4*den*den) for x in product_twice(d,conjugate_twice(d),table))
def check_component(data,nodes,forest,grade):
 fwd=[];inv=[]
 for mp in data['mappings']:
  f=dict(mp);r={y:x for x,y in f.items()};assert len(f)==len(r);fwd.append(f);inv.append(r)
 targets={'P':(F(1,3),)+(F(0),)*31,'R':(F(4,3),)+(F(0),)*31};want=targets[grade]
 tab=multiplication_twice();den=data['denominator'];adj={x:set() for x in nodes};transitions=0
 for a,b in nodes:
  assert d2(data['points'][a],data['points'][b],tab,den)==want
  for f,r in zip(fwd,inv):
   if a in f and b in f:
    x=pair(f[a],f[b]);assert x in nodes;adj[(a,b)].add(x);adj[x].add((a,b));transitions+=1
   if a in r and b in r:
    x=pair(r[a],r[b]);assert x in nodes;adj[(a,b)].add(x);adj[x].add((a,b));transitions+=1
 seen=set();components=[]
 while len(seen)<len(nodes):
  todo=[min(nodes-seen)];seen.add(todo[0]);component=[]
  while todo:
   x=todo.pop();component.append(x)
   for y in adj[x]:
    if y not in seen:seen.add(y);todo.append(y)
  components.append(component)
 assert len(components)==1
 parent={x:x for x in nodes};rows=[]
 def find(x):
  if parent[x]!=x:parent[x]=find(parent[x])
  return parent[x]
 for i,e in enumerate(forest):
  s=tuple(e['source']);t=tuple(e['target']);j=e['motion'];assert s in nodes and t in nodes
  assert pair(fwd[j][s[0]],fwd[j][s[1]])==t
  assert find(s)!=find(t);parent[find(s)]=find(t)
  par,ch=(s,t) if e['direction']=='forward' else (t,s)
  assert e['direction'] in ('forward','inverse_traversal')
  rows.append(dict(row_id=i,source=list(s),target=list(t),parent=list(par),child=list(ch),motion=j,direction=e['direction']))
 assert len(forest)==len(nodes)-1 and len({find(x) for x in nodes})==1
 return fwd,rows,transitions

def main():
 root=Path(__file__).resolve().parents[1]
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--certificate',type=Path,default=root/'certificates/g14_pr_transport_bound.json')
 ap.add_argument('--pair-basis',type=Path,default=root/'certificates/g14_pair_orbit_basis.json.gz')
 ap.add_argument('--r-candidate',type=Path,default=root/'certificates/g14_r_pair_orbit_basis.json.gz')
 ap.add_argument('--write-receipt',action='store_true')
 a=ap.parse_args()
 sys.path.insert(0,str(root/'research'))
 global multiplication_twice,product_twice,conjugate_twice
 from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice
 from audit_full_law_preparation import reconstruct
 cert=read(a.certificate);cert_sha=cert.pop('certificate_sha256');assert cert_sha==sha(canonical(cert));cert['certificate_sha256']=cert_sha
 B=read(a.pair_basis);Rcert=read(a.r_candidate);bsha=B['basis_sha256'];rsha=Rcert['candidate_sha256']
 B0=dict(B);assert B0.pop('basis_sha256')==sha(canonical(B0))
 R0=dict(Rcert);assert R0.pop('candidate_sha256')==sha(canonical(R0))
 assert cert['pair_components']['P']['basis_sha256']==bsha and cert['pair_components']['R']['candidate_sha256']==rsha
 data,summary=reconstruct(root);semantic=summary['semantic_sha256'];assert semantic==cert['geometry_semantic_sha256']==B['geometry_semantic_sha256']==Rcert['geometry_semantic_sha256']
 P={tuple(x) for x in B['orbit_nodes_by_grade']['1/sqrt3']};R={tuple(x) for x in Rcert['orbit_nodes']}
 assert len(P)==len(B['orbit_nodes_by_grade']['1/sqrt3']) and len(R)==len(Rcert['orbit_nodes'])
 assert all(0<=a<b<len(data['points']) for a,b in P|R)
 assert Rcert['seed']['source_pair']==[233,239] and Rcert['seed']['image_pair']==[238,5557]
 fP,rowsP,tp=check_component(data,P,[x for x in B['forest_edges'] if x['grade']=='1/sqrt3'],'P')
 fR,rowsR,tr=check_component(data,R,Rcert['forest_edges'],'R')
 assert cert['pair_components']['P']['node_count']==len(P)==1860 and cert['pair_components']['R']['node_count']==len(R)==1472
 # Audit source G14 proof binding and original virtual-event seed coverage.
 g14path=root/'certificates/g14_port_or_certificate.json'
 g14=read(g14path);assert g14['actual_Y_embedding']['semantic_sha256']==semantic
 legacy=copy.deepcopy(g14);legacy.get('actual_Y_embedding',{}).pop('semantic_sha256',None)
 expected=B['source_g14_certificate_sha256'];legacy_raw=(json.dumps(legacy,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode();assert sha(legacy_raw)==expected
 labels=g14['actual_Y_embedding']['vertex_indices'];seedP={pair(labels[e['u']],labels[e['v']]) for e in g14['independent_check']['virtual_pairs'] if e['distance']=='1/sqrt3'}
 assert len(seedP)==27 and seedP<=P
 assert tuple(Rcert['seed']['source_pair']) in R and tuple(Rcert['seed']['image_pair']) in R
 V=cert['local_hex']['vertices'];assert V==[4641,877,887,3483,5535,7479,7489]
 T=multiplication_twice();den=data['denominator'];tags={'unit':F(1),'P':F(1,3),'R':F(4,3)};records=[]
 for u,v in combinations(V,2):
  value=d2(data['points'][u],data['points'][v],T,den)
  tag=next((name for name,q in tags.items() if value==(q,)+(F(0),)*31),None);assert tag is not None
  records.append(dict(pair=list(pair(u,v)),tag=tag,squared_distance=str(tags[tag])))
 assert records==cert['local_hex']['pair_tags']
 counts=Counter(x['tag'] for x in records);assert counts==Counter({'unit':6,'P':12,'R':3}) and dict(counts)==cert['local_hex']['tag_counts']
 edges={tuple(x) for x in data['edges']};unit={tuple(x['pair']) for x in records if x['tag']=='unit'}
 P7={tuple(x['pair']) for x in records if x['tag']=='P'};R7={tuple(x['pair']) for x in records if x['tag']=='R'}
 assert unit<={pair(*x) for x in edges} and P7<=P and R7<=R
 index={v:i for i,v in enumerate(V)};unit_idx=[(index[x],index[y]) for x,y in unit];event_idx=[(index[x],index[y]) for x,y in P7|R7]
 legal=0;minimum=999;examples=[]
 for part in rgs(7,5):
  if any(part[x]==part[y] for x,y in unit_idx):continue
  legal+=1;n_same=sum(part[x]==part[y] for x,y in event_idx)
  if n_same<minimum:minimum=n_same;examples=[list(part)]
  elif n_same==minimum and len(examples)<5:examples.append(list(part))
 assert legal==cert['local_hex']['legal_proper_5_partition_count'] and minimum==cert['local_hex']['minimum_same_P_or_R_pairs']==2
 assert examples==cert['local_hex']['minimizing_partition_examples']
 # Triangle pair tags and all Bell-3 partitions.
 tri=cert['local_triangle'];assert tri['vertices']==[229,4641,305]
 assert pair(*tri['P_pair']) in P and all(pair(*x) in R for x in tri['R_pairs'])
 ix={x:i for i,x in enumerate(tri['vertices'])};ri=[(ix[x],ix[y]) for x,y in tri['R_pairs']];pa=tri['P_pair'];pi=(ix[pa[0]],ix[pa[1]])
 values=[sum(z[a]==z[b] for a,b in ri)-int(z[pi[0]]==z[pi[1]]) for z in rgs(3,5)]
 assert len(values)==tri['all_Bell3_partitions']==5 and max(values)==tri['maximum_2R_minus_P']==1
 # Upper calibration: the outer triple is a unit triangle, so the center can match at most one
 # outer vertex; its three P-spoke equality indicators sum to at most one.
 upper=cert['local_P_upper_bound'];uv=upper['vertices'];assert uv==[4641,877,5535,7479]
 outer=[pair(*x) for x in combinations(uv[1:],2)];spokes=[pair(uv[0],x) for x in uv[1:]]
 assert upper['outer_unit_triangle']==[list(x) for x in outer] and upper['P_spokes']==[list(x) for x in spokes]
 assert all(x in {pair(*e) for e in data['edges']} for x in outer) and all(x in P for x in spokes)
 uix={x:i for i,x in enumerate(uv)};outer_idx=[(uix[a],uix[b]) for a,b in outer];spoke_idx=[(uix[a],uix[b]) for a,b in spokes]
 upper_scores=[sum(z[a]==z[b] for a,b in spoke_idx) for z in rgs(4,5) if all(z[a]!=z[b] for a,b in outer_idx)]
 assert len(upper_scores)==upper['proper_partitions_checked'] and max(upper_scores)==upper['maximum_same_P_spokes']==1
 # Verify the displayed F exactly equals the 30-row integer combination.
 Fcoef=Counter()
 for x,y in R7:Fcoef[pair(x,y)]+=2
 for x,y in tri['R_pairs']:Fcoef[pair(x,y)]-=3
 assert sum(Fcoef.values())==0
 fdesc=cert['face_separator'];assert fdesc['zero_coefficient_sum'] and len(fdesc['forest_row_decomposition'])==fdesc['nonzero_forest_rows']==30
 rows_by_id={x['row_id']:x for x in rowsR}
 def validate_span(terms):
  rebuilt=Counter();seen_ids=set()
  for term in terms:
   i=term['row_id'];assert type(i) is int and i not in seen_ids;seen_ids.add(i)
   row=rows_by_id[i];lam=F(term['coefficient'])
   assert row['source']==term['source'] and row['target']==term['target'] and row['motion']==term['motion']
   rebuilt[tuple(row['source'])]+=lam;rebuilt[tuple(row['target'])]-=lam
  assert all(rebuilt[v]==F(Fcoef[v]) for v in R), 'forest combination is not F'
 validate_span(fdesc['forest_row_decomposition'])
 for label,change in [
   ('changed-row-coefficient',lambda t:t[0].__setitem__('coefficient',str(F(t[0]['coefficient'])+1))),
   ('missing-row',lambda t:t.pop()),
   ('changed-row-target',lambda t:t[0]['target'].__setitem__(0,t[0]['target'][0]+1))]:
  terms=copy.deepcopy(fdesc['forest_row_decomposition']);change(terms)
  try:validate_span(terms)
  except (AssertionError,ValueError,KeyError,IndexError):pass
  else:raise ValueError('mutation accepted: '+label)
 # Exact elimination: 2*(12p+3r-2)+3*(p-2r+1)=27p-1.
 assert [2*x+3*y for x,y in zip((12,3,-2),(1,-2,1))]==[27,0,-1]
 assert fdesc['event_potential']=='F = 2*(e_R(877,7489)+e_R(887,7479)+e_R(3483,5535)) - 3*(e_R(229,4641)+e_R(305,4641))'
 assert cert['expected_inequalities']==['12p+3r >= 2','2r-p <= 1'] and cert['derived_inequality']=='27p >= 1'
 assert cert['necessary_interval']['lower']=='1/27' and cert['necessary_interval']['upper']=='1/3'
 report=dict(status='PASS_G14_PR_PAIR_COMPONENT_FACE_SEPARATOR',certificate_sha256=cert_sha,geometry_semantic_sha256=semantic,
  pair_basis_sha256=bsha,r_candidate_sha256=rsha,legacy_g14_source_sha256=expected,
  P_component_nodes=len(P),R_component_nodes=len(R),P_transitions=tp,R_transitions=tr,
  K7_pair_tags=dict(counts),K7_min_same_P_or_R=minimum,K7_legal_proper5_partitions=legal,
  triangle_Bell3_max=1,P_upper_spoke_max=1,necessary_interval=['1/27','1/3'],
  forest_span_nonzero_rows=30,face_F_lower_bound=1,derived_inequality='27p>=1',
  row_span_mutations_rejected=['changed-row-coefficient','missing-row','changed-row-target'],
  scope=cert['scope'])
 receipt=root/'certificates/g14_pr_transport_verification.json'
 if a.write_receipt:receipt.write_text(json.dumps(report,indent=2)+'\n')
 else:assert canonical(read(receipt))==canonical(report), 'P/R receipt differs from fresh replay'
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
