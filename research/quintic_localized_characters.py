"""E073: six-character sufficient law on the nu-localized module.

Failure excludes only this ansatz. Even positive generator checks do not
establish all exit/reentry domains of an infinite orientation group.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, product
import json
from sympy import Matrix
from quintic_joint_ports import build
from quintic_second_host import multiply,conjugate


def run(root, screen_all=False, general_characters=False):
    from pysat.solvers import Solver
    raw,points,_,edges,den,summary,_=build(root)
    physical=[tuple(Q(x,den) for x in p) for p in points]
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    z=tuple(Q(x,96) for x in sum(json.loads(raw)['points'][64],[])+[0]*16)
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    omega=tuple(-2*a-3*b for a,b in zip(one,z))
    powers=[one]
    for _ in range(4):powers.append(multiply(powers[-1],eta))
    basis=powers[:4]+[multiply(z,p) for p in powers[:4]]
    basis += [multiply(nu,p) for p in basis[:]]
    matrix=Matrix(32,16,lambda i,j:basis[j][i]);pivots=matrix.T.rref()[1]
    inv=matrix[list(pivots),:].inv();inverse=[[Q(x) for x in inv.row(i)] for i in range(16)]
    characters=[(j,lam) for j in range(3) for lam in (2,3)];weights=[(1,2),(2,3),(2,0)]
    def split(p):
        coeff=[sum(x*p[j] for x,j in zip(row,pivots)) for row in inverse]
        rem=tuple(p[i]-sum(coeff[j]*basis[j][i] for j in range(16)) for i in range(32))
        fractions=[];shifts=[]
        for x in coeff:
            d=x.denominator;power3=1
            while d%3==0:d//=3;power3*=3
            fraction=Q((x.numerator*pow(power3,-1,d))%d,d) if d>1 else Q(0)
            fractions.append(fraction);v=x-fraction
            shifts.append(v.numerator*pow(v.denominator,-1,5)%5)
        a,b,c,d=[sum(shifts[i:i+4]) for i in range(0,16,4)]
        h=([(a*x+b*y+c*u+d*v)%5 for x,y,u,v in characters] if screen_all or general_characters else
           [(weights[j][0]*(a+lam*c)+weights[j][1]*(b+lam*d))%5 for j,lam in characters])
        return (rem,tuple(fractions)),h
    if screen_all:
        characters=[c for c in product(range(5),repeat=4) if any(c) and next(x for x in c if x)==1]
    elif general_characters:
        screen=json.loads((root/'certificates/quintic_localized_character_screen.json').read_text())
        characters=[tuple(row['character']) for row in screen['witnesses'] if row['zero_edge'] is None]
    signatures=[split(p) for p in physical];keys=sorted({key for key,h in signatures});index={key:i for i,key in enumerate(keys)}
    pdata=[(index[key],h) for key,h in signatures];n=len(keys)
    if screen_all:
        witnesses=[]
        for j,ch in enumerate(characters):
            witness=next(([u,v] for u,v in edges if pdata[u][0]==pdata[v][0] and pdata[u][1][j]==pdata[v][1][j]),None)
            witnesses.append(dict(character=ch,zero_edge=witness))
        survivors=[row['character'] for row in witnesses if row['zero_edge'] is None]
        print('all character screen',len(characters),'survivors',len(survivors),survivors,flush=True)
        return dict(schema=1,experiment='E074',geometry=summary,module_cosets=n,witnesses=witnesses,
                    scope='Zero-edge filter on all eta-invariant additive F5 characters, not arbitrary colorings')
    def var(j,a,c):return 5*(j*n+a)+c+1
    count=len(characters)
    clauses=[[var(j,a,c) for c in range(5)] for j in range(count) for a in range(n)]
    clauses += [[-var(j,a,c),-var(j,a,d)] for j in range(count) for a in range(n) for c,d in combinations(range(5),2)]
    for u,v in edges:
        a,ha=pdata[u];b,hb=pdata[v]
        for j in range(count):
            clauses += [[-var(j,a,c),-var(j,b,(c+ha[j]-hb[j])%5)] for c in range(5)]
    result=dict(schema=1,experiment='E075' if general_characters else 'E073',geometry=summary,module_cosets=n,basis_pivots=list(pivots),characters=characters)
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        stages=[]
        def solve(stage):
            solver.conf_budget(200000);answer=solver.solve_limited()
            row=dict(stage=stage,status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_FIXED_CHARACTER_MODEL_ONLY')
            if answer is True:
                model=set(solver.get_model())
                values=[[next(c for c in range(5) if var(j,a,c) in model) for a in range(n)] for j in range(count)]
                row['words']=[''.join(str((values[j][a]+h[j])%5) for a,h in pdata) for j in range(count)]
            stages.append(row);print(stage,n,row['status'],flush=True)
            return answer
        if solve('all_N_translations') is True:
            for name,r,reflection in [('eta',eta,False),('omega',omega,False),('conjugate',one,True),('nu',nu,False)]:
                hits=0
                for i,p in enumerate(physical):
                    key,hq=split(multiply(r,conjugate(p) if reflection else p))
                    if key not in index:continue
                    hits+=1;a,ha=pdata[i];b=index[key]
                    for j,ch in enumerate(characters):
                        if general_characters:
                            a0,b0,c0,d0=ch
                            transformed=((-2*a0-3*b0,a0+b0,-2*c0-3*d0,c0+d0) if name=='omega' else
                                         (a0,-a0-b0,-c0,c0+d0) if reflection else
                                         (c0,d0,-a0,-b0) if name=='nu' else ch)
                            transformed=tuple(x%5 for x in transformed);scale=next(x for x in transformed if x)
                            target_character=tuple(x*pow(scale,-1,5)%5 for x in transformed)
                        else:
                            k,lam=ch
                            target_character=((k+1)%3,lam) if name=='omega' else ((-k)%3,(-lam)%5) if reflection else (k,lam)
                            scale=lam if name=='nu' else 1
                        other=characters.index(target_character)
                        for c in range(5):solver.add_clause([-var(other,a,c),var(j,b,(scale*(c+ha[other])-hq[j])%5)])
                print('added',name,hits,flush=True)
            solve('four_generators_with_N_translations')
    result['stages']=stages
    result['scope']='Sufficient fixed-character ansatz only; generator checks not full infinite orientation closure'
    return result


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/quintic_localized_characters.json').write_text(json.dumps(run(root),indent=2)+'\n')
