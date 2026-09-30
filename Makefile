.PHONY: check-heptagon-module check-python check-joined-pricing check-full15-support check-eta-support check check-salem check-quartet check-orbit check-covers check-frames check-preparation check-pricing check-rotations check-rank2 check-next check-cyclic-translates setup explore check-lattice-ports check-qd-family check-t028-host-orbit check-g14-port-or check-y-full-geometry check-port4-exact-law
.DEFAULT_GOAL := check

check-python:
	python3 -c 'import sys; sys.exit("Python >=3.10 required; activate .venv before make check" if sys.version_info < (3, 10) else 0)'

check: check-python
	python3 research/verify.py
	$(MAKE) check-salem
	$(MAKE) check-quartet
	$(MAKE) check-orbit
	$(MAKE) check-covers
	$(MAKE) check-frames
	$(MAKE) check-preparation
	$(MAKE) check-pricing
	$(MAKE) check-rotations
	$(MAKE) check-rank2
	$(MAKE) check-next
	$(MAKE) check-cyclic-translates
	$(MAKE) check-eta-support
	$(MAKE) check-full15-support
	$(MAKE) check-heptagon-module
	$(MAKE) check-lattice-ports
	$(MAKE) check-qd-family
	$(MAKE) check-t028-host-orbit
	$(MAKE) check-g14-port-or
	$(MAKE) check-port4-exact-law

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

check-full15-support:
	python3 -S research/test_palette_difference.py
	python3 -S research/test_connected_partition_marginals.py
	python3 -S research/test_weighted_transport.py
	python3 -S research/verify_three_atom_mass.py
	python3 -S research/test_full15_support.py
	$(MAKE) check-joined-pricing

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

.PHONY: check-joint-theory
check: check-joint-theory

check-joint-theory: check-y-full-geometry
	python3 -S research/verify_scc_calibration.py
	python3 -S research/verify_free_group_star_calibration.py
	python3 -S research/verify_four_port_scc.py

.PHONY: check-g14-pair-orbit
check: check-g14-pair-orbit

check-g14-pair-orbit: check-y-full-geometry
	python3 -S research/verify_g14_pair_orbit_law.py
	python3 -S research/test_g14_pair_orbit_forest.py

.PHONY: check-g14-common-law check-cubic-unit-directions
check: check-g14-common-law check-cubic-unit-directions

check-g14-common-law: check-y-full-geometry
	python3 -S research/verify_g14_pair_port4_common_law.py

check-cubic-unit-directions:
	python3 -S research/verify_cubic_unit_directions.py

.PHONY: check-g14-pr-bound
check: check-g14-pr-bound

check-g14-pr-bound: check-y-full-geometry
	python3 -S research/verify_g14_pr_transport_bound.py

.PHONY: check-pentagon-partition-gap
check: check-pentagon-partition-gap

check-pentagon-partition-gap:
	python3 -S research/verify_pentagon_cp_partition_gap.py
