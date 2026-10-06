"""Independent geometry reconstruction, exact marginal certificate and mutations."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from audit_full_law_preparation import reconstruct
from verify_motion_packet import read
from verify_cycle_descent import check, canonical


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    local_path=root/'certificates/localized_motion_packet.json'
    event_path=root/'certificates/shared_event_research.json.gz'
    local,prior=read(local_path),read(event_path)
    lr,er=local_path.read_bytes(),event_path.read_bytes()
    cert=read(root/'certificates/original_Y_cycle_descent.json')
    def replay(c):return check(c,data,summary,local,lr,prior,er)
    report=replay(cert)
    changes={
        'schema':lambda c:c.__setitem__('schema','new'),
        'source-hash':lambda c:c.__setitem__('input_semantic_sha256','0'*64),
        'parent-commit':lambda c:c.__setitem__('parent_checkpoint','0'*40),
        'extra-conclusion':lambda c:c.__setitem__('HN_solved',True),
        'inherited-hash':lambda c:c.__setitem__('local_certificate_sha256','0'*64),
        'wrong-root':lambda c:c['core']['Y_indices'].__setitem__(0,0),
        'float-position':lambda c:c['core']['local_positions'].__setitem__(0,1.0),
        'wrong-pattern':lambda c:c['core']['patterns'][0].__setitem__(4,0),
        'wrong-order':lambda c:c['core'].__setitem__('rotation_order',3),
        'missing-layer':lambda c:c['core']['copies_in_Y'].pop(),
        'wrong-layer-point':lambda c:c['core']['copies_in_Y'][2].__setitem__(0,0),
        'missing-core-edge':lambda c:c['core']['orbit_edges'].pop(),
        'improper-core-word':lambda c:c['core'].__setitem__('sharp_core_word','0'*11),
        'strict-gap-confusion':lambda c:c['core'].__setitem__('probability_upper_bound','0'),
        'wrong-telescoping':lambda c:c['core']['telescoping_coefficients'].__setitem__(0,5),
        'wrong-facet':lambda c:c['core']['marginal_polytope']['facet_rows'][3].__setitem__(3,1),
        'missing-polytope-vertex':lambda c:c['core']['marginal_polytope']['vertex_witnesses'].pop(),
        'wrong-vertex-count':lambda c:c['core']['marginal_polytope']['vertex_witnesses'][0]['counts'].__setitem__(0,1),
        'improper-vertex-word':lambda c:c['core']['marginal_polytope']['vertex_witnesses'][0].__setitem__('word','0'*11),
        'wrong-color-threshold':lambda c:c['core']['marginal_polytope'].__setitem__('minimum_colors',2),
        'missing-tuple':lambda c:c['transport']['tuples_in_Y'].pop(),
        'bad-path':lambda c:c['transport']['rooted_paths'].__setitem__(0,[0,1]),
        'wrong-generator':lambda c:c['transport']['transitions'][0].__setitem__(1,15),
        'missing-kernel-edge':lambda c:c['transport']['kernel_edges'].pop(),
        'improper-kernel-word':lambda c:c['transport'].__setitem__('sharp_kernel_word','0'*129),
        'overstated-count':lambda c:c['transport'].__setitem__('maximum_hits',99),
        'missing-cycle':lambda c:c['transport']['eta_cycles'].pop(),
        'duplicate-cycle':lambda c:c['transport']['eta_cycles'].__setitem__(1,c['transport']['eta_cycles'][0]),
        'bad-leftover':lambda c:c['transport']['leftover_tuples'].__setitem__(0,c['transport']['eta_cycles'][0][0]),
        'false-uniform-bound':lambda c:c['transport'].__setitem__('uniform_count_mass_bound','3/4'),
        'improper-three-coloring':lambda c:c['transport'].__setitem__('ordinary_three_word','0'*129),
        'invalid-triangle':lambda c:c['transport'].__setitem__('triangle',[0,0,0]),
        'wrong-local-weights':lambda c:c['transport']['known_local_law_weights'].__setitem__(0,'2/5'),
        'wrong-E111-hash':lambda c:c['joined_zero'].__setitem__('prior_event_certificate_sha256','0'*64),
        'improper-Y-word':lambda c:c['joined_zero'].__setitem__('word','0'*10077),
        'wrong-common-partition':lambda c:c['joined_zero'].__setitem__('common_complete_partition',[0]*5),
        'weakened-tuple-claim':lambda c:c['joined_zero'].__setitem__('complete_tuple_partitions_equal',False),
        'wrong-joint-union':lambda c:c['joined_zero']['joint_observation_gap']['source'].__setitem__(0,0),
        'wrong-cross-pair':lambda c:c['joined_zero']['joint_observation_gap'].__setitem__('cross_pair_target',[0,1]),
        'wrong-joint-gap-pattern':lambda c:c['joined_zero']['joint_observation_gap'].__setitem__('target_partition',[0]*7),
        'wrong-event-count':lambda c:c['joined_zero'].__setitem__('pair_event_count',417),
    }
    rejected=[]
    for name,mutate in changes.items():
        damaged=deepcopy(cert);mutate(damaged)
        try:replay(damaged)
        except (ValueError,KeyError,IndexError,TypeError):rejected.append(name)
        else:raise AssertionError('accepted mutation: '+name)
    with tempfile.TemporaryDirectory() as td:
        duplicate=Path(td)/'duplicate.json';duplicate.write_text('{"same":1,"same":2}')
        try:read(duplicate)
        except ValueError:rejected.append('duplicate-json-key')
        else:raise AssertionError('duplicate key accepted')
    for filename in ['verify_cycle_descent.py','test_cycle_descent.py','verify_joined_kernel.py']:
        p=subprocess.run([sys.executable,'-S','-O',str(root/'research'/filename)],capture_output=True,text=True,timeout=20)
        if p.returncode==0 or 'requires assertions' not in p.stderr:
            raise AssertionError('optimized mode not rejected: '+filename)
        rejected.append('optimized-'+filename)
    # Rebuild only derived structure from the persisted positive word. This is
    # not a second independent checker and is not deterministic SAT replay.
    from build_cycle_descent import build
    rebuilt=build(data,local,lr,cert['joined_zero']['word'],er)
    if canonical(rebuilt)!=canonical(cert):raise AssertionError('derived certificate structure differs')
    from verify_joined_kernel import check as check_joined
    joined_report=check_joined(read(root/'certificates/joined_kernel_singleton.json.gz'),data,summary,cert,prior['event_records'],er,True)
    from verify_joined_kernel import check_law
    law=read(root/'certificates/joined_kernel_five_law.json')
    law_report=check_law(law,data,summary,cert,prior['event_records'])
    for name,mutate in {
        'law-improper-word':lambda c:c['words'].__setitem__(0,'0'*10077),
        'law-wrong-weight':lambda c:c['weights'].__setitem__(0,'2/5'),
        'law-duplicate-atom':lambda c:c['words'].__setitem__(0,c['words'][1]),
        'law-wrong-support-cycle':lambda c:c.__setitem__('eta_support_cycle',[0,1,2,3,4]),
        'law-wrong-balance-row':lambda c:c['eta_balance_rows'][0]['coefficients'].__setitem__(0,7),
        'law-wrong-global-status':lambda c:c.__setitem__('full_Y_passed_domains',list(range(15))),
        'law-wrong-scope':lambda c:c.__setitem__('scope','The original15 problem is solved'),
    }.items():
        bad=deepcopy(law);mutate(bad)
        try:check_law(bad,data,summary,cert,prior['event_records'])
        except (ValueError,AssertionError,KeyError,IndexError):rejected.append(name)
        else:raise AssertionError('invalid positive law accepted: '+name)
    report.update(joined_kernel_singleton=joined_report,joined_kernel_five_atom_law=law_report,rejected_mutations=rejected,derived_structure_rebuilt=True,
                  scope=report['scope']+' Full Y independently reconstructed; persisted witnesses replayed, not regenerated by SAT.')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
