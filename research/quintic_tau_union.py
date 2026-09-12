"""E077: actual induced X union tau X, escaping the residue-5 ring."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
from quintic_joint_ports import build
from quintic_independent_center import geometry
from quintic_second_host import multiply
from quintic_core_probe import solve


def run(root):
    raw,points,ids,_,den,_,_=build(root)
    physical=[tuple(Q(x,den) for x in p) for p in points]
    blocks=[[physical[i] for i in block] for block in ids]
    tau=tuple(-Q(1,10) if i==0 else Q(3,10) if i==10 else Q(0) for i in range(32))
    blocks += [[multiply(tau,p) for p in block] for block in blocks[:]]
    points,ids,edges,den,summary=geometry(blocks)
    first=set().union(*(set(b) for b in ids[:10]));second=set().union(*(set(b) for b in ids[10:]))
    summary['overlap']=len(first&second)
    summary['new_cross_edges']=sum(not ({u,v}<=first or {u,v}<=second) for u,v in edges)
    print(summary,flush=True)
    result=solve(points,ids,edges,200000);print(result['status'],flush=True)
    return dict(schema=1,experiment='E077',core_sha256=hashlib.sha256(raw).hexdigest(),
                denominator=den,geometry=summary,result=result,
                scope='Actual finite induced graph only; positive coloring not a full joint law or a coloring of the whole field')


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    (root/'certificates/quintic_tau_union.json').write_text(json.dumps(run(root),indent=2)+'\n')
