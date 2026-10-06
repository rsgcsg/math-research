"""Independently check the fixed-singleton joint-observation experiment.

The actual Y and the 129-point observation orbit are verified by the caller.
The CNF is rebuilt by the existing independent packet checker, never by the
search encoder. A selected initial subformula and its hinted-RUP derivation
are checked. This cannot be used to reject an arbitrary probability law.
"""
from pathlib import Path
from copy import deepcopy
from itertools import permutations
import hashlib
import json
from verify_motion_packet import rebuild_singleton, require, pattern, read
from verify_rup_lrat import check as check_rup

SCOPE = ('No single full-Y proper five-color partition satisfies all15 complete '
         'local129-kernel domains, the complete Y-u domain and the twelve inherited '
         'pair events. This is a single-atom restriction, not an obstruction to '
         'arbitrary probability laws.')


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def equal(a,b,message):
    require(canonical(a)==canonical(b),message)


def prepare(cert,data,summary,orbit,event_records,event_raw):
    """Bind and rebuild the exact semantics, then return the initial CNF."""
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    fields=['cnf_sha256','date','full_clauses','full_variables','initial_clause_ids',
            'input_semantic_sha256','kernel_Y_indices','kernel_only_word','mapping_sizes',
            'prior_event_certificate_sha256','proof','proof_report','schema','scope']
    equal(sorted(cert),sorted(fields),'singleton fields')
    equal(cert['schema'],'hn-joined-kernel-singleton-v1','singleton schema')
    equal(cert['date'],'2026-09-28','singleton date')
    equal(cert['scope'],SCOPE,'singleton scope')
    equal(cert['input_semantic_sha256'],summary['semantic_sha256'],'singleton geometry')
    equal(cert['kernel_Y_indices'],orbit['transport']['kernel_Y_indices'],'singleton kernel')
    equal(cert['prior_event_certificate_sha256'],hashlib.sha256(event_raw).hexdigest(),'singleton event binding')
    kernel=cert['kernel_Y_indices'];ix={v:i for i,v in enumerate(kernel)}
    local_maps=[[[a,b] for a,b in mm if a in ix and b in ix] for mm in data['mappings']]
    eta=dict(local_maps[2]);closed=set()
    for v in kernel:
        current=v;orbit_points=[]
        for _ in range(5):
            if current not in eta:break
            orbit_points.append(current);current=eta[current]
        if len(orbit_points)==5 and current==v:closed.update(orbit_points)
    require(len(closed)==121 and [v for v in sorted(closed) if eta[v]==v]==[4641], 'closed C5 subset')
    require(all(x==0 for x in data['points'][4641]),'rotation fixed point is not the origin')

    pairs=[row for row in event_records if row[0]!=14]
    require(len(pairs)==12,'twelve additional pair events required')
    for j,a,b,x,y in pairs:
        mm=dict(data['mappings'][j]);require(mm.get(a)==x and mm.get(b)==y,'unphysical pair event')
    maps=local_maps+[data['mappings'][14]]+[[[a,x],[b,y]] for j,a,b,x,y in pairs]
    equal(cert['mapping_sizes'],list(map(len,maps)),'singleton domain sizes')
    built=rebuild_singleton(len(data['points']),data['edges'],5,maps)
    equal(cert['cnf_sha256'],built['cnf_sha256'],'independent singleton CNF differs')
    equal(cert['full_variables'],built['nv'],'variable count')
    equal(cert['full_clauses'],len(built['clauses']),'clause count')
    # The kernel itself has a proper invariant single word; the negative
    # query above genuinely includes the full Y edges and additional domains.
    word=cert['kernel_only_word']
    require(isinstance(word,str) and len(word)==len(kernel) and set(word)<=set('01234'),'kernel word shape')
    require(all(word[ix[a]]!=word[ix[b]] for a,b in data['edges'] if a in ix and b in ix),'improper kernel-only word')
    require(all(pattern(word,[ix[a] for a,b in mm])==pattern(word,[ix[b] for a,b in mm])
                for mm in local_maps),'kernel-only complete-domain invariance')
    return built['clauses']


