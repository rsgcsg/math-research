"""Bounded search, never a proof from the solver status alone.

Run on the independently rebuilt full-law cache. Negative traces are reduced
to their dependency cone, then replayed by the existing independent RUP checker.
"""
import argparse
import json
import lzma
from pathlib import Path
import subprocess
import tempfile
import time
from full15_support_cnf import build
from rup_hint_export import export
from verify_eta_minimum_support import replay_case
from audit_full_law_preparation import canonical, sha
from verify_anchored_eta import read


def reduce_trace(initial, trace):
    return reduce_lrat(len(initial),export(initial,trace))


def reduce_lrat(base,lines):
    records={}
    for line in lines:
        fields=line.split()
        if not fields or fields[0]=='c':continue
        if len(fields)>1 and fields[1]=='d':continue
        values=list(map(int,fields));end=values.index(0)
        if values[-1]!=0 or any(i<=0 for i in values[end+1:-1]):
            raise ValueError('non-positive/RAT LRAT unsupported')
        records[values[0]]=(values[1:end],values[end+1:-1])
    if not records or records[max(records)][0]:raise ValueError('no final empty clause')
    needed={max(records)};todo=list(needed);original=set()
    while todo:
        for i in records[todo.pop()][1]:
            if i<=base:original.add(i)
            elif i not in needed:needed.add(i);todo.append(i)
    return sorted(original),[records[i][0] for i in sorted(needed)]


def fast_trace(built,trace,binary):
    # An untrusted converter only. No mathematical conclusion is accepted
    # until the reduced initial-clause subset passes independent RUP replay.
    with tempfile.TemporaryDirectory(prefix='hn-full15-proof-') as folder:
        folder=Path(folder);cnf=folder/'input.cnf';proof=folder/'input.drat';lrat=folder/'output.lrat'
        with cnf.open('w') as stream:
            stream.write(f'p cnf {built["nv"]} {len(built["clauses"])}\n')
            for c in built['clauses']:stream.write(' '.join(map(str,c))+' 0\n')
        # Some APIs omit the final empty clause. Propose it, but only the
        # independent checker may establish the needed root contradiction.
        additions=[line.strip() for line in trace if line.strip() and not line.startswith(('d','c'))]
        trailer='' if additions and additions[-1]=='0' else '0\n'
        proof.write_text('\n'.join(trace)+'\n'+trailer)
        converted=subprocess.run([str(binary.resolve()),str(cnf),str(proof),'-L',str(lrat),'-t','180'],
                                 capture_output=True,text=True,timeout=200)
        if converted.returncode or not lrat.exists():raise ValueError('DRAT conversion failed: '+converted.stdout[-1000:])
        with lrat.open() as stream:return reduce_lrat(len(built['clauses']),stream)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--weighted',action='store_true')
    p.add_argument('--case',type=int,choices=range(3),required=True)
    p.add_argument('--conflicts',type=int,default=12000)
    p.add_argument('--solver',choices=['glucose3','cadical195'],default='cadical195')
    p.add_argument('--drat-trim',type=Path,help='Optional untrusted native LRAT exporter')
    args=p.parse_args()
    if args.conflicts<=0:raise ValueError('positive conflict budget required')
    root=Path(__file__).resolve().parents[1]
    data=read(args.cache);identity=sha(canonical(data))
    expected=read(root/'certificates/full_law_preparation_audit.json')['independent_inputs']['semantic_sha256']
    if identity!=expected:raise ValueError('cache has not been independently authenticated')
    started=time.monotonic();built=build(data,args.weighted,args.case)
    print(json.dumps(dict(stage='built',weighted=args.weighted,case=args.case,
                          variables=built['nv'],clauses=len(built['clauses']))),flush=True)
    from pysat.solvers import Solver
    with Solver(name=args.solver,bootstrap_with=built['clauses'],with_proof=True) as solver:
        solver.conf_budget(args.conflicts);answer=solver.solve_limited()
        stats=solver.accum_stats()
        trace=solver.get_proof() if answer is False else None
        model=solver.get_model() if answer is True else None
    out=dict(schema='full15-three-atom-search-v1',input_semantic_sha256=identity,
             weighted=args.weighted,case=args.case,status='UNKNOWN',
             cnf_sha256=built['cnf_sha256'],full_clause_count=len(built['clauses']),
             full_variable_count=built['nv'],solver=args.solver,conflict_budget=args.conflicts,
             statistics=stats)
    print(json.dumps(dict(stage='solver',answer=answer,statistics=stats,
                         trace_lines=len(trace) if trace is not None else None)),flush=True)
    if answer is False:
        out.update(status='RESTRICTED_UNSAT_UNCERTIFIED',solver_trace=trace)
        try:
            ids,proof=(fast_trace(built,trace,args.drat_trim) if args.drat_trim else
                       reduce_trace(built['clauses'],trace))
            out.update(initial_clause_ids=ids,rup_clauses=proof)
            checked=replay_case(out,built)
        except (ValueError,AssertionError,KeyError,IndexError,TypeError,subprocess.TimeoutExpired) as error:
            out['certification_error']=str(error)
        else:
            out.update(status='VERIFIED_RESTRICTED_UNSAT',verification=checked)
            del out['solver_trace']
    elif answer is True:
        positives=set(v for v in model if v>0);n=len(data['points'])
        words=[]
        for s in range(3):
            word=''.join(str(next(c for c in range(5) if 5*built['component'][s*n+v]+c+1 in positives))
                         for v in range(n))
            words.append(word)
        out.update(status='SAT_WITNESS_REQUIRES_REPLAY',words=words)
    out['elapsed_seconds']=round(time.monotonic()-started,6)
    if args.drat_trim:out['untrusted_converter_sha256']=sha(args.drat_trim.read_bytes())
    args.output.write_bytes(lzma.compress(canonical(out)))
    print(json.dumps({k:v for k,v in out.items() if k not in
                      ('solver_trace','rup_clauses','initial_clause_ids','words')}),flush=True)


if __name__=='__main__':main()
