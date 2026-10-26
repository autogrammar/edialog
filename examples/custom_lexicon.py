"""Explicit author-assigned motif, not automatically learned emotion weights."""
import json
from edialog import EmotionLexicon, TextEmotionAnalyzer

original = EmotionLexicon()
edited = original.with_weights('czerwona wstążka', {'scared': .8, 'sad': .2})
reloaded = EmotionLexicon.from_json(json.dumps(edited.to_dict()))
assert reloaded.model_id == edited.model_id
assert original.model_id != edited.model_id
print(TextEmotionAnalyzer(reloaded).analyze('Na stole leży czerwona wstążka.').to_dict())
