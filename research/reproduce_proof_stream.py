"""Version-pinned search-side reproducer; not part of proof verification."""
from pathlib import Path
import sys,json,hashlib,inspect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research'))
from pysat.solvers import Solver,Cadical195
from closed_binary_proof import close_and_read,parse_binary
from verify_eta_minimum_support import check_rup
results=[]
for initial in ([[1],[-1]],[[1,2],[-1,2],[1,-2],[-1,-2]]):
 s=Solver(name='cadical195',bootstrap_with=initial,with_proof=True)
 assert s.solve() is False
 raw_api=s.get_proof()
 # get_proof moves the file offset. These tiny instances have zero on-disk
 # bytes before the native flush, so that call cannot truncate a long trace.
 fixed,record=close_and_read(s)
 additions=[list(map(int,l.split()[:-1])) for l in fixed if not l.startswith('d')]
 result=check_rup(initial,additions)
 results.append(dict(cnf=initial,early_get_proof=raw_api,flushed_snapshot=fixed,stream=record,independent_check=result))
try:parse_binary(b'a')
except ValueError:rejected=True
else:rejected=False
assert rejected
out=dict(schema='pinned-native-proof-export-reproducer-v1',python_sat='1.9.dev15',solver='CaDiCaL 1.9.5',
 wrapper_source_sha256=hashlib.sha256(Path(inspect.getfile(Cadical195)).read_bytes()).hexdigest(),tests=results,
 header_only_old_parser=Solver._proof_bin2text(bytearray(b'a')),header_only_strict_parser_rejected=rejected,
 scope='Observed on the archived Linux wheel only. A truncated export is not a logical UNSAT certificate; existing independently verified proofs are not invalidated.')
(ROOT/'certificates/full15_proof_export_reproducer.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
