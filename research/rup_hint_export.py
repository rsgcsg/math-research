"""Untrusted DRUP-to-positive-LRAT exporter (RAT additions are not supported).

Deletion records are validated then ignored: keeping extra clauses is sound
for RUP, not for general RAT. Output must be checked by verify_rup_lrat.
The forward occurrence-list propagation avoids scanning the full graph for
every forced literal; no solver is used to manufacture hints.
"""
from collections import defaultdict,deque


def export(initial, proof_lines):
    clauses={i+1:tuple(c) for i,c in enumerate(initial)}
    occurrence=defaultdict(list);units=[]
    def index(i,c):
        for x in c:occurrence[x].append(i)
        if len(c)==1:units.append(i)
    for i,c in clauses.items():index(i,c)
    def prove(clause):
        assignment={};queue=deque();hints=[]
        def assign(lit):
            assignment[abs(lit)]=lit>0;queue.append(lit)
        for lit in clause:assign(-lit)
        def inspect(i):
            undecided=[]
            for x in clauses[i]:
                v=assignment.get(abs(x))
                if v is None:undecided.append(x)
                elif v==(x>0):return False
            if len(undecided)>1:return False
            hints.append(i)
            if not undecided:return True
            assign(undecided[0]);return False
        for i in units:
            if inspect(i):return hints
        while queue:
            lit=queue.popleft()
            for i in occurrence[-lit]:
                if inspect(i):return hints
        raise ValueError('Non-RUP addition; retain as uncertified, do not infer UNSAT')
    output=[];last=len(initial);finished=False
    for line in proof_lines:
        fields=line.split()
        if not fields or fields[0]=='c':continue
        if finished:raise ValueError('data after empty clause')
        deletion=fields[0]=='d'
        values=list(map(int,fields[1:] if deletion else fields))
        if not values or values[-1]!=0 or 0 in values[:-1]:raise ValueError('bad DRUP text')
        c=tuple(dict.fromkeys(values[:-1]))
        if any(-lit in c for lit in c):raise ValueError('tautological trace unsupported')
        if deletion:continue
        hints=prove(c);last+=1
        output.append(' '.join(map(str,[last,*c,0,*hints,0])))
        clauses[last]=c;index(last,c)
        finished=not c
    if not finished:
        # Some solver APIs omit a final empty clause after root inconsistency.
        # Derive it independently, never infer it from a solver return value.
        hints=prove(());last+=1
        output.append(' '.join(map(str,[last,0,*hints,0])))
    return output
