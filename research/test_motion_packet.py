"""Solver-free T141/T142/E113/C025 checks and exact finite calibrations."""
from copy import deepcopy
from itertools import product, permutations
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from audit_full_law_preparation import reconstruct
from verify_motion_packet import (check, fast_checks, read, rebuild_singleton,
                                  require, verify_word, full_law_domains, pattern, CORE, BASE)
from verify_event_pricing import bind_events, score
from fractions import Fraction


def calibration():
    cases = [
        (1, [], 2, [[(0,0)]]),
        (3, [(0,1)], 2, [[(0,1),(1,0),(2,2)]]),
        (4, [(0,1),(0,2),(1,2)], 3, [[(0,1),(1,2),(2,0),(3,3)]]),
        (4, [(0,1),(1,2)], 2, [[(0,0),(2,3)],[(0,1),(2,3)]]),
    ]
    assignments = 0
    flips = 0
    # Exhaustively compare the CNF with its definition, including all colors,
    # all independent palette permutations and fixed-point tautologies.
    for n, edges, k, maps in cases:
        built = rebuild_singleton(n, edges, k, maps)
        for colors in product(range(k), repeat=n):
            for palettes in product(list(permutations(range(k))), repeat=len(maps)):
                true = {v*k+c+1 for v,c in enumerate(colors)}
                for j, perm in enumerate(palettes):
                    true.update(n*k+j*k*k+1+c*k+d for c,d in enumerate(perm))
                observed = all(any((v in true) if v>0 else (-v not in true) for v in clause)
                               for clause in built['clauses'])
                expected = all(colors[a]!=colors[b] for a,b in edges) and all(
                    colors[b]==pi[colors[a]] for mapping, pi in zip(maps,palettes) for a,b in mapping)
                require(observed==expected, 'CNF semantic calibration failed')
                assignments += 1
                for bit in range(1,built['nv']+1):
                    changed = true ^ {bit}
                    # Flipping any one bit destroys a vertex exactly-one or a
                    # palette permutation row/column, regardless of graph edges.
                    accepts = all(any((v in changed) if v>0 else (-v not in changed)
                                      for v in clause) for clause in built['clauses'])
                    require(not accepts, 'accepted one-hot/permutation bit flip')
                    flips += 1
    # A five-state abstract flow: min support is 2, but its 3-cycle law is not
    # in the convex hull of 2-supported laws. Not a planar geometry example.
    successor = [1,0,3,4,2]
    feasible_pairs = []
    for a in range(5):
        for b in range(a+1,5):
            w = [Fraction(int(i in (a,b)),2) for i in range(5)]
            if all(w[i]==w[successor[i]] for i in range(5)):
                feasible_pairs.append([a,b])
    three = [Fraction(0),Fraction(0),Fraction(1,3),Fraction(1,3),Fraction(1,3)]
    require(feasible_pairs==[[0,1]] and all(three[i]==three[successor[i]] for i in range(5)),
            'abstract packet-convexity calibration')
    return dict(cases=len(cases), color_and_permutation_assignments=assignments,
                one_bit_rejections=flips, abstract_two_packet_hull_counterexample=True)


