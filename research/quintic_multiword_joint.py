"""Free equal-weight joint supports; bounded failure is never all-word failure.

Each motion has its own support permutation and each source word its own color
permutation. No group relations between those permutations are imposed.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import json
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import conjugate_twice,digest


class MultiwordEncoding:
    def __init__(self,n,edges,m,k=5):
        self.n=n;self.m=m;self.k=k;self.top=n*m*k
        self.clauses=[];self.witness_vars=[]
        for a in range(m):
            for i in range(n):self.exactly_one([self.color(a,i,c) for c in range(k)],self.clauses)
            self.clauses.extend([-self.color(a,i,c),-self.color(a,j,c)] for i,j in edges for c in range(k))

    def color(self,a,i,c):return (a*self.n+i)*self.k+c+1
    def fresh(self):self.top+=1;return self.top

    @staticmethod
    def exactly_one(variables,clauses):
        clauses.append(list(variables));clauses.extend([-a,-b] for a,b in combinations(variables,2))

    def permutation(self,size,clauses):
        matrix=[[self.fresh() for _ in range(size)] for _ in range(size)]
        for line in matrix+list(map(list,zip(*matrix))):self.exactly_one(line,clauses)
        return matrix

    def add_motion(self,mapping):
        clauses=[];sigma=self.permutation(self.m,clauses)
        pi=[self.permutation(self.k,clauses) for _ in range(self.m)]
        for a in range(self.m):
            for i,j in mapping:
                target=[self.fresh() for _ in range(self.k)]
                for b in range(self.m):
                    for color in range(self.k):
                        old=self.color(b,j,color);new=target[color];select=sigma[a][b]
                        clauses.extend([[-select,-old,new],[-select,old,-new]])
                for source in range(self.k):
                    clauses.extend([-self.color(a,i,source),-pi[a][source][dest],target[dest]]
                                   for dest in range(self.k))
        self.witness_vars.append((sigma,pi));return clauses

    def decode(self,model):
        positive={v for v in model if v>0}
        words=[''.join(str(next(c for c in range(self.k) if self.color(a,i,c) in positive))
                       for i in range(self.n)) for a in range(self.m)]
        def perm(matrix):return [next(i for i,v in enumerate(row) if v in positive) for row in matrix]
        return dict(words=words,word_permutations=[perm(s) for s,p in self.witness_vars],
                    color_permutations=[[perm(p) for p in palettes] for s,palettes in self.witness_vars])


def calibration():
    from pysat.solvers import Solver
    results=[]
    for m in [1,2]:
        # Three collinear points 0,1,1/2 with reflection x -> 1-x.
        enc=MultiwordEncoding(3,[(0,1)],m,k=2)
        clauses=enc.add_motion([(0,1),(1,0),(2,2)])
        with Solver(name='cadical195',bootstrap_with=enc.clauses+clauses) as s:
            answer=s.solve();assert answer==(m==2)
            result=enc.decode(s.get_model()) if answer else None
        if result:
            for w in result['words']:assert w[0]!=w[1]
            for a,w in enumerate(result['words']):
                b=result['word_permutations'][0][a];pi=result['color_permutations'][0][a]
                assert all(int(result['words'][b][j])==pi[int(w[i])] for i,j in [(0,1),(1,0),(2,2)])
        results.append(dict(support=m,status='SAT' if answer else 'UNSAT_CALIBRATION',result=result))
    return results


def run(root,m=2,budget=20000,solver_name='cadical195',return_domain=False):
    from pysat.solvers import Solver
    print(json.dumps(dict(calibration=calibration())),flush=True)
    parent,c=geometry(root,geometry_context=True)
    r=c['ring'];mul=r['mul'];pts=c['points'];lookup={p:i for i,p in enumerate(pts)}
    zero=(Q(0),)*32;one=(Q(1),)+zero[1:];eta=zero[:16]+one[:16];z=r['blocks'][0][64]
    add=lambda p,q:tuple(a+b for a,b in zip(p,q))
    bar=lambda p:tuple(Q(x)/2 for x in conjugate_twice(p))
    omega=tuple(-2*a-3*b for a,b in zip(one,z))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    definitions=[('tau',r['tau'],zero,False),('nu',nu,zero,False),('eta',eta,zero,False),
                 ('omega',omega,zero,False),('bar',one,zero,True),
                 ('bridge',tuple(-x for x in eta),add(one,mul(eta,z)),False),
                 ('translation_one',one,one,False),('translation_z',one,z,False)]
    power=one
    for j in range(1,5):
        power=mul(power,eta);definitions.append((f'one_plus_eta_{j}',one,add(one,power),False))
    definitions.append(('bridge_shift',one,add(one,mul(eta,z)),False))
    if return_domain:
        definitions.append(('minus_bar',tuple(-x for x in one),zero,True))
    enc=MultiwordEncoding(len(pts),c['edges'],m)
    for a in range(m):
        for color,idx in enumerate([0,153,150]):enc.clauses.append([enc.color(a,lookup[r['blocks'][0][idx]],color)])
    history=[];maps=[];positive=None
    with Solver(name=solver_name,bootstrap_with=enc.clauses) as solver:
        del enc.clauses
        for name,a,t,reflection in definitions:
            mapping=[(i,lookup[q]) for i,p in enumerate(pts)
                     if (q:=add(t,mul(a,bar(p) if reflection else p))) in lookup]
            maps.append(mapping);clauses=enc.add_motion(mapping)
            solver.append_formula(clauses);del clauses
            print(json.dumps(dict(added=name,domain=len(mapping),variables=enc.top,support=m)),flush=True)
            if len(maps)<9:continue
            solver.conf_budget(budget);answer=solver.solve_limited()
            status='SAT' if answer is True else 'UNSAT_FIXED_SUPPORT_ONLY' if answer is False else 'UNKNOWN'
            stage=dict(motion=name,status=status,domains=len(maps),stats=solver.accum_stats())
            history.append(stage);print(json.dumps(stage),flush=True)
            if answer is not True:break
            positive=enc.decode(solver.get_model())
            positive.update(motions=[d[0] for d in definitions[:len(maps)]],mapping_sha256=[digest(mm) for mm in maps])
            print(json.dumps(dict(positive=positive)),flush=True)
    return dict(experiment='E083' if return_domain else 'E080',support=m,geometry=parent['geometry'],history=history,result=positive,
                scope='Positive listed full domains only; bounded-support UNSAT or UNKNOWN is not a full-joint obstruction')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--support',type=int,default=2)
    parser.add_argument('--budget',type=int,default=20000);parser.add_argument('--solver',default='cadical195')
    parser.add_argument('--return-domain',action='store_true',help='Append the full minus-conjugation return domain')
    args=parser.parse_args();assert args.support>=1
    print(json.dumps(run(Path(__file__).resolve().parents[1],args.support,args.budget,args.solver,args.return_domain),indent=2))
