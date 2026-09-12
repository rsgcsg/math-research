"""E070: three affine characters, mixed rather than a single color frame."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import hashlib
import json
from sympy import Matrix
from quintic_joint_ports import build
from quintic_second_host import multiply,conjugate


def run(root, include_nu=False):
    from pysat.solvers import Solver
    raw,points,_,edges,den,summary,_=build(root)
    physical=[tuple(Q(x,den) for x in p) for p in points]
    z=tuple(Q(x,96) for x in sum(json.loads(raw)['points'][64],[])+[0]*16)
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    powers=[one]
    for _ in range(4):powers.append(multiply(powers[-1],eta))
    omega=tuple(-2*a-3*b for a,b in zip(one,z));omegas=[one,omega,multiply(omega,omega)]
    basis=powers[:4]+[multiply(z,p) for p in powers[:4]]
    matrix=Matrix(32,8,lambda i,j:basis[j][i]);pivots=matrix.T.rref()[1]
    inv=matrix[list(pivots),:].inv();inverse=[[Q(x) for x in inv.row(i)] for i in range(8)]
    def split(p):
        coeff=[sum(x*p[j] for x,j in zip(row,pivots)) for row in inverse]
        remainder=tuple(p[i]-sum(coeff[j]*basis[j][i] for j in range(8)) for i in range(32))
        floors=[x.numerator//x.denominator for x in coeff];a=sum(floors[:4]);b=sum(floors[4:])
        return (remainder,tuple(x-y for x,y in zip(coeff,floors))),[(a+2*b)%5,(2*a+3*b)%5,2*a%5]
    signatures=[split(p) for p in physical];keys=sorted({key for key,h in signatures});index={key:i for i,key in enumerate(keys)}
    p_data=[(index[key],h) for key,h in signatures];n=len(keys)
    def var(j,a,c):return 5*(j*n+a)+c+1
    clauses=[[var(j,a,c) for c in range(5)] for j in range(3) for a in range(n)]
    clauses += [[-var(j,a,c),-var(j,a,d)] for j in range(3) for a in range(n) for c,d in combinations(range(5),2)]
    for u,v in edges:
        a,ha=p_data[u];b,hb=p_data[v]
        for j in range(3):clauses += [[-var(j,a,c),-var(j,b,(c+ha[j]-hb[j])%5)] for c in range(5)]
    hits=[]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        for reflection in (False,True):
            for sign in (1,-1):
                for k,om in enumerate(omegas):
                    for e,power in enumerate(powers):
                        r=multiply(om,power);count=0
                        for i,p in enumerate(physical):
                            q=tuple(sign*x for x in multiply(r,conjugate(p) if reflection else p));key,hq=split(q)
                            if key not in index:continue
                            count+=1;a,ha=p_data[i];b=index[key]
                            for j in range(3):
                                other=((-(j+k)) if reflection else j+k)%3
                                for c in range(5):
                                    target=(sign*(c+ha[other])-hq[j])%5
                                    solver.add_clause([-var(other,a,c),var(j,b,target)])
                        hits.append([reflection,sign,k,e,count])
                    print('added orientation coset',reflection,sign,k,flush=True)
        extra={}
        if include_nu:
            nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
            lookup={p:i for i,p in enumerate(physical)}
            domain=[(i,lookup[q]) for i,p in enumerate(physical) if (q:=multiply(nu,p)) in lookup]
            next_var=15*n
            def fresh():
                nonlocal next_var
                next_var+=1
                return next_var
            def permutation(size):
                array=[[fresh() for _ in range(size)] for _ in range(size)]
                for row in array+list(map(list,zip(*array))):
                    solver.add_clause(row)
                    for a,b in combinations(row,2):solver.add_clause([-a,-b])
                return array
            sigma=permutation(3);perms=[permutation(5) for _ in range(3)]
            for u,v in domain:
                a,ha=p_data[u];b,hb=p_data[v]
                for j in range(3):
                    for other in range(3):
                        for c in range(5):
                            for d in range(5):
                                solver.add_clause([-sigma[j][other],-var(other,a,(c-ha[other])%5),
                                                   -perms[j][c][d],var(j,b,(d-hb[j])%5)])
            extra['nu_domain']=domain
            print('added full nu domain',len(domain),flush=True)
        solver.conf_budget(200000);answer=solver.solve_limited()
        result=dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_THREE_CHARACTER_MODEL_ONLY')
        if answer is True:
            model=set(solver.get_model());values=[[next(c for c in range(5) if var(j,a,c) in model) for a in range(n)] for j in range(3)]
            result['words']=[''.join(str((values[j][a]+h[j])%5) for a,h in p_data) for j in range(3)]
            if include_nu:
                extra['word_permutation']=[next(k for k in range(3) if sigma[j][k] in model) for j in range(3)]
                extra['color_permutations']=[[next(d for d in range(5) if perms[j][c][d] in model) for c in range(5)] for j in range(3)]
    print(result['status'],flush=True)
    parent=(root/'certificates/quintic_module_law.json').read_bytes()
    return dict(schema=1,experiment='E072' if include_nu else 'E070',geometry=summary,parent_sha256=hashlib.sha256(parent).hexdigest(),
                cosets=n,orbit_hits=hits,result=result,
                **extra,
                scope=('Three-character sufficient model retaining M semidirect H30 and adding full nu domain; failure is not a joint obstruction'
                       if include_nu else 'Three-word sufficient full joint for M semidirect mu30/reflections; failure is not a joint obstruction'))


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/quintic_three_character_law.json').write_text(json.dumps(run(root),indent=2)+'\n')
