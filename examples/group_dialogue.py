"""Recipient visibility is distinct from individual emotional predictions."""
from edialog import Dialogue, Participant, FictionEngine, FictionRequest

d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan'),
              Participant('piotr', 'Piotr')))
public = d.add_turn('piotr', 'Ktoś jest za drzwiami.')
private = d.add_turn('anna', 'To nasza tajemnica.', recipients=('jan',))
engine = FictionEngine()
request = FictionRequest({'scared': .8}, ('suspense',))
individual = engine.generate(d, actor='jan', recipients=('anna',), request=request)
group = engine.generate(d, actor='jan', recipients=('anna', 'piotr'), request=request)
assert private.id in individual.baseline['context_turn_ids']
assert private.id not in group.baseline['context_turn_ids']
assert public.id in group.baseline['context_turn_ids']
print('Do Anny:', individual.text)
print('Do grupy:', group.text)
print('Wynik tonu sceny, nie emocje każdej osoby:', group.candidates[0]['reader_proxy'])
