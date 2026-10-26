"""One sentence in three contexts; unknown is not the neutral category."""
import json
from edialog import TextEmotionAnalyzer

a = TextEmotionAnalyzer()
for history in ([], ['Ktoś nas śledzi.'], ['Cieszę się, że wróciłeś.']):
    r = a.analyze('Słyszę kroki.', history=history)
    print(json.dumps({'history': history, 'status': r.status,
                      'scores': r.scores, 'evidence': r.evidence}, ensure_ascii=False))
assert a.analyze('Słyszę kroki.').status == 'unknown'
assert a.analyze('Nie boję się.').scores['scared'] < a.analyze('Boję się.').scores['scared']
