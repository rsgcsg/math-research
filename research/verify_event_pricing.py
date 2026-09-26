"""Independent semantic CNF reconstruction and strict certificate replay.

Does not import the pricing producer, hint exporter, SAT or numerical tools.
Positive hinted-RUP validation reuses the repository's separate checker;
input and formula validation below fail closed before invoking it.
"""
from collections import Counter
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from verify_rup_lrat import check as check_lrat


def ensure(condition, message):
    if not condition:raise ValueError(message)


def rebuild(n, edges, k, events, coeff, target):
    ensure(type(n) is int and n>0 and type(k) is int and k>0,'dimensions')
    ensure(type(target) is int and len(events)==len(coeff),'objective')
    ensure(n*k<=1000000,'variable resource bound')
    clauses=[];serial=n*k;same={};instructions=[];partitions={}
    def allocate():
        nonlocal serial
        serial+=1;return serial
    for vertex in range(n):
        choices=[vertex*k+c+1 for c in range(k)]
        clauses.append(choices)
        for i in range(k):
            for j in range(i+1,k):clauses.append([-choices[i],-choices[j]])
    used=set()
    for a,b in edges:
        ensure(type(a) is int and type(b) is int and 0<=a<b<n and (a,b) not in used,'edges')
        used.add((a,b))
        for c in range(k):clauses.append([-(a*k+c+1),-(b*k+c+1)])
    def equality(x,y):
        pair=min(x,y),max(x,y)
        if pair not in same:
            out=allocate();same[pair]=out
            if x==y:clauses.append([out])
            else:
                for color in range(k):
                    a=pair[0]*k+color+1;b=pair[1]*k+color+1
                    clauses.append([-a,-b,out]);clauses.append([-out,-a,b])
        return same[pair]
    def full_partition(indices,labels):
        ensure(len(indices)==len(labels) and len(set(indices))==len(indices),'partition size')
        ensure(all(type(i) is int and 0<=i<n for i in indices),'partition index')
        seen=[]
        for x in labels:
            ensure(type(x) is int and 0<=x<k,'partition label')
            if x not in seen:
                ensure(x==len(seen),'partition canonicality');seen.append(x)
        key=(tuple(indices),tuple(labels))
        if key not in partitions:
            representatives=[];conditions=[]
            for index,label in zip(indices,labels):
                if label==len(representatives):representatives.append(index)
                else:conditions.append(equality(index,representatives[label]))
            for i in range(len(representatives)):
                for j in range(i+1,len(representatives)):
                    conditions.append(-equality(representatives[i],representatives[j]))
            out=allocate();partitions[key]=out
            for lit in conditions:clauses.append([-out,lit])
            clauses.append([out]+[-lit for lit in conditions])
        return partitions[key]
    objective=Counter()
    for vertices,coefficient in zip(events,coeff):
        ensure(type(coefficient) is int,'event coefficient')
        if type(vertices) is dict:
            ensure(set(vertices)=={'source','target','pattern'},'event fields')
            left=full_partition(vertices['source'],vertices['pattern'])
            right=full_partition(vertices['target'],vertices['pattern'])
        else:
            ensure(len(vertices)==4 and all(type(v) is int and 0<=v<n for v in vertices),'event indices')
            if coefficient==0:continue
            left=equality(vertices[0],vertices[1]);right=equality(vertices[2],vertices[3])
        objective[left]+=coefficient;objective[right]-=coefficient
    objective={key:value for key,value in objective.items() if value}
    correction=sum(value for value in objective.values() if value<0)
    terms=sorted((var,value) for var,value in objective.items())
    positive=[(v if w>0 else -v,abs(w)) for v,w in terms]
    total=sum(w for _,w in positive);limit=target-correction;width=total.bit_length()
    ensure(width<=4096 and len(positive)*max(width,1)<=200000,'circuit resource bound')
    zero=allocate();clauses.append([-zero])
    def operation(kind,x,y):
        constant=None
        # Use Boolean truth values for constant/identical-input simplification.
        if x==y:constant=x if kind!='xor' else zero
        elif x==-y:constant=zero if kind=='and' else -zero
        elif abs(x)==zero or abs(y)==zero:
            if abs(y)==zero:x,y=y,x
            truth=x<0
            if kind=='and':constant=y if truth else zero
            elif kind=='or':constant=-zero if truth else y
            elif kind=='xor':constant=-y if truth else y
        if constant is not None:return constant
        out=allocate();instructions.append((kind,x,y,out))
        if kind=='and':block=[[-out,x],[-out,y],[out,-x,-y]]
        elif kind=='or':block=[[out,-x],[out,-y],[-out,x,y]]
        else:block=[[x,y,-out],[-x,-y,-out],[x,-y,out],[-x,y,out]]
        clauses.extend(block);return out
    accum=[zero for _ in range(width)]
    if limit<0:clauses.append([zero])
    elif limit<total:
        for signed,weight in positive:
            next_bits=[];carry=zero
            for position,old in enumerate(accum):
                bit=signed if (weight//2**position)%2 else zero
                partial=operation('xor',old,bit)
                next_bits.append(operation('xor',partial,carry))
                left=operation('and',old,bit);right=operation('and',partial,carry)
                carry=operation('or',left,right)
            accum=next_bits
        for position in reversed(range(width)):
            if limit & (1<<position):continue
            c=[-accum[position]]
            for higher in range(width-1,position,-1):
                c.append(-accum[higher] if limit & (1<<higher) else accum[higher])
            if -zero in c or set(c).intersection(-x for x in c):continue
            c=list(dict.fromkeys(x for x in c if x!=zero))
            clauses.append(c or [zero])
    encoded=('p cnf %d %d\n'%(serial,len(clauses))+
             ''.join(' '.join(str(x) for x in clause)+' 0\n' for clause in clauses)).encode()
    return dict(nv=serial,clauses=clauses,cnf_sha256=hashlib.sha256(encoded).hexdigest(),
                equality=same,partitions=partitions,gates=instructions,false=zero,sum_bits=accum)


def partition_value(word,indices,pattern):
    labels={};value=tuple(labels.setdefault(word[i],len(labels)) for i in indices)
    return value==tuple(pattern)


def score(word, events, coefficients):
    result=0
    for event,v in zip(events,coefficients):
        if type(event) is dict:
            a=partition_value(word,event['source'],event['pattern'])
            b=partition_value(word,event['target'],event['pattern'])
        else:
            p,q,x,y=event;a=word[p]==word[q];b=word[x]==word[y]
        result+=v*(int(a)-int(b))
    return result


def verify_query(instance, query):
    if not __debug__:raise RuntimeError('verification requires assertions')
    ensure(set(query)=={'coefficients','target','cnf_sha256','proof','status'},'query fields')
    ensure(query['status']=='NO_WORD_AT_OR_BELOW_TARGET','verdict')
    built=rebuild(instance['n'],instance['edges'],instance['k'],instance['events'],
                  query['coefficients'],query['target'])
    ensure(built['cnf_sha256']==query['cnf_sha256'],'CNF mismatch')
    proof=query['proof'];ensure(isinstance(proof,list) and all(type(x) is str for x in proof),'proof lines')
    # Strict inputs protect the inherited assertion-based checker.
    for clause in built['clauses']:
        ensure(bool(clause) and len(clause)==len(set(clause)) and
               all(type(x) is int and 0<abs(x)<=built['nv'] and -x not in clause for x in clause),'CNF literal')
    report=check_lrat(built['clauses'],proof)
    return dict(status='PASS',target=query['target'],lower_bound=query['target']+1,
                strictly_positive_on_all_words=query['target']>=0,
                cnf_sha256=built['cnf_sha256'],rup=report)


def check_word(word,n,k,edges):
    ensure(type(k) is int and 1<=k<=10 and type(word) is str and len(word)==n and set(word)<=set(map(str,range(k))),'word alphabet')
    ensure(all(word[a]!=word[b] for a,b in edges),'improper word')


def bind_events(records, mappings):
    """Bind every source/target point to the actual isometry, not just a name."""
    events=[]
    for row in records:
        if type(row) is dict:
            ensure(set(row)=={'motion','source','pattern'},'partition record')
            j=row['motion'];ensure(type(j) is int and 0<=j<len(mappings),'motion')
            mapping=dict(mappings[j]);source=row['source']
            ensure(type(source) is list and all(type(i) is int and i in mapping for i in source),'partition source')
            events.append(dict(source=source,target=[mapping[i] for i in source],pattern=row['pattern']))
        else:
            ensure(type(row) is list and len(row)==5 and all(type(i) is int for i in row),'event record')
            j,a,b,x,y=row;ensure(0<=j<len(mappings) and a!=b,'motion index or equal sources')
            mapping=dict(mappings[j]);ensure(mapping.get(a)==x and mapping.get(b)==y,'false geometric mapping')
            events.append([a,b,x,y])
    return events


def verify_saved_result(root,result):
    """Verify a frontend result against freshly reconstructed actual geometry."""
    if not __debug__:raise RuntimeError('verification requires assertions')
    from audit_full_law_preparation import reconstruct
    data,summary=reconstruct(root)
    ensure(result['schema']=='event-pricing-result-v1','result schema')
    ensure(result['input_semantic_sha256']==summary['semantic_sha256'],'input source')
    request=result['request'];ensure(request['schema']=='event-pricing-request-v1','request schema')
    events=bind_events(request['events'],data['mappings'])
    instance=dict(n=len(data['points']),k=5,edges=data['edges'],events=events)
    if result['status']=='SAT_WITNESS':
        # Rebuilding also validates coefficient types, objective, and descriptors.
        built=rebuild(**instance,coeff=request['coefficients'],target=request['target'])
        ensure(built['cnf_sha256']==result['cnf_sha256'],'SAT CNF binding')
        check_word(result['word'],instance['n'],5,instance['edges'])
        value=score(result['word'],events,request['coefficients'])
        ensure(type(result['value']) is int and value==result['value'] and value<=request['target'],'SAT objective')
        return dict(status='VERIFIED_SAT_WITNESS',value=value,scope='This one pricing query only.')
    if result['status']=='VERIFIED_NO_WORD_AT_OR_BELOW_TARGET':
        query=result['query']
        ensure(query['coefficients']==request['coefficients'] and query['target']==request['target'],'query request')
        # Validate request independently, so bool/int comparison cannot erase a malformed request.
        bound=rebuild(**instance,coeff=request['coefficients'],target=request['target'])
        ensure(bound['cnf_sha256']==query['cnf_sha256']==result['cnf_sha256'],'request CNF')
        return verify_query(instance,query)
    ensure(result['status'] in ('UNKNOWN','UNSAT_UNCERTIFIED'),'unknown status')
    return dict(status='NO_MATHEMATICAL_VERDICT',reported_status=result['status'])


if __name__=='__main__':
    if not __debug__:raise RuntimeError('verification requires assertions')
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args()
    def pairs(items):
        value={}
        for k,v in items:
            ensure(k not in value,'duplicate JSON key');value[k]=v
        return value
    result=json.loads(args.result.read_text(),object_pairs_hook=pairs)
    print(json.dumps(verify_saved_result(Path(__file__).resolve().parents[1],result),indent=2))
