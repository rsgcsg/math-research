#!/usr/bin/env python3
"""Solver-free checker for the portable common law on the G14 p=0,q=1 face."""
import argparse,copy,gzip,hashlib,json,math,sys
if not __debug__:
 raise RuntimeError('Verification requires assertions; run without -O')
from collections import deque
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

def sha(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def unique_keys(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('duplicate JSON key: '+k)
  out[k]=v
 return out
def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw,object_pairs_hook=unique_keys)
def pattern(word,ids):
 labels={};return ''.join(str(labels.setdefault(word[i],len(labels))) for i in ids)
def d2(p,q,table,den):
 delta=[a-b for a,b in zip(p,q)]
 return tuple(F(x,4*den*den) for x in product_twice(delta,conjugate_twice(delta),table))
def rgs(n):
 out=[]
 def rec(p,top):
  if len(p)==n:
   out.append(''.join(map(str,p)));return
  for x in range(top+2):rec(p+[x],max(top,x))
 rec([0],0);return out

def validate_port4_rows(data,rows,expected_sha):
 edges={tuple(e) for e in data['edges']}
 ports=[(8,(3604,3817,4114,4641)),(7,(3484,6700,7219,9104)),
        (3,(3748,3797,4513,5158)),(14,(233,239,9425,9951))]
 rebuilt=[]
 for j,T in ports:
  mapping=dict(data['mappings'][j]);assert all(x in mapping for x in T)
  image=[mapping[x] for x in T]
  for pat in rgs(4):
   if all(not (pat[a]==pat[b] and tuple(sorted((T[a],T[b]))) in edges)
          for a,b in combinations(range(4),2)):
    rebuilt.append(dict(motion=j,source=list(T),image=image,pattern=pat))
 assert len(rebuilt)==50 and rows==rebuilt and sha(canonical(rebuilt))==expected_sha
 return rebuilt

def validate_pair_basis(data,B,g14):
 copyB=dict(B);basis_sha=copyB.pop('basis_sha256');assert basis_sha==sha(canonical(copyB))
 assert B['geometry_semantic_sha256']==sha(canonical(data)) and B['motion_names']==data['motions']
 nodes={g:{tuple(p) for p in pairs} for g,pairs in B['orbit_nodes_by_grade'].items()}
 assert {g:len(p) for g,p in nodes.items()}=={'1/sqrt3':1860,'2':780}
 for g,pairs in B['orbit_nodes_by_grade'].items():
  assert len(pairs)==len(nodes[g]) and all(0<=a<b<len(data['points']) for a,b in pairs)
 labels=g14['actual_Y_embedding']['vertex_indices'];seeds={'1/sqrt3':set(),'2':set()}
 for e in g14['independent_check']['virtual_pairs']:
  seeds[e['distance']].add(tuple(sorted((labels[e['u']],labels[e['v']]))))
 assert {g:len(p) for g,p in seeds.items()}=={'1/sqrt3':27,'2':5}
 assert all(seeds[g]<=nodes[g] for g in nodes)
 fwd=[];inv=[]
 for pairs in data['mappings']:
  f=dict(pairs);r={v:k for k,v in f.items()};assert len(f)==len(r);fwd.append(f);inv.append(r)
 tab=multiplication_twice();den=data['denominator'];targets={'1/sqrt3':(F(1,3),)+(F(0),)*31,'2':(F(4),)+(F(0),)*31}
 transitions=0
 for grade,ps in nodes.items():
  adj={p:set() for p in ps}
  for a,b in ps:
   assert d2(data['points'][a],data['points'][b],tab,den)==targets[grade]
   for f,r in zip(fwd,inv):
    if a in f and b in f:
     t=tuple(sorted((f[a],f[b])));assert t in ps;adj[(a,b)].add(t);adj[t].add((a,b));transitions+=1
    if a in r and b in r:
     t=tuple(sorted((r[a],r[b])));assert t in ps;adj[(a,b)].add(t);adj[t].add((a,b));transitions+=1
  visited=set();components=[]
  while len(visited)<len(ps):
   root=min(ps-visited);todo=[root];visited.add(root);component=[]
   while todo:
    p=todo.pop();component.append(p)
    for q in adj[p]:
     if q not in visited:visited.add(q);todo.append(q)
   components.append(component)
  assert len(components)==1 and len(set(components[0])&seeds[grade])==len(seeds[grade])
 forest=B['forest_edges'];assert len(forest)==2638
 parent={g:{p:p for p in ps} for g,ps in nodes.items()};counts={'1/sqrt3':0,'2':0}
 def find(g,x):
  if parent[g][x]!=x:parent[g][x]=find(g,parent[g][x])
  return parent[g][x]
 for e in forest:
  grade=e['grade'];j=e['motion'];s=tuple(e['source']);t=tuple(e['target']);f=fwd[j]
  assert s in nodes[grade] and t in nodes[grade]
  assert tuple(sorted((f[s[0]],f[s[1]])))==t
  assert find(grade,s)!=find(grade,t);parent[grade][find(grade,s)]=find(grade,t);counts[grade]+=1
 assert counts=={'1/sqrt3':1859,'2':779}
 assert all(len({find(g,p) for p in nodes[g]})==1 for g in nodes)
 return nodes,transitions

def validate_certificate(cert,data,nodes,rows):
 if not __debug__:raise RuntimeError('Run without python -O')
 assert cert['four_port_basis']['rows']==rows
 corpus=cert['whole_Y_word_corpus'];assert len(corpus)==cert['word_corpus_count']==81
 assert sha(canonical(corpus))==cert['word_corpus_sha256']
 words=[r['word'] for r in corpus];assert len(set(words))==81
 for r,w in zip(corpus,words):
  assert sha(w.encode())==r['sha256'] and len(w)==len(data['points']) and set(w)<=set('01234')
  assert all(w[a]!=w[b] for a,b in data['edges'])
  assert sum(w[a]==w[b] for a,b in nodes['1/sqrt3'])==0
  assert sum(w[a]==w[b] for a,b in nodes['2'])==780
 weights=[F(0) for _ in words];used=set()
 for x in cert['weights']:
  i=x['word_id'];assert type(i) is int and 0<=i<len(words) and i not in used;used.add(i)
  assert x['word_sha256']==corpus[i]['sha256'] and x['source']==corpus[i]['source'] and x['index']==corpus[i]['index']
  q=F(x['weight']);assert q>0;weights[i]=q
 assert len(used)==cert['support_size']==39 and sum(weights)==1
 assert math.lcm(*(q.denominator for q in weights if q))==cert['common_denominator']==300531
 balance=[]
 for row in rows:
  mapping=dict(data['mappings'][row['motion']]);assert [mapping[x] for x in row['source']]==row['image']
  balance.append(sum(weights[i]*(int(pattern(words[i],row['source'])==row['pattern'])-
                                 int(pattern(words[i],row['image'])==row['pattern']))
                      for i in range(len(words))))
 assert balance==[0]*50 and cert['exact_row_balances']==['0']*50
 # Audit the complete original domains for this exact mixture, not its support atoms.
 motion_audit=[]
 for j,(name,mapping_pairs) in enumerate(zip(data['motions'],data['mappings'])):
  source=[a for a,b in mapping_pairs];target=[b for a,b in mapping_pairs]
  net={};sm={};tm={};source_types=set();target_types=set()
  for i,q in enumerate(weights):
   if not q:continue
   w=words[i];ps=pattern(w,source);pt=pattern(w,target)
   source_types.add(ps);target_types.add(pt)
   sm[ps]=sm.get(ps,F(0))+q;tm[pt]=tm.get(pt,F(0))+q
   net[ps]=net.get(ps,F(0))+q;net[pt]=net.get(pt,F(0))-q
  residuals={p:q for p,q in net.items() if q}
  if residuals:
   first=min(residuals)
   first_residual=dict(pattern=first,source_mass=str(sm.get(first,F(0))),
                       image_mass=str(tm.get(first,F(0))),source_minus_image=str(residuals[first]))
   status='UNBALANCED'
  else:first_residual=None;status='BALANCED'
  motion_audit.append(dict(motion=j,name=name,domain_size=len(mapping_pairs),status=status,
      source_partition_types=len(source_types),image_partition_types=len(target_types),
      nonzero_partition_residual_count=len(residuals),first_residual=first_residual))
 audit=dict(schema='g14-face-port4-full15-audit-v1',geometry_semantic_sha256=cert['geometry_semantic_sha256'],
      law_support_size=cert['support_size'],law_denominator=cert['common_denominator'],motions=motion_audit,
      scope='Exact complete-partition marginal comparison for the final39-atom law, one pattern residual per unbalanced original full domain; no full15 law claim.')
 audit['audit_sha256']=sha(canonical(audit))
 assert cert['full15_domain_audit']==audit
 return weights,audit

def mutation_tests(cert,data,nodes,rows):
 rejected=[]
 def must_fail(name,c):
  try:validate_certificate(c,data,nodes,rows)
  except (AssertionError,ValueError,IndexError,KeyError,TypeError):rejected.append(name)
  else:raise AssertionError('mutation accepted: '+name)
 for name,change in [
  ('negative-weight',lambda c:c['weights'][0].__setitem__('weight','-1')),
  ('changed-weight',lambda c:c['weights'][0].__setitem__('weight',str(F(c['weights'][0]['weight'])+1))),
  ('missing-support-word',lambda c:c['weights'][0].__setitem__('word_id',999999)),
  ('changed-source-image-map',lambda c:c['four_port_basis']['rows'][0]['image'].__setitem__(0,c['four_port_basis']['rows'][0]['image'][0]+1)),
  ('altered-color-edge',lambda c:(
      c['whole_Y_word_corpus'][0].__setitem__('word',c['whole_Y_word_corpus'][0]['word'][:data['edges'][0][1]]+c['whole_Y_word_corpus'][0]['word'][data['edges'][0][0]]+c['whole_Y_word_corpus'][0]['word'][data['edges'][0][1]+1:]),
      c['whole_Y_word_corpus'][0].__setitem__('sha256',sha(c['whole_Y_word_corpus'][0]['word'].encode())),
      c.__setitem__('word_corpus_sha256',sha(canonical(c['whole_Y_word_corpus']))))),
 ]:
  c=copy.deepcopy(cert);change(c);must_fail(name,c)
 assert len(rejected)==5
 return rejected

def main():
 root=Path(__file__).resolve().parents[1]
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--certificate',type=Path,default=root/'certificates/g14_pair_port4_common_law.json.gz')
 ap.add_argument('--pair-basis',type=Path,default=root/'certificates/g14_pair_orbit_basis.json.gz')
 ap.add_argument('--write-receipt',action='store_true')
 a=ap.parse_args()
 sys.path.insert(0,str(root/'research'))
 global multiplication_twice,product_twice,conjugate_twice
 from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice
 from audit_full_law_preparation import reconstruct
 cert=read(a.certificate);cert_sha=cert.pop('certificate_sha256');assert cert_sha==sha(canonical(cert));cert['certificate_sha256']=cert_sha
 B=read(a.pair_basis);pairsha=B['basis_sha256'];assert cert['pair_basis']['basis_sha256']==pairsha
 data,summary=reconstruct(root);semantic=summary['semantic_sha256'];assert semantic==cert['geometry_semantic_sha256']
 g14path=root/'certificates/g14_port_or_certificate.json'
 g14=read(g14path);assert g14['actual_Y_embedding']['semantic_sha256']==semantic
 g14raw=g14path.read_bytes();expected_g14=cert['pair_basis']['source_g14_legacy_sha256']
 if sha(g14raw)!=expected_g14:
  legacy=copy.deepcopy(g14)
  legacy.get('actual_Y_embedding',{}).pop('semantic_sha256',None)
  legacy_raw=(json.dumps(legacy,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
  assert sha(legacy_raw)==expected_g14
 assert B['source_g14_certificate_sha256']==expected_g14
 nodes,transitions=validate_pair_basis(data,B,g14)
 rows=cert['four_port_basis']['rows'];assert cert['four_port_basis']['row_count']==50
 assert cert['four_port_basis']['basis_sha256']==sha(canonical(rows))
 validate_port4_rows(data,rows,cert['four_port_basis']['basis_sha256'])
 weights,full15_audit=validate_certificate(cert,data,nodes,rows)
 mutations=mutation_tests(cert,data,nodes,rows)
 report=dict(status='PASS_EXACT_COMMON_LAW_ON_G14_FACE',geometry_semantic_sha256=semantic,geometry_reconstructed=True,
  certificate_sha256=cert_sha,pair_basis_sha256=pairsha,port4_basis_sha256=cert['four_port_basis']['basis_sha256'],
  g14_legacy_source_sha256=expected_g14,pair_orbit_nodes={g:len(v) for g,v in nodes.items()},pair_orbit_forest_rows=2638,
  pair_map_transitions_checked=transitions,whole_Y_words=len(cert['whole_Y_word_corpus']),whole_Y_edge_checks=81*len(data['edges']),
  support_size=sum(bool(x) for x in weights),common_denominator=cert['common_denominator'],exact_port4_rows=50,
  exact_pair_orbit_rows=2638,mutation_tests_rejected=mutations,
  full15_domain_balance={x['name']:x['status'] for x in full15_audit['motions']},
  full15_first_residuals={x['name']:x['first_residual']['source_minus_image'] for x in full15_audit['motions']},
  scope=cert['scope'])
 receipt=root/'certificates/g14_pair_port4_common_verification.json'
 if a.write_receipt:receipt.write_text(json.dumps(report,indent=2)+'\n')
 else:assert canonical(read(receipt))==canonical(report), 'Common-law receipt differs from fresh replay'
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
