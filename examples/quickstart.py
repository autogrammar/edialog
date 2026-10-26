"""Smallest offline example. Run after installing edialog."""
from edialog import Dialogue, Participant, FictionEngine

d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan')))
d.add_turn('anna', 'Słyszę kroki. Ktoś jest za drzwiami.')
engine = FictionEngine()
p = engine.generate(d, actor='jan', recipients=('anna',),
                    instruction='Cel: strach=0,8; strategia: suspense')
print(p.text)
print(p.candidates[0]['reader_proxy'])
assert p.status == 'fiction_draft'
assert engine.replay(p.dsl, d).text == p.text
