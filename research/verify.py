"""Small standard-library entry point for independent finite verification."""
import json
from pathlib import Path
from phase_checks import run
from relations import calibrate
from exact_geometry import check_geometry
from balanced_weights import run as check_balanced_weights
import hashlib
from verify_search_models import verify as verify_search_models
from itertools import permutations
from verify_translated_seam import verify as verify_translated_seam
from verify_long_chain import verify as verify_long_chain
from fractional_ceiling import verify as verify_fractional_ceiling
from joint_moment_gap import verify as verify_joint_moment_gap
from verify_joint_face import verify as verify_joint_face
from verify_parts_core import verify as verify_parts_core
from verify_quintic_shifted_spectrum import verify as verify_quintic_shifted_spectrum
from verify_quintic_radial_escape import verify as verify_quintic_radial_escape
from verify_quintic_parametric_contacts import verify as verify_quintic_parametric_contacts
from verify_parts_triples import verify as verify_parts_triples
from verify_parts_parallelograms import verify as verify_parts_parallelograms
from verify_residue11 import verify as verify_residue11
from verify_parts_escape import verify as verify_parts_escape
from valuation_escape import verify as verify_valuation_escape
from verify_pair_orbits import verify as verify_pair_orbits
from verify_anchored_geometry import verify as verify_anchored_geometry
from verify_six_pair_uniform import verify as verify_six_pair_uniform
from verify_spindle_gate import verify as verify_spindle_gate
from verify_repair_cascade import verify as verify_repair_cascade
from verify_repair_pair_fan import verify as verify_repair_pair_fan
from verify_rooted_spindle import verify as verify_rooted_spindle
from verify_coupled_gate import verify as verify_coupled_gate
from verify_root_contact_repair import verify as verify_root_contact_repair
from verify_spindle_joint_support import verify as verify_spindle_joint_support
from verify_pose_field_lock import verify as verify_pose_field_lock
from verify_residue_method_obstruction import verify as verify_residue_method_obstruction
from verify_higher_residue_precision import verify as verify_higher_residue_precision
from verify_multicenter_cores import verify as verify_multicenter_cores
from verify_refined_centers import verify as verify_refined_centers, verify_finite as verify_refined_finite
from verify_background_repair import verify as verify_background_repair
from verify_palette_activation import verify as verify_palette_activation
from verify_free_pose_rank import verify as verify_free_pose_rank
from verify_translated_field_stack import verify as verify_translated_field_stack
from verify_triangular_field_stack import verify as verify_triangular_field_stack
from verify_quadratic_virtual_pivot import verify as verify_quadratic_virtual_pivot
from verify_mixed_shell_stack import verify as verify_mixed_shell_stack
from verify_contact_translation_closure import verify as verify_contact_translation_closure
from verify_resonant_translation_stack import verify as verify_resonant_translation_stack
from verify_resonant_center_projection import verify as verify_resonant_center_projection
from verify_resonant_twist_obstruction import verify as verify_resonant_twist_obstruction
from verify_center_palette_rigidity import verify as verify_center_palette_rigidity
from verify_cyclotomic_integer_stack import verify as verify_cyclotomic_integer_stack
from verify_cyclotomic_127 import verify as verify_cyclotomic_127
from verify_cyclotomic_field import verify as verify_cyclotomic_field
from verify_cyclotomic_sparse_coupling import verify as verify_cyclotomic_sparse_coupling
from verify_cyclotomic_direction_parity import verify as verify_cyclotomic_direction_parity
from verify_quintic_projection import verify as verify_quintic_projection
from verify_cm_density_coloring import verify as verify_cm_density_coloring
from verify_invariant_joint_ceiling import verify as verify_invariant_joint_ceiling
from verify_quintic_core_probe import verify as verify_quintic_core_probe
from verify_dense_five_color_tower import verify as verify_dense_five_color_tower
from verify_quintic_congruence import verify as verify_quintic_congruence
from verify_quintic_anchor_bridge import verify as verify_quintic_anchor_bridge
from verify_quintic_bridge_family import verify as verify_quintic_bridge_family
from verify_quintic_bridge_contacts import verify as verify_quintic_bridge_contacts
from verify_quintic_second_host import verify as verify_quintic_second_host
from verify_quintic_root_spectrum import verify as verify_quintic_root_spectrum
from verify_quintic_independent_center import verify as verify_quintic_independent_center
from verify_quintic_translated_orbit import verify as verify_quintic_translated_orbit
from verify_quintic_joint_ports import verify as verify_quintic_joint_ports
from verify_joint_column_pricing import verify as verify_joint_column_pricing
from verify_quintic_pair_completion import verify as verify_quintic_pair_completion


