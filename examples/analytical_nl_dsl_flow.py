"""Analityczny rozkład wielokolejkowego dialogu (NL -> Metryki -> Cel NL -> Odpowiedź + DSL/JSON/YAML + Diagram ASCII).

Dla każdej kolejki dialogu prezentuje kolejno 4 bloki procesowo-analityczne:
  1. Opis sytuacji (środowisko, historia relacji, dystans, osoba vs grupa)
  2. Zdanie wejściowe do analizy + metryki stanu emocjonalnego (TextEmotionAnalyzer + reader_proxy_before)
  3. Opis stanu docelowego w NL + skompilowane parametry (target_vector, strategies, Action URI)
  4. Odpowiedź edialog (dla danej osoby lub grupy) + równoległy opis stanu w DSL, YAML i JSON + diagram ASCII.

Uruchomienie:
  PYTHONPATH=src .venv/bin/python examples/analytical_nl_dsl_flow.py
  PYTHONPATH=/home/tom/github/subactor/subllm/src:src .venv/bin/python examples/analytical_nl_dsl_flow.py --live-subllm
"""
from __future__ import annotations

import argparse
import json

from edialog import Dialogue, Participant, analyze_and_respond_turn


def build_cast() -> Dialogue:
    return Dialogue([
        Participant('tomasz', 'Tomasz (40 l., główny architekt)'),
        Participant('klaudia', 'Klaudia (25 l., projektantka wnętrz)'),
        Participant('ewa', 'Ewa (28 l., koordynatorka projektu)'),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description='Analityczny przepływ NL -> Metryki -> Cel NL -> Odpowiedź + DSL/JSON/YAML.')
    parser.add_argument('--live-subllm', action='store_true', help='Użyj live SubLLM (subactor/subllm) do generowania kandydatów.')
    args = parser.parse_args()

    dialogue = build_cast()
    backend = 'subllm' if args.live_subllm else None

    turns_spec = [
        {
            'situation': {
                'title': 'Kolejka 1: Pierwszy kontakt w sytuacyjnym napięciu (Osoba -> Osoba)',
                'environment': 'Wieczór po zamknięciu biura, ulewa za przeszklonym holem, awaria wind.',
                'history': 'Znają się dotąd wyłącznie z widzenia na korytarzu czwartego piętra.',
                'social_distance': 'Uprzejmy dystans zawodowy, pierwsze bezpośrednie zagajenie.',
            },
            'trust_level': 'low',
            'input_speaker': 'klaudia',
            'input_recipients': ['tomasz'],
            'input_sentence': 'Boję się, że przez tę burzę i awarię utknęliśmy tu na dobre, a ja naprawdę nie znoszę takich pustych korytarzy po zmroku.',
            'actor': 'tomasz',
            'recipients': ['klaudia'],
            'target_nl': 'Cel: neutralnosc=0,70; cel: radosc=0,35; strategia: wyciszenie i ulga',
            'author_brief': {
                'intent': 'Rozładuj napięcie i lęk Klaudii spokojnym, rzeczowym tonem z odrobiną suchego humoru, bez spoufalania się.',
            },
            'offline_candidates': [
                'Spokojnie. To tylko awaria zasilania na jednym pionie; możemy zejść oświetloną klatką od strony dziedzińca i cieszę się, że mamy zapasową latarkę.',
                'Boję się, że ma pani rację i zaraz zgaśnie również światło awaryjne na całym piętrze.',
                'Zwyczajnie poczekajmy przy recepcji. Nie trzeba teraz niczego przyspieszać, ochrona zaraz otworzy boczne wyjście.',
            ],
        },
        {
            'situation': {
                'title': 'Kolejka 2: Zejście do holu i włączenie trzeciej osoby (Odpowiedź dla GRUPY)',
                'environment': 'Parter przy wyjściu na dziedziniec; dołącza zdenerwowana Ewa z dokumentacją.',
                'history': 'Po pierwszym spokojnym komentarzu Tomasza napięcie opadło, pojawia się wspólny problem zespołu.',
                'social_distance': 'Malejący dystans, przejście w koleżeńską współpracę w grupie (Klaudia + Ewa).',
            },
            'trust_level': 'rebuilding',
            'input_speaker': 'ewa',
            'input_recipients': ['tomasz', 'klaudia'],
            'input_sentence': 'Jestem wściekła na administrację! Przez to zalanie podjazdu kurier odwołał odbiór makiet i cały nasz jutrzejszy pokaz wisi na włosku.',
            'actor': 'tomasz',
            'recipients': ['klaudia', 'ewa'],
            'target_nl': 'Cel: neutralnosc=0,65; cel: ekscytacja=0,40; strategia: wyciszenie i oczekiwanie',
            'author_brief': {
                'intent': 'Odpowiedz jednocześnie Klaudii i Ewie (grupie): wycisz gniew Ewy, zaproponuj konkretny plan awaryjny i zamień frustrację w spokojną gotowość do działania.',
            },
            'offline_candidates': [
                'Spokojnie, dziewczyny. Makiety są już spakowane w tubach, a mój samochód stoi na suchym poziomie minus jeden — ruszajmy rano prosto na salę przed otwarciem pokazu.',
                'Kłamiesz, administracja uprzedzała o remoncie od tygodnia i teraz sami jesteśmy sobie winni.',
                'Zwyczajnie zostawmy te makiety w recepcji i zobaczmy jutro rano, czy ktoś je odbierze.',
            ],
        },
        {
            'situation': {
                'title': 'Kolejka 3: Po rozwiązaniu kryzysu — bezpośredni zwrot z wyższym zaufaniem (Osoba -> Osoba)',
                'environment': 'Zadaszony podjazd przed biurowcem, deszcz cichnie, Ewa poszła po klucze do magazynu.',
                'history': 'Tomasz opanował sytuację z windą i uratował jutrzejszy pokaz makiet; Klaudia czuje ulgę i wyraźną sympatię.',
                'social_distance': 'Zbudowane zaufanie sytuacyjne, swobodna i ciepła wymiana jeden-na-jeden.',
            },
            'trust_level': 'high',
            'input_speaker': 'klaudia',
            'input_recipients': ['tomasz'],
            'input_sentence': 'Cieszę się, że trafiliśmy dziś na ciebie na tym czwartym piętrze. Naprawdę uratowałeś nam wieczór i jutrzejszą prezentację.',
            'actor': 'tomasz',
            'recipients': ['klaudia'],
            'target_nl': 'Cel: radosc=0,60; cel: ekscytacja=0,45; strategia: powrot i oczekiwanie',
            'author_brief': {
                'intent': 'Przyjmij podziękowanie z klasą i subtelnym ciepłem, zostawiając naturalny pretekst do wspólnej kawy jutro po prezentacji.',
            },
            'offline_candidates': [
                'Cieszę się, że mogłem pomóc. Zostawmy formalności na jutro — nie mogę się doczekać, żeby po waszej prezentacji sprawdzić, czy kawa na dole smakuje lepiej niż deszcz na czwartym piętrze.',
                'To tylko rutyna. Zamknę bagażnik i wracam do swoich rysunków.',
                'Boję się, że jutro rano korki i tak zatrzymają całe miasto.',
            ],
        },
    ]

    current_dialogue: Dialogue | dict = dialogue
    all_records = []

    for idx, spec in enumerate(turns_spec, start=1):
        rec = analyze_and_respond_turn(
            current_dialogue,
            situation=spec['situation'],
            input_speaker=spec['input_speaker'],
            input_sentence=spec['input_sentence'],
            input_recipients=spec['input_recipients'],
            actor=spec['actor'],
            recipients=spec['recipients'],
            target_nl=spec['target_nl'],
            trust_level=spec['trust_level'],
            author_brief=spec['author_brief'],
            candidates=None if args.live_subllm else spec['offline_candidates'],
            backend=backend,
            step_no=idx,
        )
        current_dialogue = rec['updated_dialogue']
        all_records.append(rec)

        print('\n' + rec['ascii_diagram'])
        print('\n--- RÓWNOLEGŁY OPIS STANU I PARAMETRÓW (A: Kompaktowy DSL) ---')
        print(rec['4_edialog_response_and_parallel_dsl']['parallel_representations']['compact_dsl'])
        print('\n--- RÓWNOLEGŁY OPIS STANU I PARAMETRÓW (B: YAML) ---')
        print(rec['4_edialog_response_and_parallel_dsl']['parallel_representations']['yaml_state'])
        print('\n--- RÓWNOLEGŁY OPIS STANU I PARAMETRÓW (C: JSON) ---')
        print(json.dumps(rec['4_edialog_response_and_parallel_dsl']['parallel_representations']['json_state'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
