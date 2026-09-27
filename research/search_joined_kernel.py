"""Search and certify the singleton version of the joined observation family.

Requires python-sat only for search. Independent verification is performed by
verify_joined_kernel.py. A negative singleton result does not refute a law.
For 2..5 equal-weight words an optional sound C5 consequence helps search;
negative/UNKNOWN results in those models are never promoted to arbitrary laws.
"""
from pathlib import Path
from itertools import permutations
import argparse
import gzip
import hashlib
import json
import time
from verify_motion_packet import read


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def compact_proof(initial,proof):
    """Backward-select the proof dependencies; this is not a proof checker."""
    n=len(initial);steps={}
    for line in proof:
        row=list(map(int,line.split()));identifier=row.pop(0);end=row.index(0)
        if row[-1]!=0:raise ValueError('invalid proof delimiters')
        steps[identifier]=(row[:end],row[end+1:-1])
    if not steps or steps[max(steps)][0]:raise ValueError('no final contradiction')
    needed={max(steps)};todo=list(needed)
    while todo:
        current=todo.pop()
        if current>n:
            for hint in steps[current][1]:
                if hint not in needed:needed.add(hint);todo.append(hint)
    orig=sorted(i for i in needed if i<=n);learned=sorted(i for i in needed if i>n)
    maximum=max((abs(v) for i in learned for v in steps[i][0]),default=0)
    if max(abs(v) for i in orig for v in initial[i-1])<maximum:
        orig=sorted(set(orig)|{next(i+1 for i,c in enumerate(initial) if any(abs(v)>=maximum for v in c))})
    ids={i:j+1 for j,i in enumerate(orig+learned)}
    lines=[' '.join(map(str,[ids[i]]+steps[i][0]+[0]+[ids[j] for j in steps[i][1]]+[0])) for i in learned]
    return orig,lines