def replay(cert,initial):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    ids=cert['initial_clause_ids']
    require(isinstance(ids,list) and ids and all(type(i) is int and 1<=i<=len(initial) for i in ids),'initial clause references')
    require(ids==sorted(set(ids)),'initial clause IDs must be increasing and unique')
    require(isinstance(cert['proof'],list) and all(isinstance(s,str) for s in cert['proof']),'proof format')
    report=check_rup([initial[i-1] for i in ids],cert['proof'])
    equal(report,cert['proof_report'],'reported proof statistics')
    return report


def check(cert,data,summary,orbit,event_records,event_raw,mutations=False):
    initial=prepare(cert,data,summary,orbit,event_records,event_raw)
    report=replay(cert,initial);rejected=[]
    if mutations:
        for name,change in {
            'proof-truncated':lambda c:c['proof'].pop(),
            'negative-RAT-hint':lambda c:c['proof'].__setitem__(-1,c['proof'][-1].replace(' 0 ',' 0 -',1)),
            'initial-id-out-of-range':lambda c:c['initial_clause_ids'].__setitem__(0,len(initial)+1),
            'initial-id-boolean':lambda c:c['initial_clause_ids'].__setitem__(0,True),
            'false-proof-statistics':lambda c:c['proof_report'].__setitem__('additions',0),
        }.items():
            bad=deepcopy(cert);change(bad)
            try:replay(bad,initial)
            except (ValueError,AssertionError,KeyError,IndexError):rejected.append(name)
            else:raise AssertionError('invalid singleton proof accepted: '+name)
        for name,change in {
            'wrong-CNF-hash':lambda c:c.__setitem__('cnf_sha256','0'*64),
            'law-not-singleton-scope':lambda c:c.__setitem__('scope','No probability law exists'),
            'missing-domain':lambda c:c['mapping_sizes'].pop(),
            'invalid-kernel-positive-word':lambda c:c.__setitem__('kernel_only_word','0'*129),
        }.items():
            bad=deepcopy(cert);change(bad)
            try:prepare(bad,data,summary,orbit,event_records,event_raw)
            except (ValueError,AssertionError,KeyError,IndexError):rejected.append(name)
            else:raise AssertionError('invalid singleton input accepted: '+name)
    permutation_checks=0
    for degree in range(1,6):
        for perm in permutations(range(degree)):
            permutation_checks+=1
            power=list(range(degree))
            for _ in range(5):power=[perm[x] for x in power]
            if power==list(range(degree)) and (degree<5 or perm[0]==0):
                require(list(perm)==list(range(degree)),'prime-order fixed-support calibration')
    return dict(closed_eta_points=121, fixed_eta_points=[4641],
                small_support_permutation_calibrations=permutation_checks,
                status='PASS',query='FIXED_SINGLETON_ONLY',maps=28,full_variables=cert['full_variables'],
                full_clauses=cert['full_clauses'],proof_report=report,kernel_local_singleton_positive=True,
                rejected_mutations=rejected,arbitrary_law_infeasibility_proved=False)


LAW_SCOPE = ('A five-atom probability law on the full proper Y space for F=all15 '
    'local129-kernel complete domains, the complete Y-u domain and twelve inherited '
    'pair events. It is extreme in the entire F-law polytope, not a fullY15 law; '
    'minimum support is only bounded between two and five.')


