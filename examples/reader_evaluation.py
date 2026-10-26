"""Metric demonstration with explicitly synthetic ratings, not research data."""
import json
from pathlib import Path
from edialog import evaluate_annotations

ratings = json.loads(Path(__file__).with_name('ratings.synthetic.json').read_text())
result = evaluate_annotations(ratings)
assert result['records'] == 2 and result['rated_dimensions'] == 3
print('SYNTHETIC RATINGS — demonstration only')
print(json.dumps(result, indent=2, ensure_ascii=False))
