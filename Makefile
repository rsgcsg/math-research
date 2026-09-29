.PHONY: check-heptagon-module check-python check-joined-pricing check-full15-support check-eta-support check check-salem check-quartet check-orbit check-covers check-frames check-preparation check-pricing check-rotations check-rank2 check-next check-cyclic-translates setup explore
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