def main():
    from pysat.solvers import Solver
    from motion_packet_cnf import singleton_formula
    from quintic_multiword_joint import MultiwordEncoding
    from rup_hint_export import export
    from verify_rup_lrat import check as check_rup
    from verify_motion_packet import full_law_domains, pattern
    from fractions import Fraction
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--certificate-output',type=Path,help='Optional gzip certificate, only on independently replayed singleton RUP')
    parser.add_argument('--words',type=int,choices=range(1,6),default=1)
    parser.add_argument('--conflicts',type=int,default=10000)
    parser.add_argument('--relator',action='store_true',help='Use the proved C5 fixed-point consequence when words<5; see T143 proof section6.2')
    parser.add_argument('--phase-seed',choices=('zero','e083'),default='zero')
    parser.add_argument('--fixed-non-u-e083',action='store_true',help='Positive-construction ansatz: five words, fix only the weaker F non-u support/palette matches to an E083-compatible choice, never full old14 domains.')
    args=parser.parse_args()
    if args.fixed_non_u_e083 and args.words!=5:raise ValueError('the E083 matching construction uses exactly five words')
    if args.conflicts<=0:raise ValueError('positive conflict budget required')
    root=Path(__file__).resolve().parents[1];data=read(args.cache)
    orbit=read(root/'certificates/original_Y_cycle_descent.json')
    if hashlib.sha256(canonical(data)).hexdigest()!=orbit['input_semantic_sha256']:
        raise ValueError('wrong cached geometry')
    old_path=root/'certificates/shared_event_research.json.gz';old=read(old_path)
    vertices=orbit['transport']['kernel_Y_indices'];K=set(vertices)
    mappings=[[[a,b] for a,b in mm if a in K and b in K] for mm in data['mappings']]
    mappings += [data['mappings'][14]]+[[[a,x],[b,y]] for j,a,b,x,y in old['event_records'] if j!=14]
    m=args.words;n=len(data['points'])
    if m==1:
        built=singleton_formula(n,data['edges'],5,mappings);clauses=built['clauses'];top=built['nv']
    else:
        enc=MultiwordEncoding(n,data['edges'],m);clauses=enc.clauses;del enc.clauses
        for j,mm in enumerate(mappings):
            clauses.extend(enc.add_motion(mm))
            if args.fixed_non_u_e083 and j!=15:
                source=[a for a,b in mm];target=[b for a,b in mm];seed=data['words']
                sigma=next(p for p in permutations(range(5)) if all(pattern(seed[a],source)==pattern(seed[p[a]],target) for a in range(5)))
                support_vars,palette_vars=enc.witness_vars[-1]
                for a,b in enumerate(sigma):
                    clauses.append([support_vars[a][b]])
                    known={int(seed[a][x]):int(seed[b][y]) for x,y in mm}
                    available=iter(c for c in range(5) if c not in known.values())
                    palette=[known[c] if c in known else next(available) for c in range(5)]
                    for c,d in enumerate(palette):clauses.append([palette_vars[a][c][d]])
        top=enc.top
    closed=set();eta=dict(mappings[2])
    if args.relator and m<5:
        for a in vertices:
            v=a;visited=[]
            for _ in range(5):
                if v not in eta:break
                visited.append(v);v=eta[v]
            if len(visited)==5 and v==a:closed.update(visited)
        if not any(eta[v]==v for v in closed):raise ValueError('fixed point needed for k=5 color constancy')
        for t in range(m):
            for a in sorted(closed):
                b=eta[a]
                for c in range(5):
                    x=t*n*5+5*a+c+1;y=t*n*5+5*b+c+1
                    if x!=y:clauses.extend([[-x,y],[x,-y]])
    raw=('p cnf %d %d\n'%(top,len(clauses))+''.join(' '.join(map(str,row))+' 0\n' for row in clauses)).encode()
    start=time.monotonic()
    solver_name='g3' if m==1 else 'cadical195'
    with Solver(name=solver_name,bootstrap_with=clauses,with_proof=(m==1)) as solver:
        seed=data['words'] if args.phase_seed=='e083' else [orbit['joined_zero']['word']]
        solver.set_phases([t*n*5+5*i+int(c)+1 for t in range(m) for i,c in enumerate(seed[t%len(seed)])])
        solver.conf_budget(args.conflicts);answer=solver.solve_limited();stats=solver.accum_stats()
        model=solver.get_model() if answer else None
        trace=solver.get_proof() if answer is False and m==1 else None
    result=dict(schema='hn-joined-observation-search-v1',equal_weight_words=m,
        status='SAT_WITNESS' if answer else ('UNSAT_FIXED_MODEL_UNCERTIFIED' if answer is False else 'UNKNOWN_FIXED_MODEL'),
        variables=top,clauses=len(clauses),cnf_sha256=hashlib.sha256(raw).hexdigest(),
        conflicts=args.conflicts,statistics=stats,seconds=time.monotonic()-start,
        relator_equalities_added=bool(closed),closed_eta_points=len(closed),
        phase_seed=args.phase_seed,fixed_non_u_E083_matching=args.fixed_non_u_e083,
        scope='Fixed equal-weight word count only; no arbitrary-law negative inference.')
    if model:
        positive=set(model)
        words=[''.join(str(next(c for c in range(5) if t*n*5+5*i+c+1 in positive)) for i in range(n)) for t in range(m)]
        if not all(w[a]!=w[b] for w in words for a,b in data['edges']):raise ValueError('bad solver word')
        passed,_=full_law_domains(words,[Fraction(1,m)]*m,mappings)
        if passed!=list(range(len(mappings))):raise ValueError('bad solver common-law witness')
        result['words']=words
    if trace is not None and not closed:
        # A relator-augmented proof requires an additional semantics record;
        # this producer intentionally certifies only the original singleton CNF.
        try:
            proof=export(clauses,trace);orig,proof=compact_proof(clauses,proof)
            report=check_rup([clauses[i-1] for i in orig],proof)
            template=read(root/'certificates/joined_kernel_singleton.json.gz')
            certificate=dict(template,initial_clause_ids=orig,proof=proof,proof_report=report,
                full_clauses=len(clauses),full_variables=top,cnf_sha256=built['cnf_sha256'])
            if args.certificate_output:
                payload=bytearray(gzip.compress(json.dumps(certificate,separators=(',',':')).encode()+b'\n',mtime=0));payload[9]=255
                args.certificate_output.parent.mkdir(parents=True,exist_ok=True);args.certificate_output.write_bytes(payload)
            result.update(status='RUP_FIXED_SINGLETON',proof_report=report,
                independent_semantics_replay_required=True)
        except (ValueError,AssertionError,KeyError,IndexError) as error:
            result['proof_export_error']=str(error)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='words'},indent=2))


if __name__=='__main__':main()
