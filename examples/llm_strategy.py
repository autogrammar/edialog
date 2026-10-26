"""Opt-in live LLM with author facts and a concrete strategy brief.

The brief guides the model; the library does not separately validate character
reactions, plot consistency or adherence to one-sentence output.
"""
import argparse
from edialog import (Dialogue, Participant, FictionEngine, FictionRequest,
                     CallableFictionBackend, OllamaJSON)

STRATEGY_BRIEFS = {
    'suspense': 'Nawiąż do wcześniejszego dźwięku i dodaj jedną niejednoznaczność; nie rozwiązuj zagadki.',
    'release': 'Wyjaśnij wcześniejszą niejednoznaczność zgodnie z faktami i pozwól postaci odetchnąć.',
    'confrontation': 'Nazwij sprzeczność między obietnicą a zachowaniem, zachowując głos postaci.',
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--strategy', choices=STRATEGY_BRIEFS, default='suspense')
    parser.add_argument('--base-url', default='http://localhost:11434')
    args = parser.parse_args()
    transport = OllamaJSON(args.model, base_url=args.base_url, timeout=120)

    def complete(payload):
        enriched = dict(payload)
        if payload['task'] == 'generate_fiction_candidates':
            enriched['author_brief'] = {
                'facts': ['Jan zna źródło kroków.', 'Anna i Piotr nie wiedzą, kto nadchodzi.'],
                'relationships': ['Anna zwykle ufa Janowi; Piotr podejrzewa, że Jan coś ukrywa.'],
                'strategy': STRATEGY_BRIEFS[args.strategy],
                'format': 'Każdy wariant ma być jednym zdaniem po polsku, wypowiadanym przez Jana.',
                'boundary': 'Opis relacji jest kontekstem autorskim; celem numerycznym jest ton sceny.',
            }
        return transport(enriched)

    d = Dialogue((Participant('anna', 'Anna'), Participant('jan', 'Jan'), Participant('piotr', 'Piotr')))
    d.add_turn('anna', 'Słyszę kroki, chociaż wszyscy już wyszli.', recipients=('jan', 'piotr'))
    p = FictionEngine(backend=CallableFictionBackend(complete)).generate(
        d, actor='jan', recipients=('anna', 'piotr'),
        request=FictionRequest(strategies=(args.strategy,)))
    print(p.text)
    for candidate in p.candidates:
        print(candidate['distance'], candidate['text'])


if __name__ == '__main__':
    main()
