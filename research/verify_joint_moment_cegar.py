"""E099 independent validation by the existing full-geometry/full-law checker."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
from verify_quintic_tau_union import verify as geometry
from verify_joint_pair_cegar import check


def verify(root):
    if not __debug__:raise RuntimeError('Do not disable verification assertions')
    path=root/'certificates/joint_moment_cegar.json';data=json.loads(path.read_text())
    assert data['schema']==1 and data['experiment']=='E099'
    if data['result'] is None:
        report=dict(status='NO_POSITIVE_WITNESS',search_status=data['search']['status'],
                    scope='Search did not certify a positive law or a mathematical negative result')
    else:
        parent,context=geometry(root,geometry_context=True)
        copied=deepcopy(data);copied['experiment']='E097'
        report=check(root,copied,parent,context);report['experiment']='E099'
    report['certificate_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return report


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];report=verify(root)
    (root/'certificates/joint_moment_cegar_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VALIDATION '+json.dumps(report),flush=True)
