"""Save/replay a plan and explicitly append a fictional line to a copy."""
import argparse
from pathlib import Path
from edialog import Dialogue, Participant, FictionEngine, FictionRequest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, help='Optional destination for the generated DSL')
    args = parser.parse_args()
    d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan')))
    d.add_turn('anna', 'Boję się. Ktoś nas śledzi.')
    engine = FictionEngine()
    p = engine.generate(d, actor='jan', recipients=('anna',),
                        request=FictionRequest({'scared': .8}))
    assert engine.replay(p.dsl, d).to_dict() == p.to_dict()
    next_scene = engine.continue_scene(d, p)
    assert len(d.turns) == 1 and len(next_scene.turns) == 2
    assert next_scene.turns[-1].kind == 'synthetic'
    if args.out:
        args.out.write_text(p.dsl+'\n', encoding='utf-8')
    print('DSL replay matches; original history unchanged.')
    print(next_scene.turns[-1].text)


if __name__ == '__main__':
    main()
