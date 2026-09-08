"""Exact Parts 509 coordinate import and induced unit graph.

Safe arithmetic-only AST parser; no eval, SymPy parsing, or author code.
All coordinates lie in Q(sqrt(3),sqrt(11),sqrt(5)). Nested radicals simplify
as sqrt(5*(7 +/- sqrt(33))/2) = (sqrt(55) +/- sqrt(15))/2.
"""
import ast
import hashlib
import json
import math
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

RADICANDS=(1,3,11,33,5,15,55,165)


def scalar(x=0):
    return (F(x),)+(F(0),)*7


def add(x,y):
    return tuple(a+b for a,b in zip(x,y))


def neg(x):
    return tuple(-a for a in x)


def mul(x,y):
    result=[0]*8
    for i,a in enumerate(x):
        if a:
            for j,b in enumerate(y):
                if b:
                    result[i^j]+=a*b*RADICANDS[i&j]
    return tuple(result)


def inv_monomial(x):
    terms=[(i,c) for i,c in enumerate(x) if c]
    assert len(terms)==1,'Only monomial denominators supported'
    i,c=terms[0]
    return tuple(F(1,c*RADICANDS[i]) if j==i else F(0) for j in range(8))


def sqrt(x):
    if all(v==0 for v in x[1:]) and x[0]>=0:
        n=x[0].numerator*x[0].denominator
        for i,r in enumerate(RADICANDS):
            q=math.isqrt(n//r)
            if q*q*r==n:
                return tuple(F(q,x[0].denominator) if j==i else F(0) for j in range(8))
    for sign in (1,-1):
        expected=list(scalar(F(35,2)));expected[3]=sign*F(5,2)
        if x==tuple(expected):
            root=[F(0)]*8;root[6]=F(1,2);root[5]=sign*F(1,2)
            assert mul(root,root)==x
            # sqrt(55)>sqrt(15)>0 fixes the positive root for both signs.
            return tuple(root)
    raise ValueError(f'Unsupported exact square root: {x}')


def parse_expr(node):
    if isinstance(node,ast.Constant) and type(node.value)==int:
        return scalar(node.value)
    if isinstance(node,ast.UnaryOp):
        x=parse_expr(node.operand)
        if isinstance(node.op,ast.USub):
            return neg(x)
        if isinstance(node.op,ast.UAdd):
            return x
    if isinstance(node,ast.BinOp):
        x,y=parse_expr(node.left),parse_expr(node.right)
        if isinstance(node.op,ast.Add):
            return add(x,y)
        if isinstance(node.op,ast.Sub):
            return add(x,neg(y))
        if isinstance(node.op,ast.Mult):
            return mul(x,y)
        if isinstance(node.op,ast.Div):
            return mul(x,inv_monomial(y))
    if (isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and
            node.func.id=='Sqrt' and len(node.args)==1 and not node.keywords):
        return sqrt(parse_expr(node.args[0]))
    raise ValueError(f'Unsupported coordinate AST: {ast.dump(node)}')


def read_points(path):
    points=[]
    for line in path.read_text().splitlines():
        text=line.strip().replace('{','(').replace('}',')').replace('[','(').replace(']',')')
        node=ast.parse(text,mode='eval').body
        assert isinstance(node,ast.Tuple) and len(node.elts)==2
        points.append(tuple(parse_expr(e) for e in node.elts))
    assert len(points)==len(set(points))==509
    den=math.lcm(*(c.denominator for p in points for x in p for c in x))
    return [tuple(tuple(int(c*den) for c in x) for x in p) for p in points],den


def unit_edges(points,den):
    edges=[]
    for i,j in combinations(range(len(points)),2):
        dx,dy=[tuple(a-b for a,b in zip(x,y)) for x,y in zip(points[i],points[j])]
        squared=add(mul(dx,dx),mul(dy,dy))
        if squared==(den*den,0,0,0,0,0,0,0):
            edges.append((i,j))
    return edges


def clauses(n,edges,k,exactly_one=True):
    result=[[k*v+c+1 for c in range(k)] for v in range(n)]
    if exactly_one:
        result.extend([-k*v-a-1,-k*v-b-1] for v in range(n) for a,b in combinations(range(k),2))
    result.extend([-k*a-c-1,-k*b-c-1] for a,b in edges for c in range(k))
    return result


def run(cache):
    path=cache/'parts509.vtx'
    points,den=read_points(path)
    edges=unit_edges(points,den)
    assert len(edges)==2442
    reduced=json.loads((cache/'parts509_reduced.json').read_text())['edges']
    assert len(reduced)==len(set(map(tuple,reduced)))==2259
    assert all(tuple(e) in set(edges) for e in reduced)
    rows=(cache/'parts509_reduced.cnf').read_text().splitlines()
    assert rows[0]=='p cnf 2036 9548'
    parsed=[list(map(int,line.split())) for line in rows[1:]]
    assert len(parsed)==9548 and all(row[-1]==0 for row in parsed)
    cnf=[row[:-1] for row in parsed]
    expected=clauses(509,reduced,4,exactly_one=False)+[[1],[598],[611]]
    assert cnf==expected
    # Pins: vertices 0,149,152 receive colors 0,1,2. They form a triangle,
    # so any proper four-coloring can be renamed to obey these pins.
    assert all(tuple(sorted(e)) in set(map(tuple,reduced)) for e in combinations((0,149,152),2))
    from pysat.solvers import Solver
    with Solver(name='cadical195',bootstrap_with=clauses(509,edges,5)) as solver:
        assert solver.solve()
        model=set(solver.get_model())
    coloring=[next(c for c in range(5) if 5*v+c+1 in model) for v in range(509)]
    assert all(coloring[a]!=coloring[b] for a,b in edges)
    return dict(status='EXACT_GEOMETRY_CNF_AND_FIVE_COLORING_VERIFIED',vertices=509,
                coordinate_denominator=den,points=points,induced_edges=edges,
                reduced_edges=reduced,five_coloring=coloring,
                source_commit='6d5ac08491f7cadbebd7d5b79e3f825d08eedf7b',
                source_hashes={name:hashlib.sha256((cache/name).read_bytes()).hexdigest()
                               for name in ('parts509.vtx','parts509_reduced.json','parts509_reduced.cnf','parts509_reduced.drat')},
                four_color_lower_bound='requires separate DRAT replay')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--cache',type=Path,default=Path('references/cache'))
    parser.add_argument('--output',type=Path,default=Path('certificates/parts509_core.json'))
    args=parser.parse_args()
    result=run(args.cache)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('points','induced_edges','reduced_edges','five_coloring')},indent=2))
