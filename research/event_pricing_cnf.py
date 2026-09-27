"""Exact shared-equality-event pricing with logarithmic-width integer sums.

The formula encodes all proper k-colorings, with no saved word, fixed palette,
periodicity or support-size assumption. Solvers are not imported here.
"""
from collections import Counter
from itertools import combinations
import hashlib


def integer(x, name, low=None):
    if type(x) is not int or (low is not None and x < low):
        raise ValueError('invalid integer: ' + name)
    return x


def dimacs(nv, clauses):
    return ('p cnf %d %d\n' % (nv, len(clauses)) +
            ''.join(' '.join(map(str,c)) + ' 0\n' for c in clauses)).encode()


def formula(n, edges, k, events, coefficients, target):
    """events contain (a,b,x,y): the difference [a=b]-[x=y]."""
    integer(n,'n',1);integer(k,'k',1);integer(target,'target')
    if len(events)!=len(coefficients):raise ValueError('coefficient length')
    if n*k > 1000000:raise ValueError('declared variable limit')
    top=n*k;clauses=[];eq={};gates=[];partitions={}
    def fresh():
        nonlocal top
        top+=1;return top
    def color(i,c):return i*k+c+1
    for i in range(n):
        vs=[color(i,c) for c in range(k)]
        clauses.append(vs)
        clauses.extend([[-a,-b] for a,b in combinations(vs,2)])
    seen=set()
    for edge in edges:
        if len(edge)!=2:raise ValueError('edge arity')
        a,b=edge
        if any(type(i) is not int or not 0<=i<n for i in edge) or a>=b or (a,b) in seen:
            raise ValueError('noncanonical edge')
        seen.add((a,b))
        clauses.extend([[-color(a,c),-color(b,c)] for c in range(k)])
    def equal(a,b):
        key=tuple(sorted((a,b)))
        if key not in eq:
            e=fresh();eq[key]=e
            if a==b:clauses.append([e])
            else:
                for c in range(k):
                    x,y=color(key[0],c),color(key[1],c)
                    clauses.extend([[-x,-y,e],[-e,-x,y]])
        return eq[key]
    def partition(ids,pattern):
        ids=tuple(ids);pattern=tuple(pattern)
        if len(ids)!=len(pattern) or len(set(ids))!=len(ids):raise ValueError('partition domain')
        if any(type(i) is not int or not 0<=i<n for i in ids):raise ValueError('partition vertex')
        labels={};normal=[]
        for c in pattern:
            integer(c,'partition label',0);normal.append(labels.setdefault(c,len(labels)))
        if tuple(normal)!=pattern or len(labels)>k:raise ValueError('noncanonical partition')
        key=(ids,pattern)
        if key not in partitions:
            roots={};terms=[]
            for i,c in zip(ids,pattern):
                if c in roots:terms.append(equal(i,roots[c]))
                else:roots[c]=i
            terms.extend(-equal(i,j) for i,j in combinations(roots.values(),2))
            e=fresh();partitions[key]=e
            clauses.extend([[-e,t] for t in terms]);clauses.append([e]+[-t for t in terms])
        return partitions[key]
    weights=Counter()
    for event,v in zip(events,coefficients):
        integer(v,'coefficient')
        if isinstance(event,dict):
            if set(event)!={'source','target','pattern'}:raise ValueError('partition fields')
            # Validate even zero-weight records by constructing the event.
            left=partition(event['source'],event['pattern']);right=partition(event['target'],event['pattern'])
        else:
            if len(event)!=4 or any(type(i) is not int or not 0<=i<n for i in event):
                raise ValueError('event vertices')
            if not v:continue
            a,b,x,y=event;left=equal(a,b);right=equal(x,y)
        weights[left]+=v;weights[right]-=v
    weights={v:w for v,w in weights.items() if w}
    offset=sum(w for w in weights.values() if w<0)
    terms=[(v if w>0 else -v,abs(w)) for v,w in sorted(weights.items())]
    total=sum(w for _,w in terms);bound=target-offset
    bits=total.bit_length()
    if bits>4096 or len(terms)*max(bits,1)>200000:raise ValueError('declared circuit limit')
    false=fresh();clauses.append([-false])
    def gate(op,a,b):
        if op=='and':
            if false in (a,b) or a==-b:return false
            if a==-false:return b
            if b==-false or a==b:return a
        if op=='or':
            if -false in (a,b) or a==-b:return -false
            if a==false:return b
            if b==false or a==b:return a
        if op=='xor':
            if a==b:return false
            if a==-b:return -false
            if a==false:return b
            if b==false:return a
            if a==-false:return -b
            if b==-false:return -a
        z=fresh();gates.append((op,a,b,z))
        if op=='and':clauses.extend([[-z,a],[-z,b],[z,-a,-b]])
        elif op=='or':clauses.extend([[z,-a],[z,-b],[-z,a,b]])
        elif op=='xor':clauses.extend([[a,b,-z],[-a,-b,-z],[a,-b,z],[-a,b,z]])
        else:raise ValueError(op)
        return z
    acc=[false]*bits
    if bound<0:
        clauses.append([false])
    elif bound<total:
        for lit,weight in terms:
            carry=false;out=[]
            for i,a in enumerate(acc):
                b=lit if (weight>>i)&1 else false
                p=gate('xor',a,b);out.append(gate('xor',p,carry))
                carry=gate('or',gate('and',a,b),gate('and',p,carry))
            acc=out
        for i in range(bits-1,-1,-1):
            if not ((bound>>i)&1):
                clause=[-acc[i]]+[-acc[j] if (bound>>j)&1 else acc[j]
                                   for j in range(bits-1,i,-1)]
                # Simplify constants, duplicates and tautologies canonically.
                if -false in clause or any(-x in clause for x in clause):continue
                clause=list(dict.fromkeys(x for x in clause if x!=false))
                if not clause:clauses.append([false])
                else:clauses.append(clause)
    raw=dimacs(top,clauses)
    return dict(nv=top,clauses=clauses,cnf_sha256=hashlib.sha256(raw).hexdigest(),
                equality=eq,partitions=partitions,gates=gates,false=false,terms=terms,offset=offset,
                total=total,bound=bound,sum_bits=acc)
