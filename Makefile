.DEFAULT_GOAL := check
.PHONY: check-python check check-salem check-quartet check-orbit check-covers check-frames check-preparation setup explore check-pricing check-rotations check-rank2 check-next check-cyclic-translates check-eta-support check-full15-support check-joined-pricing check-heptagon-module check-lattice-ports check-qd-family check-t028-host-orbit check-y-full-geometry check-g14-port-or check-port4-exact-law check-joint-theory check-g14-pair-orbit check-g14-common-law check-cubic-unit-directions check-g14-pr-bound check-pentagon-partition-gap check-pr-local-projection check-cyclic-interval-kernel check-bw-pr-odd-cycle-ceiling check-hidden-pair-elimination check-q-pr-coupling-audit check-transport-projection check-q-defect-lifting check-q-joint-boundary-gap check-q-chorded-w22-audit check-generalized-partition-facets check-q-robust-capacity check-q-defect-lift check-q-defect-scope-audit check-packet check-cycle-descent check-unit-translate check-translate-kernel check-legacy-full15-support

check-python:
	python3 -c 'import sys; sys.exit("Python >=3.10 required; activate .venv before make check" if sys.version_info < (3, 10) else 0)'

check: check-binary-povm check-integration check-two-partition-w22-audit check-q-chorded-w22-audit check-python check-joint-theory check-g14-pair-orbit check-g14-common-law check-cubic-unit-directions check-g14-pr-bound check-pentagon-partition-gap check-pr-local-projection check-cyclic-interval-kernel check-bw-pr-odd-cycle-ceiling check-hidden-pair-elimination check-q-pr-coupling-audit check-transport-projection check-q-defect-lifting check-q-joint-boundary-gap check-generalized-partition-facets check-q-robust-capacity check-q-defect-lift check-q-defect-scope-audit check-salem check-quartet check-orbit check-covers check-frames check-preparation check-pricing check-rotations check-rank2 check-next check-cyclic-translates check-eta-support check-full15-support check-heptagon-module check-lattice-ports check-qd-family check-t028-host-orbit check-g14-port-or check-port4-exact-law check-packet check-cycle-descent check-unit-translate check-translate-kernel check-legacy-full15-support
	python3 research/verify.py

check-salem:
	python3 research/test_salem_sextic_certificates.py

check-quartet:
	python3 research/test_partition_quartet_completeness.py

check-orbit:
	python3 research/test_cyclic_valuation_sieve.py
	python3 research/verify_dyadic_cyclic_orbit.py

check-covers:
	python3 research/test_joint_cover_certificates.py

check-frames:
	python3 research/test_finite_frame_certificates.py

check-preparation:
	python3 research/audit_full_law_preparation.py --self-test

setup:
	uv venv --allow-existing .venv
	uv pip install --python .venv/bin/python -r requirements-research.txt

explore:
	.venv/bin/python research/search_phases.py --width 6 --height 6 --opposite-only

check-pricing:
	python3 research/test_full_law_pricing.py

check-rotations:
	python3 research/verify_dyadic_commuting_patch.py --mutations
	python3 research/verify_rational_rotation_orbit.py --mutations
	python3 research/verify_rotation_orbit_colorings.py --mutation-tests

check-rank2:
	python3 research/test_rank2_rotation.py

check-next:
	python3 -S research/test_research_checkpoint.py

check-cyclic-translates:
	python3 -S research/test_cyclic_translate_contacts.py
	python3 -S research/verify_cyclic_translate_research.py

check-eta-support:
	python3 -S research/test_eta_joined_support.py

check-full15-support: check-joined-pricing
	python3 -S research/test_palette_difference.py
	python3 -S research/test_connected_partition_marginals.py
	python3 -S research/test_weighted_transport.py
	python3 -S research/verify_three_atom_mass.py
	python3 -S research/test_full15_support.py

check-joined-pricing:
	python3 -S research/verify_joined_seed_pricing.py
	python3 -S research/test_joined_seed_pricing.py
	python3 -S research/verify_joined_negative_probe.py

check-heptagon-module:
	python3 -S research/test_heptagon_module.py
	python3 -S research/verify_heptagon_residue27.py
	python3 -S research/verify_heptagon_actual_patch.py

check-lattice-ports:
	python3 -S research/test_lattice_mixed.py
	python3 -S research/verify_Y_pair_portfolio.py --self-test
	python3 -S research/verify_cube_symmetry_gap.py

