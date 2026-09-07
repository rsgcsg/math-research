"""Regenerate exact finite tables; no external solver is used by this command."""
import json
from pathlib import Path
from phase_checks import run
from relations import calibrate
from exact_geometry import check_geometry
from balanced_weights import run as check_balanced_weights

root = Path(__file__).resolve().parents[1]
result = run()
result['relation_calibration'] = calibrate()
result['exact_geometry'] = check_geometry()
result['balanced_weights'] = check_balanced_weights()
target = root / 'certificates/phase_checks.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(target.relative_to(root))