def exploration_checks(exp, data, summary):
    require(exp['schema']=='motion-packet-exploration-v1' and
            exp['input_semantic_sha256']==summary['semantic_sha256'], 'exploration binding')
    pricing = exp['pricing_prefix']
    pevents = bind_events(pricing['records'], data['mappings'])
    for w in pricing['words']:
        verify_word(w, data)
    prices = 0
    maxbits = 0
    for row in pricing['history']:
        if row['kind']=='SEARCH_RESTART':
            continue
        events = pevents[:row['record_count']]
        if row['kind']=='EXACT_EVENT_LAW':
            weights = [Fraction(w) for w in row['weights']]
            require(len(weights)<=len(pricing['words']) and all(w>=0 for w in weights)
                    and sum(weights)==1, 'prefix probability')
            for event in events:
                require(sum(w*score(word,[event],[1]) for word,w in
                            zip(pricing['words'],weights))==0, 'prefix event law')
        else:
            require(row['kind']=='EXACT_POOL_SEPARATOR' and row['answer']=='SAT', 'prefix verdict')
            potential = row['potential']
            require(len({j for j,a in potential})==len(potential) and all(
                type(j) is int and 0<=j<len(events) and type(a) is int and a!=0
                for j,a in potential), 'potential shape')
            chosen = [events[j] for j,a in potential]
            coeff = [a for j,a in potential]
            values = [score(w,chosen,coeff) for w in pricing['words'][:row['pool_size']]]
            require(values==row['pool_values'] and min(values)>0, 'pool separator')
            require(row['new_word_index']==row['pool_size'], 'column chronology')
            value = score(pricing['words'][row['new_word_index']],chosen,coeff)
            require(value==row['value'] and value<=0, 'pricing counterexample')
            prices += 1
            maxbits = max(maxbits,*(abs(a).bit_length() for a in coeff))
    zero = exp['zero_refinement']
    events = bind_events(zero['records'], data['mappings'])
    require(len(zero['words'])==len(zero['history'])+1, 'zero chronology')
    for word in zero['words']:
        verify_word(word, data)
    initial_count = len(zero['records'])-sum(len(row['added']) for row in zero['history'])
    require(all(score(zero['words'][0],[ev],[1])==0 for ev in events[:initial_count]), 'initial zero word')
    count = initial_count
    for i,row in enumerate(zero['history']):
        old = zero['words'][i]
        added = row['added']
        require(zero['records'][count:count+len(added)]==added, 'event chronology')
        new_events = bind_events(added, data['mappings'])
        require(all(score(old,[ev],[1])!=0 for ev in new_events), 'nonviolated refinement')
        count += len(added)
        require(row['records']==count and row['word_index']==i+1 and row['status']=='SAT', 'refinement verdict')
        require(all(score(zero['words'][i+1],[ev],[1])==0 for ev in events[:count]), 'zero prefix witness')
    passed,_ = full_law_domains([zero['words'][-1]],[Fraction(1)],data['mappings'])
    require(count==len(events) and passed==[14], 'not the recorded proper restricted-event witness')
    return dict(pricing_counterexamples=prices, pricing_words_checked=len(pricing['words']),
                pricing_largest_coefficient_bits=maxbits, zero_refinement_steps=len(zero['history']),
                zero_event_records=len(events), zero_final_full_domains=passed,
                scope='Exact finite exploration prefixes and restricted-event counterexamples only; '
                      'not all-word separation, event independence, or a full 15-domain law.')


