"""Exact lazy fixed-support full-joint search; no frozen words or operators.

Search only. SAT is accepted only after the independent whole-domain checker.
UNSAT concerns the chosen support size; bounded solver failure is UNKNOWN.
"""
from collections import Counter
from itertools import combinations, product, permutations
from pathlib import Path
import argparse
import hashlib
import json
import time


def pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


class PairJointEncoding:
    def __init__(self, n, edges, mappings, m=5, k=5):
        self.n, self.m, self.k = n, m, k
        self.maps = mappings
        self.top = n*m*k
        self.equalities = {}
        self.cuts = set()
        self.clauses = []
        for a in range(m):
            for i in range(n):
                self.one([self.color(a, i, c) for c in range(k)], self.clauses)
            for i, j in edges:
                self.clauses.extend([[-self.color(a,i,c), -self.color(a,j,c)] for c in range(k)])
        self.sigma = []
        for mapping in mappings:
            matrix = [[self.fresh() for b in range(m)] for a in range(m)]
            for row in matrix + list(map(list, zip(*matrix))):
                self.one(row, self.clauses)
            self.sigma.append(matrix)

    def fresh(self):
        self.top += 1
        return self.top

    def color(self, a, i, c):
        return (a*self.n+i)*self.k+c+1

    @staticmethod
    def one(vs, clauses):
        clauses.append(list(vs))
        clauses.extend([[-v,-w] for v,w in combinations(vs,2)])

    def equal(self, a, i, j, clauses):
        if i == j:
            key = (a,i,j)
            if key not in self.equalities:
                e = self.fresh(); self.equalities[key] = e; clauses.append([e])
            return self.equalities[key]
        i,j = sorted((i,j)); key = (a,i,j)
        if key not in self.equalities:
            e = self.fresh(); self.equalities[key] = e
            for c in range(self.k):
                x,y = self.color(a,i,c),self.color(a,j,c)
                clauses.extend([[-x,-y,e],[-e,-x,y]])
        return self.equalities[key]

    def add_pair(self, t, p, q):
        p,q = sorted((p,q)); key = (t,p,q)
        if key in self.cuts:
            raise AssertionError('a previously imposed cut was violated')
        self.cuts.add(key)
        i,j = self.maps[t][p]; u,v = self.maps[t][q]
        clauses = []
        left = [self.equal(a,i,u,clauses) for a in range(self.m)]
        right = [self.equal(b,j,v,clauses) for b in range(self.m)]
        for a in range(self.m):
            for b in range(self.m):
                s = self.sigma[t][a][b]
                clauses.extend([[-s,-left[a],right[b]],[-s,left[a],-right[b]]])
        return clauses

    def decode(self, model):
        positive = {v for v in model if v > 0}
        words = [''.join(str(next(c for c in range(self.k) if self.color(a,i,c) in positive))
                         for i in range(self.n)) for a in range(self.m)]
        sigma = [[next(b for b in range(self.m) if matrix[a][b] in positive)
                  for a in range(self.m)] for matrix in self.sigma]
        return words, sigma


def violated_pairs(words, sigma, mappings, cap=3):
    """Return genuine pair obstructions to each selected FULL partition match."""
    out = set()
    for t, mapping in enumerate(mappings):
        for a,b in enumerate(sigma[t]):
            left, right = {}, {}
            found = 0
            for p,(i,j) in enumerate(mapping):
                x,y = words[a][i],words[b][j]
                for here,key,other in ((left,x,y),(right,y,x)):
                    if key in here and here[key][0] != other:
                        q = here[key][1]
                        out.add((t,min(p,q),max(p,q)))
                        found += 1
                    else:
                        here.setdefault(key,(other,p))
                if found >= cap:
                    break
    return sorted(out)


def complete_result(words, sigma, mappings, k):
    palettes=[]
    for t,mapping in enumerate(mappings):
        pp=[]
        for a,b in enumerate(sigma[t]):
            rel={}
            for i,j in mapping:
                x,y=int(words[a][i]),int(words[b][j])
                if x in rel and rel[x]!=y:
                    raise ValueError('inconsistent palette')
                rel[x]=y
            if len(set(rel.values()))!=len(rel):
                raise ValueError('noninjective palette')
            remaining=iter(sorted(set(range(k))-set(rel.values())))
            pp.append([rel[c] if c in rel else next(remaining) for c in range(k)])
        palettes.append(pp)
    return dict(words=words,word_permutations=sigma,color_permutations=palettes)


