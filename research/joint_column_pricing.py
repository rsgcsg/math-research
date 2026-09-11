"""E063: full proper-word SAT pricing for selected mixed quartet laws.

LP proposes candidates only. Positive rational laws require independent replay.
An UNSAT pricing search without a checked proof is never a joint obstruction.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, product
from functools import lru_cache
import argparse
import hashlib
import json
import random
import sys
from quintic_joint_ports import build
from quintic_second_host import multiply, add


def pattern(word,indices):
    labels={}
    return tuple(labels.setdefault(word[i],len(labels)) for i in indices)


PATTERNS=sorted({pattern(w,range(4)) for w in product(range(4),repeat=4)})


def events_for(pts,ids,den,motions,word):
    events=[dict(translation=None,motion=m['name'],pairs=m['mixed_witness']) for m in motions]
    lookup={p:i for i,p in enumerate(pts)};copies=[set(b) for b in ids];rng=random.Random(6301)
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16]
    power=one;translations=[]
    for j in range(1,5):
        power=multiply(power,eta);translations.append((f'one_plus_eta_{j}',add(one,power)))
    z=tuple(Q(x,den) for x in pts[ids[0][64]])
    translations.append(('bridge_shift',add(one,multiply(eta,z))))
    for label,tq in translations:
        assert all((x*den).denominator==1 for x in tq)
        t=tuple(int(x*den) for x in tq)
        mapping=[(i,lookup[q]) for i,p in enumerate(pts)
                 for q in [tuple(x+y for x,y in zip(p,t))] if q in lookup]
        picked=[]
        for _ in range(20000):
            pairs=sorted(rng.sample(mapping,4));left,right=zip(*pairs)
            if any(set(left)<=b or set(right)<=b for b in copies):continue
            if pattern(word,left)==pattern(word,right):continue
            if pairs in picked:continue
            picked.append(pairs)
            if len(picked)==3:break
        print(json.dumps(dict(candidate=label,maximal_domain=len(mapping),mixed_quartets=len(picked))),flush=True)
        for pairs in picked:events.append(dict(translation=list(t),translation_label=label,motion=None,pairs=pairs))
    assert len(events)>3, 'No new mixed event: old constraints are not progress'
    return events


class Encoding:
    def __init__(self,n,edges,events):
        self.top=5*n;self.clauses=[];self.rows=[];self.equalities={};self.indicators={}
        self.clauses += [[5*i+k+1 for k in range(5)] for i in range(n)]
        self.clauses += [[-5*i-k-1,-5*i-l-1] for i in range(n) for k,l in combinations(range(5),2)]
        self.clauses += [[-5*i-k-1,-5*j-k-1] for i,j in edges for k in range(5)]
        for event in events:
            left,right=zip(*event['pairs'])
            for pat in PATTERNS:self.rows.append((self.indicator(left,pat),self.indicator(right,pat)))

    def fresh(self):self.top+=1;return self.top

    def equal(self,i,j):
        key=tuple(sorted((i,j)))
        if key not in self.equalities:
            e=self.fresh();self.equalities[key]=e
            for k in range(5):
                a,b=5*i+k+1,5*j+k+1
                self.clauses += [[-e,-a,b],[-e,-b,a],[-a,-b,e]]
        return self.equalities[key]

    def indicator(self,ids,pat):
        key=(tuple(ids),tuple(pat))
        if key not in self.indicators:
            t=self.fresh();self.indicators[key]=t
            lits=[self.equal(ids[a],ids[b])*(1 if pat[a]==pat[b] else -1) for a,b in combinations(range(4),2)]
            self.clauses += [[-t,l] for l in lits]+[[t]+[-l for l in lits]]
        return self.indicators[key]

    def price(self,y,n,budget):
        from pysat.solvers import Solver
        weights={}
        for w,(a,b) in zip(y,self.rows):
            weights[a]=weights.get(a,0)+w;weights[b]=weights.get(b,0)-w
        terms=sorted([(v if w>0 else -v,abs(w)) for v,w in weights.items() if w],key=lambda x:-x[1])
        bound=sum(-w for w in weights.values() if w<0)
        suffix=[0]*(len(terms)+1)
        for i in reversed(range(len(terms))):suffix[i]=suffix[i+1]+terms[i][1]
        clauses=list(self.clauses);top=self.top;nodes=0
        sys.setrecursionlimit(max(10000,len(terms)*3+100))
        @lru_cache(None)
        def node(i,cap):
            nonlocal top,nodes
            if cap<0:return False
            if cap>=suffix[i]:return True
            nodes+=1
            if nodes>100000:raise OverflowError('weighted encoding limit')
            lit,w=terms[i];hi=node(i+1,cap-w);lo=node(i+1,cap)
            top+=1;v=top
            for prefix,child in [([-v,-lit],hi),([-v,lit],lo)]:
                if child is True:continue
                clauses.append(prefix if child is False else prefix+[child])
            return v
        try:root=node(0,bound)
        except OverflowError:return dict(status='UNKNOWN_ENCODING_LIMIT')
        if root is False:return dict(status='UNSAT_SEARCH_ONLY')
        if root is not True:clauses.append([root])
        with Solver(name='cd19',bootstrap_with=clauses) as solver:
            solver.conf_budget(budget);answer=solver.solve_limited()
            if answer is not True:return dict(status='UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',nodes=nodes)
            model=set(solver.get_model())
            word=''.join(str(next(k for k in range(5) if 5*i+k+1 in model)) for i in range(n))
        return dict(status='SAT',word=word,nodes=nodes)


def column(word,events):
    result=[]
    for e in events:
        left,right=zip(*e['pairs']);a,b=pattern(word,left),pattern(word,right)
        result.extend(int(a==p)-int(b==p) for p in PATTERNS)
    return result


def run(root,rounds=25,budget=20000):
    import numpy as np
    from scipy.optimize import linprog
    raw,pts,ids,edges,den,geometry,motions=build(root)
    parent=json.loads((root/'certificates/quintic_joint_translations.json').read_text())
    words=list(dict.fromkeys(s['word'] for s in parent['stages']))
    events=events_for(pts,ids,den,motions,words[-1]);enc=Encoding(len(pts),edges,events)
    history=[];result=dict(status='UNKNOWN_ROUND_LIMIT')
    for iteration in range(rounds):
        cols=[column(w,events) for w in words];D=np.array(cols,dtype=int).T;m,n=D.shape
        primal=linprog(np.zeros(n),A_eq=np.vstack([np.ones(n),D]),b_eq=[1]+[0]*m,bounds=(0,None),method='highs')
        if primal.success:
            lam=[Q(float(x)).limit_denominator(10**9) for x in primal.x]
            if any(l<0 for l in lam) or sum(lam)!=1 or any(sum(lam[j]*cols[j][i] for j in range(n)) for i in range(m)):
                result=dict(status='UNKNOWN_RATIONAL_EXTRACTION');break
            result=dict(status='RATIONAL_LAW',words=[w for w,l in zip(words,lam) if l],weights=[str(l) for l in lam if l]);break
        dual=linprog([0]*m+[-1],A_ub=np.column_stack([-D.T,np.ones(n)]),b_ub=np.zeros(n),bounds=[(-1,1)]*m+[(None,None)],method='highs')
        if not dual.success:result=dict(status='UNKNOWN_DUAL');break
        y=None
        for scale in (1,2,5,10,20,100):
            candidate=[int(round(scale*x)) for x in dual.x[:-1]]
            if min(sum(a*b for a,b in zip(candidate,col)) for col in cols)>0:
                y=candidate;break
        if y is None:
            result=dict(status='UNKNOWN_DUAL_ROUNDING');break
        priced=enc.price(y,len(pts),budget)
        log=dict(iteration=iteration,columns=n,events=len(events),status=priced['status'])
        if priced['status']=='SAT':
            word=priced['word'];score=sum(a*b for a,b in zip(y,column(word,events)))
            assert score<=0 and all(word[i]!=word[j] for i,j in edges) and word not in words
            log.update(score=score,y=y,word=word);words.append(word)
        history.append(log);print(json.dumps({k:v for k,v in log.items() if k not in ('word','y')}),flush=True)
        if priced['status']!='SAT':result=dict(status=priced['status']);break
    return dict(schema=1,experiment='E063',core_sha256=hashlib.sha256(raw).hexdigest(),geometry=geometry,
                events=events,initial_words=list(dict.fromkeys(s['word'] for s in parent['stages'])),
                history=history,result=result,column_generation_status=result['status'],round_limit=rounds,conflict_budget=budget,
                scope='Selected quartet laws only; not all maximal-map laws of E062; no negative certificate')


def repair_existing(root,data,budget):
    """Try a sufficient one-word positive law; failure carries no negative claim."""
    from pysat.solvers import Solver
    import numpy as np
    from scipy.optimize import linprog
    raw,pts,ids,edges,den,geometry,motions=build(root)
    assert geometry==data['geometry']
    library=data['initial_words']+[s['word'] for s in data['history'] if s['status']=='SAT']
    cols=[column(w,data['events']) for w in library];D=np.array(cols,dtype=int).T;m,n=D.shape
    dual=linprog([0]*m+[-1],A_ub=np.column_stack([-D.T,np.ones(n)]),b_ub=np.zeros(n),
                 bounds=[(-1,1)]*m+[(None,None)],method='highs')
    if dual.success:
        for scale in (1,2,5,10,20,100):
            y=[int(round(scale*x)) for x in dual.x[:-1]]
            margin=min(sum(a*b for a,b in zip(y,c)) for c in cols)
            if margin>0:
                data['library_separator']=dict(y=y,margin=margin,columns=len(library));break
    enc=Encoding(len(pts),edges,data['events'])
    clauses=enc.clauses+[[s*a,-s*b] for a,b in enc.rows for s in (-1,1)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited()
        data['direct_repair']=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',budget=budget)
        if answer is True:
            model=set(solver.get_model())
            word=''.join(str(next(k for k in range(5) if 5*i+k+1 in model)) for i in range(len(pts)))
            assert not any(column(word,data['events'])) and all(word[i]!=word[j] for i,j in edges)
            data.setdefault('result_before_direct_repair',data['result'])
            data['result']=dict(status='RATIONAL_LAW',words=[word],weights=['1'])
    return data


def combine_existing(root,data,budget):
    """Positive-only attempt to retain all five E062 maximal-map laws too."""
    from pysat.solvers import Solver
    raw,pts,ids,edges,den,geometry,motions=build(root)
    assert geometry==data['geometry']
    old=json.loads((root/'certificates/quintic_joint_translations.json').read_text())
    enc=Encoding(len(pts),edges,data['events']);clauses=list(enc.clauses)
    clauses += [[s*a,-s*b] for a,b in enc.rows for s in (-1,1)]
    for m,motion in enumerate(old['motions']):
        def pv(a,b):return enc.top+25*m+5*a+b+1
        clauses += [[pv(a,b) for b in range(5)] for a in range(5)]
        clauses += [[pv(a,b) for a in range(5)] for b in range(5)]
        clauses += [[-pv(a,b),-pv(a,c)] for a in range(5) for b,c in combinations(range(5),2)]
        clauses += [[-pv(a,b),-pv(c,b)] for b in range(5) for a,c in combinations(range(5),2)]
        clauses += [[-5*i-a-1,-pv(a,b),5*j+b+1] for i,j in motion['mapping'] for a in range(5) for b in range(5)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget);answer=solver.solve_limited()
        data['combined_repair']=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',budget=budget)
        if answer is True:
            model=set(solver.get_model())
            word=''.join(str(next(k for k in range(5) if 5*i+k+1 in model)) for i in range(len(pts)))
            data['combined_repair']['permutations']=[[next(b for b in range(5) if enc.top+25*m+5*a+b+1 in model) for a in range(5)] for m in range(5)]
            data.setdefault('result_before_combined_repair',data['result'])
            data['result']=dict(status='RATIONAL_LAW',words=[word],weights=['1'])
            data['scope']='Selected 18 quartet laws together with all five E062 maximal-map laws; not all partial isometries; no HN lower bound'
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--rounds',type=int,default=25);p.add_argument('--budget',type=int,default=20000)
    p.add_argument('--repair-existing',action='store_true')
    p.add_argument('--repair-after',action='store_true')
    p.add_argument('--combine-existing',action='store_true')
    p.add_argument('--combine-after',action='store_true')
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.repair_existing or a.combine_existing:
        assert a.output and a.output.exists()
        data=json.loads(a.output.read_text())
        data=combine_existing(root,data,a.budget) if a.combine_existing else repair_existing(root,data,a.budget)
    else:data=run(root,a.rounds,a.budget)
    if a.repair_after:data=repair_existing(root,data,a.budget)
    if a.combine_after:data=combine_existing(root,data,a.budget)
    print(json.dumps(dict(events=len(data['events']),result=data['result']['status']),indent=2))
    if a.output:a.output.write_text(json.dumps(data,indent=2)+'\n')
