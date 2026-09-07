.PHONY: check setup explore

check:
	python3 research/verify.py

setup:
	uv venv --allow-existing .venv
	uv pip install --python .venv/bin/python -r requirements-research.txt

explore:
	.venv/bin/python research/search_phases.py --width 6 --height 6 --opposite-only

