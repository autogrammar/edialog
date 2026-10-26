"""Offline callback contract: a fixed fixture stands in for an LLM."""
from edialog import (Dialogue, Participant, FictionEngine, FictionRequest,
                     CallableFictionBackend)

calls = []


def complete(payload):
    assert payload['task'] == 'generate_fiction_candidates'
    assert payload['request']['strategies'] == ['suspense']
    calls.append(payload)
    return {'candidates': [
        {'text': 'Spokojnie. To tylko wiatr.', 'evidence_turn_ids': ['t1']},
        {'text': 'Nie otwieraj. Ktoś jest za drzwiami.', 'evidence_turn_ids': ['t1']},
    ]}


d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan')))
d.add_turn('anna', 'Słyszę kroki.')
p = FictionEngine(backend=CallableFictionBackend(complete)).generate(
    d, actor='jan', recipients=('anna',), request=FictionRequest({'scared': .8}, ('suspense',)))
assert len(calls) == 1 and len(p.candidates) == 2
assert p.text.startswith('Nie otwieraj')
print('Fixture result, not a real model output:', p.text)
