.PHONY: check check-salem check-quartet check-orbit check-covers check-frames check-preparation setup explore

check:
	python3 research/verify.py
	$(MAKE) check-salem
	$(MAKE) check-quartet
	$(MAKE) check-orbit
	$(MAKE) check-covers
	$(MAKE) check-frames
	$(MAKE) check-preparation

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