def individual_Y_extensions(cert, local, local_raw, data, summary):
    require(cert['schema']=='cyclic-pattern-individual-Y-extensions-v1'
            and cert['base_commit']==BASE
            and cert['input_semantic_sha256']==summary['semantic_sha256']
            and cert['local_certificate_sha256']==hashlib.sha256(local_raw).hexdigest(),
            'individual Y extension binding')
    require(len(cert['words'])==3, 'three individual extensions')
    for word, local_word in zip(cert['words'],local['three_word_extreme_law']['words']):
        verify_word(word,data)
        require(pattern(word,local['vertices_in_Y'])==pattern(local_word,range(29)),
                'wrong local pattern in Y extension')
    return dict(status='PASS',separate_full_Y_extensions=3,
                proper_edge_checks=3*len(data['edges']),
                scope='Separate proper extensions only; no common motion law.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    start = time.monotonic()
    root = Path(__file__).resolve().parents[1]
    data, summary = reconstruct(root)
    cert_path = root/'certificates/two_atom_motion_packet.json.gz'
    cert = read(cert_path)
    rebuilt = rebuild_singleton(len(data['points']), data['edges'], 5,
                                [data['mappings'][j] for j in CORE])
    result = check(cert, data, summary, rebuilt)
    from verify_localized_motion_packet import check as local_check
    local_cert = read(root/'certificates/localized_motion_packet.json')
    localized = local_check(local_cert, data, summary)
    from verify_localized_hintfree import replay as replay_without_hints
    hint_free = replay_without_hints(local_cert)
    from verify_cyclic_pattern_extension import check as cyclic_check
    local_raw = (root/'certificates/localized_motion_packet.json').read_bytes()
    cyclic_cert = read(root/'certificates/cyclic_pattern_extension.json')
    cyclic_result = cyclic_check(cyclic_cert,local_cert,local_raw,data)
    extensions_cert = read(root/'certificates/cyclic_pattern_Y_extensions.json')
    extensions = individual_Y_extensions(extensions_cert,local_cert,local_raw,data,summary)
    extension_rejections = []
    for name in ['individual-wrong-word','individual-wrong-restriction','individual-binding']:
        changed = deepcopy(extensions_cert)
        if name=='individual-wrong-word':
            changed['words'][0] = '0'*len(data['points'])
        elif name=='individual-wrong-restriction':
            changed['words'][0] = changed['words'][1]
        else:
            changed['local_certificate_sha256'] = '0'*64
        try:
            individual_Y_extensions(changed,local_cert,local_raw,data,summary)
        except (ValueError, AssertionError, KeyError, IndexError):
            extension_rejections.append(name)
        else:
            raise AssertionError('accepted '+name)
    # Direct small-geometry reconstruction and proofs are cheap enough to
    # reject real certificate mutations, not merely tiny surrogate clauses.
    local_mutations = {
        'local-coordinate': lambda c:c['points'][0].__setitem__(0,c['points'][0][0]+1),
        'local-denominator': lambda c:c.__setitem__('coordinate_denominator',481),
        'local-missing-edge': lambda c:c['edges'].pop(),
        'local-missing-mapping': lambda c:c['mappings'][14].pop(),
        'local-nonunit-normalization': lambda c:c['one_word_denial'].__setitem__('normalization_edge',[0,0]),
        'local-wrong-cnf': lambda c:c['one_word_denial'].__setitem__('cnf_sha256','0'*64),
        'local-proof-no-empty': lambda c:c['one_word_denial']['proof'].pop(),
        'local-unbalanced-pair': lambda c:c['two_word_law'].__setitem__('weights',['1/3','2/3']),
        'local-broadened-positive': lambda c:c['two_word_law'].__setitem__('motions',CORE),
        'local-duplicate-partition': lambda c:c['two_word_law']['words'].__setitem__(1,c['two_word_law']['words'][0]),
        'local-missing-vertex-witness': lambda c:c['omit_one_vertex'].pop(),
        'local-bad-vertex-witness': lambda c:c['omit_one_vertex'][0].__setitem__('word','0'*28),
        'local-bad-motion-witness': lambda c:c['omit_one_motion'][0].__setitem__('word','0'*29),
        'local-bad-ordinary-coloring': lambda c:c['ordinary_coloring'].__setitem__('word','0'*29),
        'local-even-cycle': lambda c:c['ordinary_coloring'].__setitem__('odd_cycle',[0,1,2,3]),
        'local-bad-six-colors': lambda c:c['singleton_six_coloring'].__setitem__('word','0'*29),
        'local-three-word': lambda c:c['three_word_extreme_law']['words'].__setitem__(0,'0'*29),
        'local-three-weights': lambda c:c['three_word_extreme_law'].__setitem__('weights',['1/2','1/4','1/4']),
        'local-extremality-rank': lambda c:c['three_word_extreme_law'].__setitem__('augmented_determinant',0),
        'local-geometric-order-assumption': lambda c:c['three_word_extreme_law'].__setitem__('eta_unique_support_matching',[0,1,2]),
        'local-wrong-Y-embedding': lambda c:c['vertices_in_Y'].__setitem__(0,33),
    }
    local_rejections = []
    for name, mutate in local_mutations.items():
        changed = deepcopy(local_cert)
        mutate(changed)
        try:
            local_check(changed,data,summary)
        except (ValueError, AssertionError, KeyError, IndexError):
            local_rejections.append(name)
        else:
            raise AssertionError('accepted mutation '+name)
    cyclic_rejections = []
    for name,field,value in [
        ('cyclic-binding','local_certificate_sha256','0'*64),
        ('cyclic-order','rotation_order',3),
        ('cyclic-sharp-mass','bound','1'),
        ('cyclic-improper-word','proper_five_coloring','0'*86),
        ('cyclic-missing-edge','edges',cyclic_cert['edges'][:-1]),
        ('cyclic-missing-copy','copies',cyclic_cert['copies'][:-1]),
    ]:
        changed = deepcopy(cyclic_cert)
        changed[field] = value
        try:
            cyclic_check(changed,local_cert,local_raw,data)
        except (ValueError, AssertionError, KeyError, IndexError):
            cyclic_rejections.append(name)
        else:
            raise AssertionError('accepted '+name)
    mutations = {
        'base-sha': lambda c:c.__setitem__('base_commit','0'*40),
        'geometry-binding': lambda c:c.__setitem__('input_semantic_sha256','0'*64),
        'wrong-motion-set': lambda c:c['motions'].__setitem__(0,0),
        'improper-first-word': lambda c:c['two_word_law']['words'].__setitem__(0,'0'*10077),
        'duplicate-partition': lambda c:c['two_word_law']['words'].__setitem__(1,c['two_word_law']['words'][0]),
        'unbalanced-weights': lambda c:c['two_word_law'].__setitem__('weights',['1/3','2/3']),
        'missing-deletion-word': lambda c:c['omit_one_motion'].pop(),
        'wrong-deletion-scope': lambda c:c['omit_one_motion'][0].__setitem__('omitted',0),
        'improper-deletion-word': lambda c:c['omit_one_motion'][0].__setitem__('word','0'*10077),
        'no-proof': lambda c:c['one_word_denial'].__setitem__('proof',[]),
        'broadened-denial': lambda c:c['one_word_denial'].__setitem__('status','NO_JOINT_LAW'),
    }
    rejected = []
    for name, mutate in mutations.items():
        changed = deepcopy(cert)
        mutate(changed)
        try:
            fast_checks(changed,data,summary)
        except (ValueError, AssertionError, KeyError, IndexError):
            rejected.append(name)
        else:
            raise AssertionError('accepted mutation '+name)
    for name, field in [('wrong-cnf-hash','cnf_sha256'),('wrong-subformula-hash','selected_cnf_sha256'),('wrong-nv','nv')]:
        changed = deepcopy(cert)
        changed['one_word_denial'][field] = '0'*64 if field.endswith('sha256') else 1
        try:
            check(changed,data,summary,rebuilt)
        except (ValueError, AssertionError):
            rejected.append(name)
        else:
            raise AssertionError('accepted mutation '+name)
    for name, ids in [('out-of-range-initial-clause',[0]),
                      ('duplicate-initial-clause',[1,1]),('boolean-initial-clause',[True])]:
        changed = deepcopy(cert)
        changed['one_word_denial']['initial_clause_ids'] = ids
        try:
            check(changed,data,summary,rebuilt)
        except (ValueError, AssertionError):
            rejected.append(name)
        else:
            raise AssertionError('accepted mutation '+name)
    # Proof-level mutations use the identical independent backend on a tiny
    # calibration, avoiding repeatedly replaying thousands of big-graph lines.
    from verify_rup_lrat import check as rup
    for name, lines in [('missing-empty',['3 1 0 1 2 0']),
                        ('negative-hint',['3 0 -1 0']),('forward-hint',['3 0 999 0'])]:
        try:
            rup([[1],[-1]], lines)
        except (ValueError, AssertionError):
            rejected.append(name)
        else:
            raise AssertionError('accepted '+name)
    for name in ['verify_motion_packet.py','test_motion_packet.py','search_motion_packet.py',
                 'verify_localized_motion_packet.py','build_localized_motion_packet.py',
                 'verify_localized_hintfree.py','verify_cyclic_pattern_extension.py',
                 'build_cyclic_pattern_extension.py']:
        proc = subprocess.run([sys.executable,'-O',str(root/'research'/name)],capture_output=True,text=True,timeout=20)
        require(proc.returncode!=0 and 'requires assertions' in proc.stderr, 'optimized-mode guard')
        rejected.append(name+':optimized-mode')
    exploration = exploration_checks(read(root/'certificates/motion_packet_exploration.json.gz'),data,summary)
    print(json.dumps(dict(status='PASS',packet=result,localized_packet=localized,
        localized_mutation_rejections=local_rejections,hint_free_proof=hint_free,
        cyclic_extension=cyclic_result,cyclic_mutation_rejections=cyclic_rejections,
        individual_Y_extensions=extensions,individual_extension_rejections=extension_rejections,
        exploration=exploration,
        cnf_calibration=calibration(),mutation_rejections=rejected,
        certificate_sha256=hashlib.sha256(cert_path.read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-start,
        scope='Fresh complete geometry/domain reconstruction and new certificates. '
              'Not an assertion that the original HN problem or all 15-domain laws are solved.'),indent=2))


if __name__=='__main__':
    main()
