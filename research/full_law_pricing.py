"""Support-free full-partition pricing; every verdict has an explicit scope.

Search dependencies are loaded only by the search functions. The standard-
library verifier never imports this producer. All fifteen domains are kept;
unseen pattern potentials are zero, but new rows are never discarded.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import math
import platform
import time


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def shape(values):
    labels = {}
    return bytes(labels.setdefault(x, len(labels)) for x in values)


def column(word, maps):
    return [(shape(word[i] for i, j in mm), shape(word[j] for i, j in mm))
            for mm in maps]


def matrix(columns):
    from scipy.sparse import coo_matrix
    keys = sorted({(j, p) for col in columns for j, ab in enumerate(col) for p in ab})
    lookup = {key: i for i, key in enumerate(keys)}
    rows, cols, vals = [], [], []
    for c, col in enumerate(columns):
        for j, (a, b) in enumerate(col):
            if a != b:
                rows.extend((lookup[j, a], lookup[j, b]))
                cols.extend((c, c)); vals.extend((1, -1))
    return keys, coo_matrix((vals, (rows, cols)), shape=(len(keys), len(columns))).tocsc()


def propose_master(columns, dense=False):
    """Floating LP proposes only; exact rational tests authorize the result."""
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import hstack, vstack
    keys, d = matrix(columns)
    r, n = d.shape
    if dense:
        lp = linprog(np.r_[np.zeros(r), -1.0],
                     A_ub=hstack([-d.T, np.ones((n, 1))]), b_ub=np.zeros(n),
                     bounds=[(-1, 1)] * r + [(None, None)], method='highs')
        proposed = lp.x[:-1] if lp.success and lp.x[-1] > 1e-8 else None
    else:
        lp = linprog(np.ones(2*r), A_ub=hstack([-d.T, d.T]),
                     b_ub=-np.ones(n), bounds=(0, None), method='highs')
        proposed = lp.x[:r] - lp.x[r:] if lp.success else None
    if proposed is not None:
        qs = [Fraction(float(x)).limit_denominator(10**6) for x in proposed]
        den = math.lcm(*(x.denominator for x in qs))
        ints = [int(x*den) for x in qs]; g = math.gcd(*ints)
        if g:
            y = {key: value//g for key, value in zip(keys, ints) if value}
            values = [sum(y.get((j,a),0)-y.get((j,b),0)
                          for j,(a,b) in enumerate(col)) for col in columns]
            if min(values) > 0:
                return dict(kind='EXACT_POOL_SEPARATOR', y=y, values=values, keys=keys)
    lp = linprog(np.zeros(n), A_eq=vstack([d, np.ones((1,n))]),
                 b_eq=np.r_[np.zeros(r),1.0], bounds=(0,None), method='highs')
    if lp.success:
        weights = [Fraction(float(x)).limit_denominator(10**7) for x in lp.x]
        if all(x>=0 for x in weights) and sum(weights)==1:
            balance=Counter()
            for col,w in zip(columns,weights):
                for j,(a,b) in enumerate(col):
                    balance[j,a]+=w; balance[j,b]-=w
            if not any(balance.values()):
                return dict(kind='EXACT_POSITIVE_LAW', weights=[str(x) for x in weights], keys=keys)
    return dict(kind='NUMERICAL_MASTER_UNRESOLVED', keys=keys)


class PatternCNF:
    """Reified whole partitions using equality forests and distinct block roots."""
    def __init__(self, n, edges, k=5):
        self.n=n; self.k=k; self.top=n*k; self.eq={}; self.events={}; self.clauses=[]
        for i in range(n):
            vs=[self.color(i,c) for c in range(k)]
            self.clauses.append(vs)
            self.clauses.extend([-a,-b] for a,b in combinations(vs,2))
        self.clauses.extend([-self.color(i,c),-self.color(j,c)]
                            for i,j in edges for c in range(k))

    def color(self,i,c): return i*self.k+c+1
    def fresh(self): self.top+=1; return self.top

    def equality(self,i,j):
        key=tuple(sorted((i,j)))
        if key not in self.eq:
            e=self.fresh(); self.eq[key]=e
            if i==j: self.clauses.append([e])
            else:
                for c in range(self.k):
                    x,z=self.color(i,c),self.color(j,c)
                    self.clauses.extend([[-x,-z,e],[-e,-x,z]])
        return self.eq[key]

    def event(self,ids,pattern):
        ids=tuple(ids); pattern=bytes(pattern)
        if len(ids)!=len(pattern) or len(set(ids))!=len(ids): raise ValueError('bad event domain')
        if any(not 0<=i<self.n for i in ids) or shape(pattern)!=pattern: raise ValueError('bad pattern')
        key=(ids,pattern)
        if key not in self.events:
            roots={}; terms=[]
            for i,c in zip(ids,pattern):
                if c in roots: terms.append(self.equality(i,roots[c]))
                else: roots[c]=i
            terms.extend(-self.equality(i,j) for i,j in combinations(roots.values(),2))
            e=self.fresh(); self.events[key]=e
            self.clauses.extend([-e,t] for t in terms)
            self.clauses.append([e]+[-t for t in terms])
        return self.events[key]

    def pricing(self,y,maps,target):
        from pysat.card import CardEnc, EncType
        coeff=Counter()
        for (j,p),value in y.items():
            coeff[self.event([i for i,_ in maps[j]],p)]+=value
            coeff[self.event([i for _,i in maps[j]],p)]-=value
        shift=sum(v for v in coeff.values() if v<0)
        literals=[var if value>0 else -var for var,value in coeff.items() for _ in range(abs(value))]
        if len(literals)>50000: raise ValueError('pricing coefficient expansion exceeds declared resource cap')
        bound=target-shift
        if bound<0:
            # Some PySAT bootstrap paths index clause[0]; encode the empty
            # clause as contradictory units without changing satisfiability.
            contradiction=self.fresh();self.clauses.extend([[contradiction],[-contradiction]])
        elif bound<len(literals):
            cnf=CardEnc.atmost(literals,bound,top_id=self.top,encoding=EncType.totalizer)
            self.top=cnf.nv; self.clauses.extend(cnf.clauses)

    def reuse(self,keys,maps,max_unseen_sides):
        """Optional HEURISTIC; failure here is never an all-column obstruction."""
        from pysat.card import CardEnc, EncType
        known=[]
        for j,mm in enumerate(maps):
            patterns=[p for jj,p in keys if jj==j]
            for side in (0,1):
                events=[self.event([ij[side] for ij in mm],p) for p in patterns]
                e=self.fresh(); self.clauses.append([-e]+events)
                self.clauses.extend([-x,e] for x in events); known.append(e)
        cnf=CardEnc.atleast(known,len(known)-max_unseen_sides,top_id=self.top,encoding=EncType.totalizer)
        self.top=cnf.nv; self.clauses.extend(cnf.clauses)

    def decode(self,model):
        pos={x for x in model if x>0}
        return ''.join(str(next(c for c in range(self.k) if self.color(i,c) in pos)) for i in range(self.n))


def encode_potential(y,columns):
    # Reference existing whole patterns, not unverified supplied bit strings.
    refs={}
    for w,col in enumerate(columns):
        for j,ab in enumerate(col):
            for side,p in enumerate(ab): refs.setdefault((j,p),(w,side))
    return [[j,*refs[j,p],v] for (j,p),v in sorted(y.items())]


def run(data, strategy, rounds, budget, output):
    from pysat.solvers import Solver
    import numpy, scipy, pysat
    maps=data['mappings']; words=data['words'][:]
    columns=[column(w,maps) for w in words]; history=[]; start=time.monotonic()
    result=dict(strategy=strategy,round_limit=rounds,conflict_budget_per_query=budget,
                words=words,history=history,status='RUNNING',full_law=None,
                environment=dict(python=platform.python_version(),numpy=numpy.__version__,
                                 scipy=scipy.__version__,python_sat=pysat.__version__,solver='cadical195'))
    for step in range(rounds):
        proposal=propose_master(columns,dense=strategy=='dense')
        if proposal['kind']!='EXACT_POOL_SEPARATOR':
            result['status']=proposal['kind']
            if proposal['kind']=='EXACT_POSITIVE_LAW': result['full_law']=proposal['weights']
            break
        y=proposal['y']; values=proposal['values']
        record=dict(step=step,pool_size=len(words),row_count=len(proposal['keys']),
                    potential=encode_potential(y,columns),pool_values=values,
                    pool_strict_margin=min(values),queries=[])
        print('MASTER',json.dumps({k:v for k,v in record.items() if k not in ('potential','pool_values')}),flush=True)
        enc=PatternCNF(len(data['points']),data['edges'])
        # Negative values are preferred for sparse pricing, but zero is a valid
        # counterexample too. Unsat of target -1 DOES NOT certify separation.
        targets=(-1,0) if strategy=='sparse' else (0,)
        found=None
        for target in targets:
            enc=PatternCNF(len(data['points']),data['edges']); enc.pricing(y,maps,target)
            if strategy=='reuse8': enc.reuse(proposal['keys'],maps,8)
            with Solver(name='cadical195',bootstrap_with=enc.clauses) as solver:
                solver.set_phases([enc.color(i,int(c)) for i,c in enumerate(words[-1])])
                solver.conf_budget(budget); answer=solver.solve_limited()
                q=dict(target=target,answer='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_UNCERTIFIED',
                       restricted_to_reused_patterns=strategy=='reuse8',stats=solver.accum_stats(),
                       variables=enc.top,clauses=len(enc.clauses))
                record['queries'].append(q)
                if answer is True:
                    found=enc.decode(solver.get_model()); break
                if answer is None: break
        if found is None:
            result['status']='PRICING_UNRESOLVED'
            history.append(record); break
        if not all(found[i]!=found[j] for i,j in data['edges']): raise RuntimeError('invalid search word')
        col=column(found,maps)
        value=sum(y.get((j,a),0)-y.get((j,b),0) for j,(a,b) in enumerate(col))
        if value>0 or col in columns: raise RuntimeError('invalid pricing witness')
        keys=set(proposal['keys'])
        new={(j,p) for j,ab in enumerate(col) for p in ab}-keys
        record.update(price=value,new_row_count=len(new),new_word_index=len(words))
        history.append(record); words.append(found); columns.append(col)
        output.write_text(json.dumps(result,separators=(',',':'))+'\n')
        print('COLUMN',json.dumps({k:v for k,v in record.items() if k not in ('potential','pool_values','queries')}),flush=True)
    if result['status']=='RUNNING': result['status']='ROUND_LIMIT_UNKNOWN'
    final=propose_master(columns,dense=False)
    result['final_pool_status']=final['kind']; result['final_row_count']=len(final['keys'])
    if final['kind']=='EXACT_POOL_SEPARATOR':
        result['final_potential']=encode_potential(final['y'],columns);result['final_pool_values']=final['values']
    elif final['kind']=='EXACT_POSITIVE_LAW':
        result['full_law']=final['weights'];result['status']='EXACT_POSITIVE_LAW'
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['scope']='Finite pool cuts and actual counterexample columns only unless exact full_law is provided. No solver UNSAT is certified by this producer.'
    output.write_text(json.dumps(result,separators=(',',':'))+'\n')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache',required=True,type=Path)
    ap.add_argument('--strategy',choices=('dense','sparse','reuse8'),default='sparse')
    ap.add_argument('--rounds',type=int,default=16)
    ap.add_argument('--budget',type=int,default=30000)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    if not 1<=args.rounds<=100 or not 1<=args.budget<=100000: raise SystemExit('out of declared research limits')
    root=Path(__file__).resolve().parents[1]
    data=json.loads(gzip.decompress(args.cache.read_bytes()))
    expected=json.loads((root/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
    if hashlib.sha256(canonical(data)).hexdigest()!=expected: raise SystemExit('cache binding mismatch')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    run(data,args.strategy,args.rounds,args.budget,args.output)


if __name__=='__main__': main()
