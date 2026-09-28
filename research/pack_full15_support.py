"""Pack untrusted search traces/cores. Run test_full15_support.py afterwards."""
from pathlib import Path
import argparse,json,gzip,hashlib

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results-dir',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    cases=[]
    for name in ['u3id','u3swap','u3cycle','w3id','w3swap','w3split']:
        q=json.loads((a.results_dir/(name+'.json')).read_text())
        c=json.loads((a.results_dir/(name+'.core.json')).read_text())
        if q['status']!='UNSAT_UNCERTIFIED':raise ValueError('missing negative candidate '+name)
        c.update({key:q[key] for key in ('kind','eta_case','eta_edges','m','nv','clauses','cnf_sha256')})
        c['search_record']=q
        c['flushed_trace_sha256']=hashlib.sha256(gzip.decompress((a.results_dir/(name+'.json.drup.gz')).read_bytes())).hexdigest()
        cases.append(c)
    certificate=dict(schema='full15-support-exclusion-v1',date='2026-09-28',base_commit='a885b67c172726e14884cb43cd37b965dbb32575',
        input_semantic_sha256=cases[0]['search_record']['input_semantic_sha256'],full_motions=list(range(15)),
        conclusion='no probability law supported on at most three complete partitions',cases=cases,
        scope='Conclusion becomes certified only after semantic reconstruction and independent RUP replay; unrestricted support and ordinary HN remain unresolved.')
    raw=json.dumps(certificate,separators=(',',':'),sort_keys=True).encode()+b'\n'
    out=bytearray(gzip.compress(raw,mtime=0));out[9]=255
    path=root/'certificates/full15_support_exclusion.json.gz';path.write_bytes(out)
    print(json.dumps(dict(status='PACKED_PENDING_INDEPENDENT_REPLAY',bytes=len(out),sha256=hashlib.sha256(out).hexdigest())))
if __name__=='__main__':main()
