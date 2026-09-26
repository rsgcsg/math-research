.PHONY: check check-salem check-quartet check-orbit check-covers check-frames check-preparation check-pricing check-rotations check-rank2 setup explore

check:
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
