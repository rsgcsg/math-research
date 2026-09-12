"""Search a sufficient affine F5 law for all motions in M semidirect H.

Failure of this fixed representation is NOT a negative full-joint result.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, permutations
import hashlib
import json
from sympy import Matrix
from quintic_joint_ports import build
from quintic_second_host import multiply,conjugate


def run(root):
    from pysat.solvers import Solver
    raw,points,_,edges,den,summary,_=build(root)
    physical=[tuple(Q(x,den) for x in p) for p in points]
    z=tuple(Q(x,96) for x in sum(json.loads(raw)['points'][64],[])+[0]*16)
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16];powers=[one]
    for _ in range(4):powers.append(multiply(powers[-1],eta))
    basis=powers[:4]+[multiply(p,z) for p in powers[:4]]
    matrix=Matrix(32,8,lambda i,j:basis[j][i]);pivots=matrix.T.rref()[1]
    inv=matrix[list(pivots),:].inv();inverse=[[Q(x) for x in inv.row(i)] for i in range(8)]
    def split(p):
        coeff=[sum(x*p[j] for x,j in zip(row,pivots)) for row in inverse]
        remainder=tuple(p[i]-sum(coeff[j]*basis[j][i] for j in range(8)) for i in range(32))
        floors=[x.numerator//x.denominator for x in coeff]
        return (remainder,tuple(x-y for x,y in zip(coeff,floors))),sum(v*(1 if j<4 else 2) for j,v in enumerate(floors))%5
    signatures=[split(p) for p in physical];keys=sorted({key for key,h in signatures});index={key:i for i,key in enumerate(keys)}
    point_data=[(index[key],h) for key,h in signatures];n=len(keys)
    clauses=[[5*v+k+1 for k in range(5)] for v in range(n)]
    clauses += [[-5*v-a-1,-5*v-b-1] for v in range(n) for a,b in combinations(range(5),2)]
    for i,j in edges:
        a,ha=point_data[i];b,hb=point_data[j]
        clauses += [[-5*a-c-1,-5*b-((c+ha-hb)%5)-1] for c in range(5)]
    stages=[];orbit_hits=[]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        for stage in ('translations','full_group'):
            if stage=='full_group':
                for reflection in (False,True):
                    for sign in (1,-1):
                        for j,power in enumerate(powers):
                            hits=0
                            for i,p in enumerate(physical):
                                q=tuple(sign*x for x in multiply(power,conjugate(p) if reflection else p))
                                key,hq=split(q)
                                if key not in index:continue
                                hits+=1;a,ha=point_data[i];b=index[key]
                                for c in range(5):
                                    target=(sign*(c+ha)-hq)%5
                                    solver.add_clause([-5*a-c-1,5*b+target+1])
                            orbit_hits.append([reflection,sign,j,hits])
            solver.conf_budget(200000);answer=solver.solve_limited()
            row=dict(stage=stage,status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_AFFINE_MODEL_ONLY')
            if answer is True:
                model=set(solver.get_model());values=[next(k for k in range(5) if 5*v+k+1 in model) for v in range(n)]
                row['word']=''.join(str((values[a]+h)%5) for a,h in point_data)
            stages.append(row);print(stage,row['status'],flush=True)
            if answer is False:break
    oldraw=(root/'certificates/quintic_full_translation_laws.json').read_bytes();old=json.loads(oldraw);word=old['result']['word']
    lookup={p:i for i,p in enumerate(points)};extra=[]
    for j in range(1,5):
        for kind,t in [('unit',powers[j]),('root',multiply(powers[j],z))]:
            shift=tuple(int(x*den) for x in t);assert all(x*den==v for x,v in zip(t,shift))
            pairs=[[i,lookup[q]] for i,p in enumerate(points) if (q:=tuple(x+y for x,y in zip(p,shift))) in lookup]
            pi=next(pi for pi in permutations(range(5)) if all(pi[int(word[i])]==int(word[k]) for i,k in pairs))
            extra.append(dict(power=j,kind=kind,domain=len(pairs),permutation=list(pi)))
    return dict(schema=1,experiment='E069',geometry=summary,parent_sha256=hashlib.sha256(oldraw).hexdigest(),
                basis_pivots=list(pivots),cosets=n,stages=stages,orbit_hits=orbit_hits,extra_translations=extra,
                scope='Sufficient affine representation only; UNSAT is not a joint obstruction')


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];data=run(root)
    (root/'certificates/quintic_module_law.json').write_text(json.dumps(data,indent=2)+'\n')
