"""Run from an installed package: python examples/demo.py"""
import json
from edialog import Dialogue, DialogueEngine, Participant

dialogue = Dialogue((
    Participant('anna', 'Anna', aliases=('Anny', 'Annę'), address='Anno'),
    Participant('jan', 'Jan', aliases=('Jana',), address='Janie'),
    Participant('piotr', 'Piotr', aliases=('Piotra',), address='Piotrze'),
))
dialogue.add_turn('anna', 'Nie wiem, co mam przygotować na spotkanie.', recipients=('jan', 'piotr'))
dialogue.add_turn('piotr', 'Potrzebuję doprecyzowania zakresu.', recipients=('jan', 'anna'))
# Explicit synthetic starting points, not emotions inferred from the two messages.
dialogue.set_state('anna', {'tension': .7, 'relief': .05, 'confusion': .6})
dialogue.set_state('piotr', {'confusion': .5})

engine = DialogueEngine()
proposal = engine.propose(
    dialogue, actor='jan', recipients=('anna', 'piotr'),
    instruction='Zmniejsz napięcie u Anny do 0,4; zmniejsz dezorientację u Piotra; '
                'strategia: empatia i doprecyzowanie.',
)
print(json.dumps(proposal.to_dict(), ensure_ascii=False, indent=2))
# An explicit new simulation branch; the original history is unchanged.
branch = engine.advance_simulation(dialogue, proposal)
assert len(branch.turns) == len(dialogue.turns)+1
assert branch.turns[-1].kind == 'synthetic'
