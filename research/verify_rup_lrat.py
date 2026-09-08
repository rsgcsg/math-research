"""Small independent checker for the RUP-only subset of textual LRAT.

Every addition is proved entailed by prior clauses using the supplied unit
propagation hints. Negative RAT hints are rejected, not silently skipped.
No SAT solver, native checker, or external proof-generation code is imported.
"""
import gzip
from pathlib import Path


def check(initial,lines):
    clauses={i+1:tuple(c) for i,c in enumerate(initial)}
    maximum=max(abs(lit) for c in initial for lit in c)
    assert all(c and len(c)==len(set(c)) and not any(-lit in c for lit in c) for c in initial)
    last=len(initial)
    additions=deletions=propagations=0
    empty=False
    for line in lines:
        fields=line.split()
        if not fields or fields[0]=='c':
            continue
        assert not empty,'Unexpected data after empty-clause derivation'
        identifier=int(fields[0])
        if fields[1]=='d':
            ids=list(map(int,fields[2:]))
            assert ids and ids[-1]==0 and all(i>0 for i in ids[:-1])
            for i in ids[:-1]:
                assert i in clauses,('deleting missing clause',i)
                del clauses[i]
                deletions+=1
            continue
        values=list(map(int,fields[1:]))
        stop=values.index(0)
        clause=tuple(values[:stop]);hints=values[stop+1:]
        assert hints and hints[-1]==0
        hints=hints[:-1]
        assert all(h>0 for h in hints),'Only positive RUP hints are supported'
        assert identifier>last and identifier not in clauses
        assert len(clause)==len(set(clause))
        assert all(0<abs(lit)<=maximum and -lit not in clause for lit in clause)
        assignment={abs(lit):(-1 if lit>0 else 1) for lit in clause}
        contradiction=False
        for hint in hints:
            assert hint in clauses and hint<identifier,('missing/forward hint',hint)
            unit=0
            for lit in clauses[hint]:
                val=assignment.get(abs(lit),0)
                assert val!=(1 if lit>0 else -1),('satisfied propagation hint',identifier,hint)
                if val==0:
                    assert unit==0,('nonunit propagation hint',identifier,hint)
                    unit=lit
            propagations+=1
            if not unit:
                contradiction=True
                break
            assignment[abs(unit)]=1 if unit>0 else -1
        assert contradiction,('no RUP contradiction',identifier)
        clauses[identifier]=clause
        last=identifier
        additions+=1
        if not clause:
            empty=True
    assert empty,'Proof did not derive the empty clause'
    return dict(status='VERIFIED_RUP_REFUTATION',initial_clauses=len(initial),
                additions=additions,deletions=deletions,hinted_propagations=propagations,
                empty_clause_id=last,rat_steps_accepted=0)


def self_test():
    assert check([[1],[-1]],['3 0 1 2 0'])['additions']==1
    square=[[1,2],[-1,2],[1,-2],[-1,-2]]
    assert check(square,['5 2 0 1 2 0','6 0 5 3 4 0'])['additions']==2
    invalid=[([[1]],['2 0 1 0']),
             ([[1,2]],['2 0 1 0']),
             ([[1],[-1]],['3 0 -1 2 0']),
             ([[1],[-1]],['3 0 9 0']),
             ([[1],[-1]],['3 1 0 1 0'])]
    for initial,lines in invalid:
        try:
            check(initial,lines)
        except (AssertionError,ValueError):
            pass
        else:
            raise AssertionError('Invalid proof accepted')


def parts_clauses(core):
    result=[list(range(4*v+1,4*v+5)) for v in range(509)]
    result += [[-4*a-c-1,-4*b-c-1] for a,b in core['reduced_edges'] for c in range(4)]
    result += [[1],[598],[611]]
    assert len(result)==9548
    return result


def verify_parts(core,path):
    self_test()
    with gzip.open(path,'rt') as stream:
        return check(parts_clauses(core),stream)


if __name__=='__main__':
    import json
    if not __debug__:
        raise SystemExit('Do not disable proof checker assertions.')
    root=Path(__file__).resolve().parents[1]
    core=json.loads((root/'certificates/parts509_core.json').read_text())
    print(json.dumps(verify_parts(core,root/'certificates/parts509_reduced.lrat.gz'),indent=2))