def check_law(law,data,summary,orbit,event_records):
    from fractions import Fraction
    from collections import Counter
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    equal(law['schema'],'hn-joined-kernel-five-law-v1','positive law schema')
    equal(law['date'],'2026-09-28','positive law date')
    equal(law['scope'],LAW_SCOPE,'positive law scope')
    equal(law['input_semantic_sha256'],summary['semantic_sha256'],'law geometry')
    equal(law['observation_kernel_Y_indices'],orbit['transport']['kernel_Y_indices'],'law observation kernel')
    kernel=set(law['observation_kernel_Y_indices']);n=len(data['points'])
    maps=[[[a,b] for a,b in mm if a in kernel and b in kernel] for mm in data['mappings']]
    maps+=[data['mappings'][14]]+[[[a,x],[b,y]] for j,a,b,x,y in event_records if j!=14]
    words=law['words'];equal(law['weights'],['1/5']*5,'probability weights')
    require(isinstance(words,list) and len(words)==5,'positive law word count')
    for word in words:
        require(isinstance(word,str) and len(word)==n and set(word)<=set('01234'),'positive law word shape')
        require(all(word[a]!=word[b] for a,b in data['edges']),'improper full-Y law word')
    require(len({pattern(w,list(range(n))) for w in words})==5,'five distinct full partitions required')
    for j,mm in enumerate(maps):
        left=Counter(pattern(w,[a for a,b in mm]) for w in words)
        right=Counter(pattern(w,[b for a,b in mm]) for w in words)
        require(left==right,'complete observation law failed at '+str(j))
    R=orbit['core']['orbit_Y_indices'];eta=dict(data['mappings'][2])
    equal(law['closed_eta_Y_indices'],R,'law closed eta witness')
    require(all(v in eta for v in R) and sorted(eta[v] for v in R)==R,'law extremality domain not closed')
    left=[pattern(w,R) for w in words];right=[pattern(w,[eta[v] for v in R]) for w in words]
    require(len(set(left))==5 and set(left)==set(right),'distinct closed-set patterns')
    matching=[[int(a==b) for b in right] for a in left]
    equal(law['eta_matching'],matching,'law matching matrix')
    cycle=law['eta_support_cycle'];require(cycle[0]==0 and sorted(cycle)==list(range(5)),'law cycle shape')
    require(all(matching[cycle[i]][cycle[(i+1)%5]]==1 for i in range(5)), 'law five-cycle extremality')
    rows=[]
    for part in sorted(set(left+right)):
        coef=[int(a==part)-int(b==part) for a,b in zip(left,right)]
        if any(coef):rows.append(dict(pattern=[list(b) for b in part],coefficients=coef))
    equal(law['eta_balance_rows'],rows,'real closed-set balance rows')
    matrix=[[Fraction(1)]*5]+[[Fraction(x) for x in row['coefficients']] for row in rows[:4]]
    determinant=Fraction(1)
    for col in range(5):
        pivot=next((i for i in range(col,5) if matrix[i][col]),None)
        require(pivot is not None,'rank deficient probability uniqueness')
        if pivot!=col:matrix[pivot],matrix[col]=matrix[col],matrix[pivot];determinant=-determinant
        val=matrix[col][col];determinant*=val
        matrix[col]=[x/val for x in matrix[col]]
        for i in range(col+1,5):
            val=matrix[i][col];matrix[i]=[x-val*y for x,y in zip(matrix[i],matrix[col])]
    require(abs(determinant)==5,'probability uniqueness determinant')
    full=[j for j,mm in enumerate(data['mappings']) if Counter(pattern(w,[a for a,b in mm]) for w in words)==Counter(pattern(w,[b for a,b in mm]) for w in words)]
    equal(law['full_Y_passed_domains'],full,'full-Y domain scope')
    equal(full,[14],'unexpected original-domain law status')
    return dict(status='PASS',full_Y_edge_checks=5*len(data['edges']),complete_observation_domains=len(maps),
                distinct_atoms=5,extremality_determinant=str(determinant),extreme_in_full_F_law_polytope=True,
                minimum_support_known_interval=[2,5],minimum_support_five_proved=False,
                only_original_Y_complete_domains=full,
                no_strict_all_word_separator_supported_on_F=True,
                scope='Exact positive five-atom law, not an original fullY15 law. Extremality follows from nonnegativity plus these full-rank probability equations, as proved in the text.')


if __name__=='__main__':
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    from audit_full_law_preparation import reconstruct
    from verify_cycle_descent import check as check_orbit
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    l=root/'certificates/localized_motion_packet.json';e=root/'certificates/shared_event_research.json.gz'
    orbit=read(root/'certificates/original_Y_cycle_descent.json');prior=read(e)
    check_orbit(orbit,data,summary,read(l),l.read_bytes(),prior,e.read_bytes())
    result=check(read(root/'certificates/joined_kernel_singleton.json.gz'),data,summary,orbit,prior['event_records'],e.read_bytes(),True)
    result['five_atom_law']=check_law(read(root/'certificates/joined_kernel_five_law.json'),data,summary,orbit,prior['event_records'])
    print(json.dumps(result,indent=2))
