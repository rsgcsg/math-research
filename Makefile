.PHONY: check check-salem check-quartet setup explore

check:
	python3 research/verify.py
	$(MAKE) check-salem
	$(MAKE) check-quartet

check-salem:
	python3 research/test_salem_sextic_certificates.py

check-quartet:
	python3 research/test_partition_quartet_completeness.py

setup:
	uv venv --allow-existing .venv
	uv pip install --python .venv/bin/python -r requirements-research.txt

explore:
	.venv/bin/python research/search_phases.py --width 6 --height 6 --opposite-only

