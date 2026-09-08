"""Export exact single-pivot contact rows from the already certified doubles."""
from pathlib import Path
import json
from parts_core import add, mul, neg


def run(root):
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    escaped = json.loads((root/'certificates/parts509_escape_rotations.json').read_text())
    points = core['points']; den = core['coordinate_denominator']
    records = []
    for case in escaped['cases']:
        rows = []
        for a,b in case['cross_edges']:
            p,q = points[a],points[b]
            dot = add(mul(p[0],q[0]),mul(p[1],q[1]))
            cross = add(neg(mul(p[0],q[1])),mul(p[1],q[0]))
            norms = add(add(mul(p[0],p[0]),mul(p[1],p[1])),
                        add(mul(q[0],q[0]),mul(q[1],q[1])))
            C = list(norms);C[0] -= den*den
            A,B = [[2*x for x in v] for v in (dot,cross)]
            assert any(A) and not any(B)
            num,denom = case['cosine']
            assert [num*x for x in A] == [denom*x for x in C]
            rows.append(dict(pair=[a,b],A=A,B=B,C=C))
        records.append(dict(radicand=case['radicand'],cosine=case['cosine'],
                            contact_rows=rows,coefficient_rank=1,augmented_rank=1))
    return dict(schema=1,core_coordinate_denominator=den,
                row_scaling='Rows use integer core coordinates; C subtracts denominator squared',
                cases=records)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = run(root)
    (root/'certificates/pose_field_lock.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(cases=len(data['cases']),rows=sum(len(c['contact_rows']) for c in data['cases']))))
