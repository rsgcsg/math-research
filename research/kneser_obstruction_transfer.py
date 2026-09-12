"""E068: small multicolor homomorphisms, not geometric realizations."""
from pathlib import Path
import hashlib
import json
from pysat.solvers import Solver
from pysat.card import CardEnc


def run(root):
    edges=set()
    for i in range(5):
        j=(i+1)%5
        edges.update(tuple(sorted(e)) for e in ((i,j),(5+i,j),(5+j,i),(5+i,10)))
    rows=[]
    for k in (2,3):
        n=3*k;top=11*n;clauses=[]
        for v in range(11):
            enc=CardEnc.equals([v*n+i+1 for i in range(n)],k,top_id=top)
            top=enc.nv;clauses+=enc.clauses
        clauses += [[-u*n-i-1,-v*n-i-1] for u,v in sorted(edges) for i in range(n)]
        with Solver(name='cd19',bootstrap_with=clauses) as solver:
            solver.conf_budget(10000)
            if solver.solve_limited() is not True:raise RuntimeError('No certified map produced')
            model=set(solver.get_model())
            rows.append(dict(n=n,k=k,sets=[[i for i in range(n) if v*n+i+1 in model] for v in range(11)]))
    return dict(schema=1,experiment='E068',
                obstruction_sha256=hashlib.sha256((root/'certificates/mycielski_collision_refutation.json.gz').read_bytes()).hexdigest(),
                maps=rows,independent_weight_numerators=[3]*5+[2]*5+[4],weight_denominator=10)


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/kneser_obstruction_transfer.json').write_text(json.dumps(run(root),indent=2)+'\n')
