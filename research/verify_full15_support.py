"""Independent standard-library replay for six complete three-atom cases.

No solver, native proof reader, or native dependency extractor is executed.
The claimed conclusion concerns support size, NOT the existence of a law on
an unrestricted support and NOT the ordinary chromatic number of the plane.
"""
from pathlib import Path
import gzip,json,hashlib,argparse
from audit_full_law_preparation import reconstruct,unique_keys
from verify_anchored_eta import geometry_check,read
from verify_eta_minimum_support import check_rup
from full15_support_cnf import build,SPLIT_TYPES,UNIFORM_CASES,require

CASES=[('uniform',list(p),list(map(list,enumerate(p)))) for p in UNIFORM_CASES]
CASES += [('211',[i],list(map(list,e))) for i,e in enumerate(SPLIT_TYPES)]


def validate_header(cert,summary):
    require(cert.get('schema')=='full15-support-exclusion-v1','certificate schema')
    require(cert.get('input_semantic_sha256')==summary['semantic_sha256'],'geometry binding')
    require(cert.get('full_motions')==list(range(15)) and all(type(i) is int for i in cert['full_motions']),'all full domains')
    require(cert.get('conclusion')=='no probability law supported on at most three complete partitions','conclusion scope')
    cases=cert.get('cases');require(type(cases) is list and len(cases)==6,'six exhaustive cases')
    for c,(kind,sigma,edges) in zip(cases,CASES):
        require(c.get('kind')==kind and c.get('eta_case')==sigma and all(type(x) is int for x in c['eta_case']),'case identity')
        require(c.get('eta_edges')==edges and all(type(v) is int for p in c['eta_edges'] for v in p),'case transport')
        require(type(c.get('m')) is int and c['m']==3,'three states')


def validate_case(c,b,known_hash=None):
    digest=b['clauses'].digest(b['nv']) if known_hash is None else known_hash
    require(c.get('cnf_sha256')==digest,'semantic CNF hash')
    require(type(c.get('nv')) is int and c['nv']==b['nv'],'variable count')
    require(type(c.get('clauses')) is int and c['clauses']==len(b['clauses']),'clause count')
    ids=c.get('initial_clause_ids')
    require(type(ids) is list and bool(ids) and all(type(i) is int and 1<=i<=len(b['clauses']) for i in ids) and ids==sorted(set(ids)),'initial IDs')
    proof=c.get('rup_clauses');require(type(proof) is list and bool(proof),'proof rows')
    require(all(type(row) is list for row in proof),'proof row structure')
    require(proof[-1]==[] and all(proof[i] for i in range(len(proof)-1)),'final contradiction placement')
    selected=[b['clauses'][i-1] for i in ids]
    report=check_rup(selected,proof)
    report['initial_by_section']={name:sum(lo<i<=hi for i in ids) for name,lo,hi in b['sections']}
    return report


def load_certificate(root):
    raw=gzip.decompress((root/'certificates/full15_support_exclusion.json.gz').read_bytes())
    return json.loads(raw,object_pairs_hook=unique_keys)


def verify(cert,data,summary,mutation_callback=None):
    validate_header(cert,summary)
    geometry=geometry_check(read(Path(__file__).resolve().parents[1]/'certificates/eta_gauge_geometry.json'),data)
    reports=[]
    for c in cert['cases']:
        b=build(data,c['eta_edges'],3,c['kind'])
        digest=b['clauses'].digest(b['nv'])
        report=validate_case(c,b,digest)
        if mutation_callback is not None:mutation_callback(c,b,digest)
        reports.append(dict(kind=c['kind'],eta_case=c['eta_case'],cnf_sha256=digest,nv=b['nv'],clauses=len(b['clauses']),**report))
        del b
    return dict(status='PASS',normalization_geometry=geometry,cases=reports,
                minimum_support_lower_bound=4,unrestricted_full15_status='UNDETERMINED',
                scope='Original complete fifteen domains on all actual Y edges. Six normalized three-state cases plus the written arbitrary-weight reduction. No ordinary HN bound.')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    argparse.ArgumentParser(description=__doc__).parse_args()
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    print(json.dumps(verify(load_certificate(root),data,summary),indent=2))

if __name__=='__main__':main()