def solve(n,edges,maps,m,k,budget,rounds,seconds,hints=None,anchors=(),verbose=True,stages=None):
    from pysat.solvers import Solver
    enc=PairJointEncoding(n,edges,maps,m,k)
    for a in range(m):
        for i,c in anchors:
            enc.clauses.append([enc.color(a,i,c)])
    start=time.monotonic(); history=[]; result=None; status='UNKNOWN'
    stages=list(stages or [len(maps)]); stage=0; active=stages[0]; checkpoints=[]
    with Solver(name='cadical195',bootstrap_with=enc.clauses) as solver:
        del enc.clauses
        if hints:
            solver.set_phases([enc.color(a,i,int(c)) for a,w in enumerate(hints) for i,c in enumerate(w)])
        for step in range(rounds):
            remaining=budget-solver.accum_stats()['conflicts']
            if remaining<=0 or time.monotonic()-start>=seconds:
                break
            solver.conf_budget(min(remaining,10000))
            answer=solver.solve_limited()
            stats=solver.accum_stats()
            if answer is not True:
                status='UNKNOWN' if answer is None else 'UNSAT_FIXED_SUPPORT_UNCERTIFIED'
                history.append(dict(round=step,active_domains=active,solver_status=status,stats=stats))
                if verbose:print('SOLVER '+json.dumps(history[-1]),flush=True)
                if answer is None:continue
                break
            words,sigma=enc.decode(solver.get_model())
            cuts=violated_pairs(words,sigma[:active],maps[:active])
            entry=dict(round=step,active_domains=active,new_pairs=len(cuts),total_pairs=len(enc.cuts),
                       equality_variables=len(enc.equalities),variables=enc.top,
                       conflicts=stats['conflicts'],elapsed_seconds=round(time.monotonic()-start,3))
            history.append(entry)
            if verbose:
                print('CEGAR '+json.dumps(entry),flush=True)
            if not cuts:
                result=complete_result(words,sigma[:active],maps[:active],k)
                result['full_domain_count']=active
                checkpoints.append(dict(domains=active,round=step,conflicts=stats['conflicts']))
                if verbose:print('CHECKPOINT '+json.dumps(checkpoints[-1]),flush=True)
                if stage+1==len(stages):status='SAT';break
                stage+=1;active=stages[stage]
                continue
            for t,p,q in cuts:
                solver.append_formula(enc.add_pair(t,p,q))
        stats=solver.accum_stats()
    return dict(status=status,result=result,history=history,stats=stats,checkpoints=checkpoints,
                generated_pairs=len(enc.cuts),equality_variables=len(enc.equalities),
                elapsed_seconds=round(time.monotonic()-start,3))


def calibration():
    maps=[[(0,1),(1,0),(2,2)]]
    reports=[]
    for m in (1,2):
        answer=solve(3,[(0,1)],maps,m,2,10000,100,30,verbose=False)
        assert (answer['status']=='SAT')==(m==2)
        if m==1:
            assert answer['status']=='UNSAT_FIXED_SUPPORT_UNCERTIFIED'
        if m==2:
            rr=answer['result'];ws=rr['words']
            assert all(w[0]!=w[1] for w in ws)
            assert Counter(pattern(w,[0,1,2]) for w in ws)==Counter(pattern(w,[1,0,2]) for w in ws)
        reports.append(dict(support=m,status=answer['status'],pairs=answer['generated_pairs']))
    # Reified equality truth table independent of the solver.
    for k in (2,3,5):
        for x,y,e in product(range(k),range(k),(False,True)):
            clauses=[(x!=c or y!=c or e) and (not e or x!=c or y==c) for c in range(k)]
            assert all(clauses)==(e==(x==y))
    print('CALIBRATION '+json.dumps(reports),flush=True)


def run(root,budget=300000,rounds=250,seconds=600):
    from dyadic_mixed_return_joint import prepare
    calibration()
    parent,context,old,algebra,mapping,definitions,maps=prepare(root)
    # All old fourteen domains, u29, the real reflected 33-domain, and u^2 805.
    one,eta,z,u,bar,mul=algebra
    definitions.append(('dyadic_u_squared',mul(u,u),tuple(0 for _ in one),False))
    maps.append(mapping(mul(u,u)))
    definitions[-2],definitions[-1]=definitions[-1],definitions[-2]
    maps[-2],maps[-1]=maps[-1],maps[-2]
    assert len(maps)==17 and len(maps[-2])==805
    lookup={p:i for i,p in enumerate(context['points'])}
    anchors=[(lookup[context['ring']['blocks'][0][j]],c) for c,j in enumerate((0,153,150))]
    print('GEOMETRY '+json.dumps(parent['geometry']),flush=True)
    print('DOMAINS '+json.dumps([(d[0],len(mm)) for d,mm in zip(definitions,maps)]),flush=True)
    answer=solve(len(context['points']),context['edges'],maps,5,5,budget,rounds,seconds,
                 old['result']['words'],anchors,stages=[15,16,17])
    result=answer.pop('result')
    if result:
        count=result['full_domain_count']
        result['motions']=[d[0] for d in definitions[:count]]
        result['mapping_sha256']=[hashlib.sha256(json.dumps(mm,separators=(',',':')).encode()).hexdigest() for mm in maps[:count]]
    data=dict(schema=1,experiment='E097',support=5,colors=5,
              geometry=parent['geometry'],search=answer,result=result,
              scope='Exact full-partition CEGAR at fixed support five; no plane bound or all-support negative claim')
    path=root/'certificates/joint_pair_cegar.json'
    path.write_text(json.dumps(data,indent=2)+'\n')
    print('SEARCH_SUMMARY '+json.dumps({k:v for k,v in answer.items() if k!='history'}),flush=True)
    return data


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--calibration',action='store_true')
    ap.add_argument('--budget',type=int,default=300000);ap.add_argument('--rounds',type=int,default=250)
    ap.add_argument('--seconds',type=int,default=600);args=ap.parse_args()
    if args.calibration:calibration()
    else:run(Path(__file__).resolve().parents[1],args.budget,args.rounds,args.seconds)
