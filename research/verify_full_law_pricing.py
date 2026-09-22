"""Independent E105 checker. Standard library; no LP, SAT, or producer import.

Reconstructs Y and every maximal domain with the existing independent input
checker. Replays strict finite-pool separators and their actual proper-word
counterexamples using sets of equality blocks, not the producer's byte labels.
No computational negative claim about all proper words is accepted here.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
from itertools import product
import gzip
import hashlib
import json
from audit_full_law_preparation import reconstruct, unique_keys
from verify_joint_two_motion_counterexample import verify as verify_toy


def require(ok, why):
    if not ok: raise ValueError(why)


def integer(x): return type(x) is int


def blocks(word, indices):
    groups={}
    for pos,i in enumerate(indices): groups.setdefault(word[i],[]).append(pos)
    return frozenset(frozenset(group) for group in groups.values())


def observed_rows(columns):
    return {(j,p) for col in columns for j,ab in enumerate(col) for p in ab}


def read_potential(records, columns, pool):
    out={}
    require(isinstance(records,list) and records,'empty potential')
    for item in records:
        require(isinstance(item,list) and len(item)==4 and all(map(integer,item)),'potential types')
        j,w,side,value=item
        require(0<=j<15 and 0<=w<pool and side in (0,1) and value!=0,'potential reference')
        key=j,columns[w][j][side]
        require(key not in out,'duplicate potential row')
        out[key]=value
    return out


def score(col, potential):
    return sum(potential.get((j,a),0)-potential.get((j,b),0) for j,(a,b) in enumerate(col))


def check_run(run, data):
    maps=data['mappings']; n=len(data['points']); edges=data['edges']
    require(run['strategy'] in ('dense','sparse','reuse8'),'strategy')
    words=run['words']
    require(isinstance(words,list) and words[:5]==data['words'],'seed changed')
    require(all(isinstance(w,str) and len(w)==n and set(w)<=set('01234') for w in words),'word shape')
    for w in words: require(all(w[i]!=w[j] for i,j in edges),'improper whole word')
    columns=[[(blocks(w,[i for i,_ in mm]),blocks(w,[i for _,i in mm])) for mm in maps] for w in words]
    history=run['history']; pool=5; added_rows=[]; prices=[]; occurrence_novelty=[]
    require(integer(run['round_limit']) and 1<=run['round_limit']<=100,'round limit')
    require(integer(run['conflict_budget_per_query']) and 1<=run['conflict_budget_per_query']<=100000,'budget')
    require(len(history)<=run['round_limit'],'history length')
    for step,h in enumerate(history):
        require(h['step']==step and h['pool_size']==pool,'pool indexing')
        current=observed_rows(columns[:pool]); require(h['row_count']==len(current),'missing complete rows')
        potential=read_potential(h['potential'],columns,pool)
        vals=[score(c,potential) for c in columns[:pool]]
        require(all(map(integer,h['pool_values'])) and h['pool_values']==vals and min(vals)>0,'false pool cut')
        require(integer(h['pool_strict_margin']) and h['pool_strict_margin']==min(vals),'strict margin')
        qs=h['queries']; require(qs and len(qs)<=2,'query log')
        for q in qs:
            require(integer(q['target']) and q['target'] in (-1,0),'query threshold')
            require(q['answer'] in ('SAT','UNKNOWN','UNSAT_UNCERTIFIED'),'unsupported verdict')
            require(q['restricted_to_reused_patterns']==(run['strategy']=='reuse8'),'hidden restriction')
        if 'new_word_index' not in h:
            require(step==len(history)-1 and qs[-1]['answer']!='SAT','missing witness')
            continue
        require(integer(h['new_word_index']) and h['new_word_index']==pool and pool<len(words),'new word reference')
        require(qs[-1]['answer']=='SAT','wrong pricing label')
        col=columns[pool]; value=score(col,potential)
        require(integer(h['price']) and h['price']==value<=qs[-1]['target']<=0,'false price')
        require(col not in columns[:pool],'duplicate complete column')
        new=observed_rows([col])-current
        require(integer(h['new_row_count']) and h['new_row_count']==len(new),'new complete rows dropped')
        unseen=sum((j,p) not in current for j,ab in enumerate(col) for p in ab)
        if run['strategy']=='reuse8': require(unseen<=8,'reuse restriction broken')
        added_rows.append(len(new));prices.append(value);occurrence_novelty.append(unseen);pool+=1
    require(pool==len(words),'unlogged word')
    require(run['final_row_count']==len(observed_rows(columns)),'final row count')
    final=run['final_pool_status']
    if final=='EXACT_POOL_SEPARATOR':
        potential=read_potential(run['final_potential'],columns,pool)
        vals=[score(c,potential) for c in columns]
        require(run['final_pool_values']==vals and all(map(integer,run['final_pool_values'])) and min(vals)>0,'false final pool verdict')
        require(run['full_law'] is None,'contradictory law claim')
    elif final=='EXACT_POSITIVE_LAW':
        require(isinstance(run['full_law'],list) and len(run['full_law'])==pool,'law shape')
        weights=[Fraction(x) for x in run['full_law']]
        require(all(w>=0 for w in weights) and sum(weights)==1,'law weights')
        balance=Counter()
        for col,weight in zip(columns,weights):
            for j,(a,b) in enumerate(col): balance[j,a]+=weight;balance[j,b]-=weight
        require(not any(balance.values()),'false full law')
    else: require(final=='NUMERICAL_MASTER_UNRESOLVED','unsupported final result')
    require(run['status'] in ('ROUND_LIMIT_UNKNOWN','PRICING_UNRESOLVED','EXACT_POSITIVE_LAW','NUMERICAL_MASTER_UNRESOLVED'),'global negative claim not permitted')
    if run['status']=='ROUND_LIMIT_UNKNOWN': require(len(history)==run['round_limit'],'round stop')
    return dict(strategy=run['strategy'],proper_words=pool,new_words=pool-5,whole_edge_checks=pool*len(edges),
                pricing_steps=len(prices),strict_pool_cuts=len(history)+int(final=='EXACT_POOL_SEPARATOR'),
                final_rows=len(observed_rows(columns)),new_rows=added_rows,pricing_values=prices,
                unseen_sides=occurrence_novelty,final_pool_status=final,status=run['status'])


def check_data(cert,data,summary):
    require(cert['schema']=='full-law-pricing-v1' and cert['experiment']=='E105','schema')
    require(cert['base_commit']=='53feae233ab7d781b3ca32242fabfabfb9cde3d4','base')
    require(cert['input_semantic_sha256']==summary['semantic_sha256'],'input binding')
    require(cert['geometry']==summary['geometry'],'geometry binding')
    require(cert['motions']==data['motions'] and len(cert['motions'])==15,'motions changed')
    require([r['strategy'] for r in cert['runs']]==['dense','sparse','reuse8'],'missing run')
    reports=[check_run(run,data) for run in cert['runs']]
    toy=verify_toy(); require(cert['counterexample']==toy,'toy certificate changed')
    calibration=cert['search_calibration']; seen=set()
    for q in calibration['checks']:
        cs=q['coefficients'];target=q['target']
        require(isinstance(cs,list) and len(cs)==4 and all(integer(x) and x in (-1,0,1) for x in cs),'calibration coefficients')
        require(integer(target) and -2<=target<=2 and type(q['satisfiable']) is bool,'calibration query')
        key=(tuple(cs),target);require(key not in seen,'duplicate calibration');seen.add(key)
        # The two complete proper partitions give precisely these two scores.
        require(q['satisfiable']==(min(cs[0]-cs[1],cs[2]-cs[3])<=target),'false calibration result')
    require(seen=={(cs,t) for cs in product((-1,0,1),repeat=4) for t in range(-2,3)},'incomplete calibration')
    masters=calibration['masters']
    require(len(masters)==3 and [m['motions'] for m in masters]==[[0],[1],[0,1]],'calibration master domains')
    for j,m in enumerate(masters[:2]):
        require(m['kind']=='EXACT_POSITIVE_LAW','calibration positive kind')
        weights=[Fraction(x) for x in m['weights']]
        require(len(weights)==4 and all(x>=0 for x in weights) and sum(weights)==1,'calibration positive weights')
        # Labeled words are 0100,0101,1010,1011; E_j imbalance is 0/1.
        imbalance=([0,1,1,0],[1,0,0,1])[j]
        require(sum(w*x for w,x in zip(weights,imbalance))==0,'calibration false positive')
    require(masters[2]['kind']=='EXACT_POOL_SEPARATOR' and masters[2]['values']==[1,1,1,1],'calibration negative values')
    return dict(status='PASS',experiment='E105',geometry=summary['geometry'],runs=reports,counterexample=toy,calibrated_pricing_queries=len(seen),
                full_fifteen_domain_law_found=any(r['final_pool_status']=='EXACT_POSITIVE_LAW' for r in reports),
                all_word_obstruction_certified=False,
                scope='All saved finite-pool inequalities and counterexample columns checked exactly. Search costs are observations; neither stopped pricing nor a final pool cut is an all-word obstruction.')


def verify(root, certificate=None):
    if not __debug__: raise RuntimeError('verification requires assertions')
    path=certificate or root/'certificates/full_law_pricing.json.gz'
    raw=path.read_bytes()
    cert=json.loads(gzip.decompress(raw),object_pairs_hook=unique_keys)
    data,summary=reconstruct(root)
    report=check_data(cert,data,summary)
    report['certificate_sha256']=hashlib.sha256(raw).hexdigest()
    return report


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),ensure_ascii=False,indent=2))
