"""Replay the public Parts subgraph refutation after exact CNF correspondence."""
import hashlib
import json
import subprocess
import gzip
from pathlib import Path
from verify_parts_core import verify_geometry
from verify_rup_lrat import verify_parts


def replay(root):
    core,edges=verify_geometry(root/'certificates/parts509_core.json')
    cache=root/'references/cache'
    cnf=cache/'parts509_reduced.cnf';proof=cache/'parts509_reduced.drat'
    reduced=list(map(tuple,core['reduced_edges']))
    for path in (cnf,proof):
        assert hashlib.sha256(path.read_bytes()).hexdigest()==core['source_hashes'][path.name]
    lines=cnf.read_text().splitlines()
    assert lines[0]=='p cnf 2036 9548'
    clauses=[tuple(map(int,line.split())) for line in lines[1:]]
    expected=[tuple(range(4*v+1,4*v+5))+(0,) for v in range(509)]
    expected += [(-4*a-c-1,-4*b-c-1,0) for a,b in reduced for c in range(4)]
    expected += [(1,0),(598,0),(611,0)]
    assert clauses==expected and len(clauses)==9548
    lrat=cache/'parts509_reduced.lrat'
    command=[str(cache/'drat-trim'),str(cnf),str(proof),'-L',str(lrat),'-t','120']
    result=subprocess.run(command,capture_output=True,text=True,timeout=130)
    assert result.returncode==0 and 's VERIFIED' in result.stdout.splitlines(),result.stdout+result.stderr
    packed=root/'certificates/parts509_reduced.lrat.gz'
    packed.write_bytes(gzip.compress(lrat.read_bytes(),mtime=0))
    independent=verify_parts(core,packed)
    return dict(status='VERIFIED_EXTERNAL_FIVE_CHROMATIC_CORE',vertices=509,
                induced_edges=2442,certified_nonfour_subgraph_edges=2259,
                source_commit=core['source_commit'],inputs_sha256=core['source_hashes'],
                checker_repository='https://github.com/marijnheule/drat-trim',
                checker_commit='2e3b2dc0ecf938addbd779d42877b6ed69d9a985',
                checker_source_sha256=hashlib.sha256((cache/'drat-trim.c').read_bytes()).hexdigest(),
                checker_binary_sha256=hashlib.sha256((cache/'drat-trim').read_bytes()).hexdigest(),
                command=command,stdout=result.stdout,stderr=result.stderr,
                exit_code=result.returncode,cnf_correspondence_verified=True,
                all_induced_edges_verified=True,five_coloring_verified=True,
                lrat_sha256=hashlib.sha256(lrat.read_bytes()).hexdigest(),
                packed_lrat_sha256=hashlib.sha256(packed.read_bytes()).hexdigest(),
                independent_rup_check=independent)


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    root=Path(__file__).resolve().parents[1]
    result=replay(root)
    (root/'certificates/parts509_drat_replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
