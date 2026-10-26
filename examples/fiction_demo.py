"""Offline, reproducible example; all scores are narrative proxies."""
import json
from edialog import (Dialogue, Participant, FictionEngine, FictionRequest,
                          TextEmotionAnalyzer, EmotionLexicon)


def make_scene():
    d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan'), Participant('piotr', 'Piotr')))
    d.add_turn('anna', 'Ktoś jest za drzwiami. Boję się.', recipients=('jan', 'piotr'))
    d.add_turn('piotr', 'Słyszę kroki.', recipients=('jan', 'anna'))
    return d


def main():
    analyzer = TextEmotionAnalyzer()
    print('To samo zdanie, różny wcześniejszy kontekst:')
    for history in ([], ['Ktoś nas śledzi.'], ['Cieszę się, że wróciłeś.']):
        result = analyzer.analyze('Słyszę kroki.', history=history)
        print(json.dumps({'history': history, 'scores': result.scores, 'evidence': result.evidence}, ensure_ascii=False))
    d, engine = make_scene(), FictionEngine()
    proposal = engine.generate(d, actor='jan', recipients=('anna', 'piotr'),
        instruction='Cel: strach=0,85; strategia: suspense', candidates=[
            'Spokojnie. To tylko wiatr.',
            'Nie otwieraj. Ktoś jest za drzwiami. Słyszysz kroki?',
            'Boję się. Ktoś nas śledzi. Uciekajmy!'])
    print('\nWybrana wypowiedź:', proposal.text)
    print('Wynik modelu:', proposal.candidates[0]['reader_proxy'])
    assert engine.replay(proposal.dsl, d).to_dict() == proposal.to_dict()
    continued = engine.continue_scene(d, proposal)
    release = engine.generate(continued, actor='anna', recipients=('jan', 'piotr'),
        request=FictionRequest({'scared': .1, 'happy': .5}, ('release',)),
        candidates=['To tylko wiatr. Jesteśmy bezpieczni.', 'Nie otwieraj!'])
    print('\nKolejny krok:', release.text)
    print('Cel osiągnięty w modelu:', release.candidates[0]['target_met_in_model'])
    # Separate, explicit author edit; no automatic learning from generated output.
    edited = EmotionLexicon().with_weights('czerwona wstążka', {'scared': .8})
    print('\nWłasny motyw:', TextEmotionAnalyzer(edited).analyze('Czerwona wstążka.').scores)


if __name__ == '__main__':
    main()