check-qd-family:
	python3 -S research/check_qd_family.py --check-certificate certificates/qd_family_certificate.json

check-t028-host-orbit:
	python3 -S research/verify_t028_host_orbit_ceiling.py

check-y-full-geometry:
	python3 -S research/audit_full_law_preparation.py --cache certificates/Y_full_geometry.json.gz

check-g14-port-or: check-y-full-geometry
	python3 -S research/verify_g14_port_or.py --check-certificate certificates/g14_port_or_certificate.json
	python3 -S research/verify_g14_unique_event_y.py

check-port4-exact-law: check-y-full-geometry
	python3 -S research/verify_port4_exact_law.py --check-certificate certificates/port4_exact_law_verification.json

check-joint-theory: check-y-full-geometry
	python3 -S research/verify_scc_calibration.py
	python3 -S research/verify_free_group_star_calibration.py
	python3 -S research/verify_four_port_scc.py

check-g14-pair-orbit: check-y-full-geometry
	python3 -S research/verify_g14_pair_orbit_law.py
	python3 -S research/test_g14_pair_orbit_forest.py

check-g14-common-law: check-y-full-geometry
	python3 -S research/verify_g14_pair_port4_common_law.py

check-cubic-unit-directions:
	python3 -S research/verify_cubic_unit_directions.py

check-g14-pr-bound: check-y-full-geometry
	python3 -S research/verify_g14_pr_transport_bound.py

check-pentagon-partition-gap:
	python3 -S research/verify_pentagon_cp_partition_gap.py

check-pr-local-projection: check-g14-pr-bound
	python3 -S research/verify_nine_point_pr_polygon.py
	python3 -S research/test_nine_point_pr_polygon.py
	python3 -S research/verify_pr_matching_window_ceiling.py

check-cyclic-interval-kernel:
	python3 -S research/verify_cyclic_interval_kernel.py

check-bw-pr-odd-cycle-ceiling: check-pr-local-projection
	python3 -S research/verify_star_odd_cycle_lemma.py
	python3 -S research/verify_bw_pr_odd_cycle_ceiling.py

check-hidden-pair-elimination: check-bw-pr-odd-cycle-ceiling
	python3 -S research/verify_hidden_pair_elimination.py

check-q-pr-coupling-audit: check-pr-local-projection check-g14-pair-orbit
	python3 -S research/verify_q_pr_coupling_audit.py

check-transport-projection: check-y-full-geometry
	python3 -S research/check_transport_projection.py --self-test

check-q-defect-lifting: check-y-full-geometry
	python3 -S research/verify_q_defect_lifting.py --self-test

check-q-joint-boundary-gap: check-y-full-geometry
	python3 -S research/verify_q_joint_boundary_gap.py --self-test

check-q-chorded-w22-audit:
	python3 -S research/verify_q_chorded_w22_audit.py

check-generalized-partition-facets: check-g14-pr-bound
	python3 -S research/verify_generalized_partition_facets.py

check-q-robust-capacity: check-transport-projection
	python3 -S research/verify_q_robust_capacity.py --self-test

check-q-defect-lift: check-transport-projection check-g14-pr-bound
	python3 -S research/check_q_defect_lift.py --self-test

check-q-defect-scope-audit: check-y-full-geometry
	python3 -S research/check_q_defect_scope_audit.py --self-test

check-packet:
	python3 -S research/test_motion_packet.py

check-cycle-descent:
	python3 -S research/test_cycle_descent.py

check-unit-translate:
	python3 -S research/verify_unit_translate.py

check-translate-kernel:
	python3 -S research/verify_integer_translate_kernel.py

check-legacy-full15-support:
	python3 -S research/legacy_test_full15_support.py

.PHONY: check-two-partition-w22-audit
check-two-partition-w22-audit: check-q-joint-boundary-gap
	python3 -S research/verify_two_partition_w22_audit.py

.PHONY: check-integration
check-integration:
	python3 -S research/check_integration.py

.PHONY: check-radical-transfer
check-radical-transfer:
	python3 -S research/verify_radical_transfer_calibration.py --self-test
	python3 -S research/verify_radical_template_mechanism.py

check: check-radical-transfer

.PHONY: check-compact-mixing
check-compact-mixing:
	python3 -S research/verify_compact_mixing_transfer.py
	python3 -S research/verify_qubit_rounding.py

check: check-compact-mixing

.PHONY: check-binary-povm
check-binary-povm:
	python3 -S research/verify_binary_povm_threshold.py --self-test
