"""Executable adapter demo using fixed test outputs, not a real language model."""
from edialog import CallableJSONBackend, Dialogue, DialogueEngine, Participant


def complete(payload):
    if payload['task'] == 'parse_request':
        return {'goals': [{'participant': 'anna', 'emotion': 'tension', 'direction': 'decrease'}],
                'strategies': ['clarify']}
    if payload['task'] == 'render_reply':
        return {'text': 'Anno, doprecyzujmy wspólnie, co powinno być gotowe na spotkanie.',
                'evidence_turn_ids': ['t1']}
    raise ValueError('Unknown task')


d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan')))
d.add_turn('anna', 'Nie wiem, co przygotować na spotkanie.', recipients=('jan',))
backend = CallableJSONBackend(complete)
p = DialogueEngine(nl_backend=backend, renderer=backend).propose(
    d, actor='jan', recipients=('anna',), instruction='Pomóż Annie spokojniej omówić przygotowania.',
)
print(p.text)
assert p.simulations['anna']['status'] == 'insufficient_state'