def main():
    import sys
    if not __debug__:
        sys.exit('Do not disable assertions when verifying mathematical certificates.')
    root = Path(__file__).resolve().parents[1]
    for p in ('README.md', 'AGENTS.md', 'docs/CURRENT.md', 'docs/ROUTES.md',
              'docs/RESULTS.md', 'references/SOURCES.md',
              'docs/proofs/hn_unified_framework.md', 'references/LITERATURE_MAP.md'):
        assert (root / p).is_file(), p
    result = run()
    result['relation_calibration'] = calibrate()
    result['exact_geometry'] = check_geometry()
    result['balanced_weights'] = check_balanced_weights()
    saved = root / 'certificates/phase_checks.json'
    assert saved.is_file(), 'Missing exact finite table'
    # JSON normalizes integer keys and tuples; compare serialized structures.
    assert json.loads(saved.read_text()) == json.loads(json.dumps(result))
    provenance = root / 'references/history/SHA256.json'
    if provenance.exists():
        for name, expected in json.loads(provenance.read_text()).items():
            assert hashlib.sha256((provenance.parent / name).read_bytes()).hexdigest() == expected
    models = root / 'certificates/search_models.json'
    assert models.is_file(), 'Missing saved search witnesses'
    print(json.dumps(verify_search_models(json.loads(models.read_text())), indent=2))
    for radius in (3, 4):
        seam = json.loads((root / f'certificates/seam_radius{radius}.json').read_text())
        points = [tuple(p) for p in seam['points']]
        expected = sorted((x,y) for x in range(-radius,radius+1) for y in range(-radius,radius+1)
                          if max(abs(x),abs(y),abs(x+y)) <= radius)
        assert points == expected
        # Independently use the all-contact theorem, rather than the search's field-distance routine.
        edges = []
        for i, (x,y) in enumerate(points):
            for j, (u,v) in enumerate(points):
                if ((x,y)==(u,v) and x*x+x*y+y*y==3) or (
                    (x,y)==(0,0) and u*u+u*v+v*v==1) or (
                    (u,v)==(0,0) and x*x+x*y+y*y==1):
                    edges.append([i,j])
        assert seam['cross_edges'] == edges
        lo = min(x//2 for x,y in points if x % 2)
        colorings = []
        for word in seam['words']:
            s = {lo:0}
            for i, step in enumerate(word):
                assert step in (0,-1)
                s[lo+i+1] = (s[lo+i]+step) % 3
            colorings.append([y%3 if x%2==0 else 3+(y+s[x//2])%3 for x,y in points])
        assert len(colorings)==len(set(tuple(c) for c in colorings))==8
        for i,a in enumerate(colorings):
            for j,b in enumerate(colorings):
                count = sum(all(a[u] != ((0,)+p)[b[v]] for u,v in edges)
                            for p in permutations(range(1,6)))
                assert count == seam['allowed_relative_permutation_counts'][i][j] == 53
    print('PASS: exact Moser-angle seam relations, 128 word pairs, 120 relative frames each')
    print(json.dumps(verify_translated_seam(root / 'certificates/translated_seam.json'), indent=2))
    print(json.dumps(verify_long_chain(root / 'certificates/long_chain_invariant.json'), indent=2))
    print(json.dumps(verify_fractional_ceiling(), indent=2))
    print(json.dumps(verify_joint_moment_gap(), indent=2))
    print(json.dumps(verify_joint_face(root / 'certificates/joint_face_exact.json'), indent=2))
    print(json.dumps(verify_joint_face(root / 'certificates/joint_face_exact.json',interior=True), indent=2))
    print(json.dumps(verify_parts_core(root), indent=2))
    print(json.dumps(verify_parts_triples(root), indent=2))
    print(json.dumps(verify_parts_parallelograms(root), indent=2))
    print(json.dumps(verify_residue11(root), indent=2))
    print(json.dumps(verify_parts_escape(root), indent=2))
    print(json.dumps(verify_valuation_escape(), indent=2))
    print(json.dumps(verify_pair_orbits(root), indent=2))
    print(json.dumps(verify_anchored_geometry(), indent=2))
    print(json.dumps(verify_six_pair_uniform(root), indent=2))
    print(json.dumps(verify_spindle_gate(root), indent=2))
    print(json.dumps(verify_repair_cascade(root), indent=2))
    print(json.dumps(verify_repair_pair_fan(root), indent=2))
    print(json.dumps(verify_rooted_spindle(root), indent=2))
    print(json.dumps(verify_coupled_gate(root), indent=2))
    print(json.dumps(verify_root_contact_repair(root), indent=2))
    print(json.dumps(verify_spindle_joint_support(root), indent=2))
    print(json.dumps(verify_pose_field_lock(root), indent=2))
    print(json.dumps(verify_residue_method_obstruction(root), indent=2))
    print(json.dumps(verify_higher_residue_precision(root), indent=2))
    print(json.dumps(verify_multicenter_cores(root), indent=2))
    print(json.dumps(verify_refined_centers(root), indent=2))
    print(json.dumps(verify_refined_finite(root), indent=2))
    print(json.dumps(verify_background_repair(root), indent=2))
    print(json.dumps(verify_palette_activation(root), indent=2))
    print(json.dumps(verify_free_pose_rank(root), indent=2))
    print(json.dumps(verify_translated_field_stack(root), indent=2))
    print(json.dumps(verify_triangular_field_stack(root), indent=2))
    print(json.dumps(verify_quadratic_virtual_pivot(), indent=2))
    print(json.dumps(verify_mixed_shell_stack(root), indent=2))
    print(json.dumps(verify_contact_translation_closure(root), indent=2))
    print(json.dumps(verify_resonant_translation_stack(root), indent=2))
    print(json.dumps(verify_resonant_center_projection(root), indent=2))
    print(json.dumps(verify_resonant_twist_obstruction(root), indent=2))
    print(json.dumps(verify_center_palette_rigidity(), indent=2))
    print(json.dumps(verify_cyclotomic_integer_stack(root), indent=2))
    print(json.dumps(verify_cyclotomic_127(root), indent=2))
    print(json.dumps(verify_cyclotomic_field(root), indent=2))
    print(json.dumps(verify_cyclotomic_sparse_coupling(root), indent=2))
    print(json.dumps(verify_cyclotomic_direction_parity(root), indent=2))
    print(json.dumps(verify_quintic_projection(root), indent=2))
    verify_cm_density_coloring()
    print(json.dumps(verify_invariant_joint_ceiling(root), indent=2))
    print(json.dumps(verify_quintic_core_probe(root), indent=2))
    print(json.dumps(verify_quintic_core_probe(root, root/'certificates/quintic_mixed_angle_probe.json'), indent=2))
    print(json.dumps(verify_dense_five_color_tower(root), indent=2))
    print(json.dumps(verify_quintic_congruence(root), indent=2))
    print(json.dumps(verify_quintic_anchor_bridge(root), indent=2))
    print(json.dumps(verify_quintic_bridge_family(root), indent=2))
    print(json.dumps(verify_quintic_bridge_contacts(root), indent=2))
    print(json.dumps(verify_quintic_second_host(root), indent=2))
    print(json.dumps(verify_quintic_second_host(root,root/'certificates/quintic_nontorsion_host.json'), indent=2))
    print(json.dumps(verify_quintic_root_spectrum(root), indent=2))
    print(json.dumps(verify_quintic_shifted_spectrum(root), indent=2))
    print(json.dumps(verify_quintic_radial_escape(root), indent=2))
    print(json.dumps(verify_quintic_parametric_contacts(root), indent=2))
    print(json.dumps(verify_quintic_independent_center(root), indent=2))
    print(json.dumps(verify_quintic_translated_orbit(root), indent=2))
    print(json.dumps(verify_quintic_joint_ports(root), indent=2))
    print(json.dumps(verify_quintic_joint_ports(root, root/'certificates/quintic_joint_translations.json'), indent=2))
    print(json.dumps(verify_joint_column_pricing(root), indent=2))
    print(json.dumps(verify_quintic_pair_completion(root), indent=2))
    print(json.dumps(dict(status='PASS', checks=list(result),
                          row_transitions=result['row_transitions'],
                          symmetry=result['symmetry']), indent=2))


if __name__ == '__main__':
    main()
