#!/usr/bin/env python3
"""Independent stdlib certificate check for the exact frozen-basis 4-port law."""
import argparse,copy,gzip,hashlib,itertools,json,math,sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];EXP=ROOT/'certificates'
sys.path.insert(0,str(ROOT/'research'))
from audit_full_law_preparation import canonical,reconstruct,unique_keys
from verify_eta_joined_law import expand_compact
from verify_event_pricing import bind_events,check_word,rebuild,score

def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw,object_pairs_hook=unique_keys),raw
def sha(x):return hashlib.sha256(x).hexdigest()
def rgs(n):
 out=[]
 def rec(p,top):
  if len(p)==n:
   if len(set(p))<=5:out.append(''.join(map(str,p)))
   return
  for x in range(top+2):rec(p+[x],max(top,x))
 rec([0],0);return out
def pattern(word,ids):
 labels={};return ''.join(str(labels.setdefault(word[x],len(labels))) for x in ids)
def rle(word,ids):return tuple(int(x) for x in pattern(word,ids))

def validate_law(state,records,words,data,basis):
 if not __debug__:raise RuntimeError('verification requires assertions')
 assert state['schema']=='port4-exact-rational-law-v1'
 assert state['status']=='EXACT_RATIONAL_4PORT_LAW' and len(records)==len(words)==75 and len(basis)==50
 assert state['whole_Y_proper_words']==75 and state['support_size']==47
 assert state['basis_sha256']==sha(canonical(basis))
 for i,word in enumerate(words):
  assert len(word)==10077 and set(word)<=set('01234') and sha(word.encode())==records[i]['sha256']
  assert all(word[a]!=word[b] for a,b in data['edges'])
 weights=[Fraction(0) for _ in records];seen_ids=set()
 for item in state['weights']:
  i=item['word_id'];assert type(i) is int and 0<=i<len(records) and i not in seen_ids
  seen_ids.add(i)
  assert item['sha256']==records[i]['sha256'] and item['source']==records[i]['source'] and item['source_index']==records[i]['index']
  q=Fraction(item['weight']);assert q>=0;weights[i]=q
 assert sum(weights)==1 and sum(bool(q) for q in weights)==47
 for row in basis:
  j=row['motion'];mapping=dict(data['mappings'][j])
  assert all(x in mapping for x in row['source']) and [mapping[x] for x in row['source']]==row['image']
 balances=[]
 for row in basis:
  balances.append(sum(weights[i]*(int(pattern(words[i],row['source'])==row['pattern'])-
                                  int(pattern(words[i],row['image'])==row['pattern']))
                      for i in range(len(words))))
 assert balances==[0]*50 and state['row_balances']==['0']*50
 return weights
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--check-certificate',type=Path,
                     help='require the fresh report to equal this saved JSON receipt')
 args=parser.parse_args()
 if not __debug__:raise RuntimeError('verification requires assertions')
 data,summary=reconstruct(ROOT)
 receipt=json.loads((ROOT/'certificates/full_law_preparation_audit.json').read_text())
 assert canonical(summary)==canonical(receipt['independent_inputs'])
 semantic=sha(canonical(data));assert semantic==summary['semantic_sha256']
 state,state_raw=read(EXP/'port4_exact_rational_law.json')
 assert state['status']=='EXACT_RATIONAL_4PORT_LAW'
 # Source corpus order is fixed by the driver and bound to original certificate bytes.
 portfolio,praw=read(ROOT/'certificates/Y_pair_portfolio.json.gz')
 full_law,flraw=read(ROOT/'certificates/full_law_pricing.json.gz')
 e111,e111raw=read(ROOT/'certificates/shared_event_research.json.gz')
 e115neg,nraw=read(ROOT/'certificates/joined_seed_negative_probe.json')
 compact,craw=read(ROOT/'certificates/eta_joined_three_compact.json.gz')
 e115,e115raw=read(ROOT/'certificates/joined_seed_pricing.json.gz')
 source_hashes={'branch56':sha(praw),'E083':sha(flraw),'E111':sha(e111raw),
                'E115_negative_price':sha(nraw),'S3':sha(craw),'E115_pool':sha(e115raw)}
 assert portfolio['input_semantic_sha256']==semantic and e111['input_semantic_sha256']==semantic
 assert e115neg['cache_semantic_sha256']==semantic and full_law['input_semantic_sha256']==semantic
 assert full_law['runs'][0]['words'][:5]==data['words'] and e115['input_semantic_sha256']==semantic
 s_words=expand_compact(compact,data,summary)['words']
 records=[];seen=set()
 for src,items in [('branch56',portfolio['words']),('E083',data['words']),('E111',[e111['positive_word']]),
                   ('E115_negative_price',[e115neg['word']]),('S3',s_words)]:
  for ix,w in enumerate(items):
   if w not in seen:records.append(dict(source=src,index=ix,word=w));seen.add(w)
 for ix,w in enumerate(e115['run']['words']):
  if w not in seen:records.append(dict(source='E115_pool',index=ix,word=w));seen.add(w)
 # Add all six validated SAT counterwords, preserving order and source names.
 price_results=[('pricing_'+Path('port4_pricing_result').stem,EXP/'port4_pricing_result.json')]
 for path in sorted(EXP.glob('port4_round_*_result.json')):
  price_results.append(('pricing_'+path.stem,path))
 pricing_reports=[]
 for src,path in price_results:
  result,rraw=read(path);assert result['status']=='SAT_WITNESS'
  req=result['request'];assert req['target']==0
  events=bind_events(req['events'],data['mappings'])
  instance=dict(n=len(data['points']),k=5,edges=data['edges'],events=events)
  built=rebuild(**instance,coeff=req['coefficients'],target=0)
  assert built['cnf_sha256']==result['cnf_sha256']
  w=result['word'];check_word(w,len(data['points']),5,data['edges'])
  value=score(w,events,req['coefficients']);assert value==result['value']<=0
  h=sha(w.encode());assert h not in seen
  rec=dict(source=src,index=0,word=w);records.append(rec);seen.add(w)
  pricing_reports.append(dict(source=src,result_sha256=sha(rraw),word_sha256=h,exact_score=value,
                              event_terms=len(events),CNF_sha256=built['cnf_sha256']))
 words=[r['word'] for r in records];assert len(words)==75 and len(set(words))==75
 # Recheck every proper coloring atom against all actual induced edges.
 edge_set=data['edges']
 for rec in records:
  w=rec['word'];assert len(w)==10077 and set(w)<=set('01234')
  assert all(w[a]!=w[b] for a,b in edge_set)
  rec['sha256']=sha(w.encode())
 # Rebuild the exact immutable four-port basis.
 ports=[(8,(3604,3817,4114,4641)),(7,(3484,6700,7219,9104)),
        (3,(3748,3797,4513,5158)),(14,(233,239,9425,9951))]
 basis=[];edge={tuple(e) for e in edge_set}
 for j,T in ports:
  mapping=dict(data['mappings'][j]);image=[mapping[x] for x in T]
  assert all(x in mapping for x in T)
  for p in rgs(4):
   if all(not(p[a]==p[b] and tuple(sorted((T[a],T[b]))) in edge)
          for a,b in itertools.combinations(range(4),2)):
    basis.append(dict(motion=j,source=list(T),image=image,pattern=p))
 assert len(basis)==50
 basis_hash=sha(canonical(basis));assert basis_hash==state['basis_sha256']
 saved_basis,braw=read(EXP/'port4_exact_rational_basis.json')
 assert saved_basis['basis_sha256']==basis_hash and saved_basis['rows']==basis
 # Verify all listed rational weights and exact row equations.
 weights=validate_law(state,records,words,data,basis)
 # Targeted mutation rejection: the checker must fail closed on corrupted proofs.
 mutation_names=[]
 mutations=[
  ('negative-weight',lambda st,ws,bs:st['weights'][0].__setitem__('weight','-1')),
  ('changed-weight',lambda st,ws,bs:st['weights'][0].__setitem__('weight',str(Fraction(st['weights'][0]['weight'])+1))),
  ('changed-source-image-map',lambda st,ws,bs:bs[0]['image'].__setitem__(0,bs[0]['image'][0]+1)),
  ('missing-support-word',lambda st,ws,bs:st['weights'][0].__setitem__('word_id',999999)),
  ('altered-color-edge',lambda st,ws,bs:ws.__setitem__(st['weights'][0]['word_id'],
      ws[st['weights'][0]['word_id']][:data['edges'][0][1]]+
      ws[st['weights'][0]['word_id']][data['edges'][0][0]]+
      ws[st['weights'][0]['word_id']][data['edges'][0][1]+1:])),
 ]
 for name,mutate in mutations:
  st=copy.deepcopy(state);ws=list(words);bs=copy.deepcopy(basis);mutate(st,ws,bs)
  try:validate_law(st,records,ws,data,bs)
  except (AssertionError,ValueError,IndexError,KeyError,TypeError):mutation_names.append(name)
  else:raise AssertionError('mutation unexpectedly accepted: '+name)
 assert len(mutation_names)==len(mutations)
 denominator=math.lcm(*(q.denominator for q in weights if q))
 assert denominator==state['common_denominator']==184246020
 # Determine whether the 75-word law also satisfies any entire original domain.
 full_equal=[]
 for j,mapping in enumerate(data['mappings']):
  source=[a for a,b in mapping];target=[b for a,b in mapping]
  bal=Counter()
  for i,w in enumerate(words):
   if weights[i]:
    bal[pattern(w,source)]+=weights[i];bal[pattern(w,target)]-=weights[i]
  if not any(bal.values()):full_equal.append(j)
 report=dict(status='PASS_EXACT_RATIONAL_4PORT_LAW',geometry_reconstructed=True,
   geometry_semantic_sha256=semantic,source_certificate_sha256=source_hashes,
   basis_sha256=basis_hash,ports=[dict(motion=j,source=list(T),image=[dict(data['mappings'][j])[x] for x in T]) for j,T in ports],
   legal_pattern_rows=50,whole_Y_proper_words=len(words),support_size=sum(bool(q) for q in weights),
   whole_edge_checks=len(words)*len(edge_set),common_denominator=denominator,
   mutation_tests_rejected=mutation_names,
   exact_row_balances=['0']*50,pricing_counterwords=pricing_reports,
   full_original_domains_balanced=full_equal,
   scope=('An exact common law for these four selected 4-port complete-pattern marginals only. '
          'This is not a joint law on the four full domains, not a full15 law, and not an HN bound.'))
 if args.check_certificate:
  saved=json.loads(args.check_certificate.read_text(encoding='utf-8'))
  if saved!=report:raise ValueError('saved four-port report differs from fresh exact replay')
  print('PASS: saved certificate exactly matches fresh replay',args.check_certificate)
 else:
  out=EXP/'port4_exact_law_verification.json'
  out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
  print('PASS',out)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
