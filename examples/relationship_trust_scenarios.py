"""Demonstracja modelowania dystansu relacji, poziomu zaufania i zmiennych środowiskowych.

Pokazuje, jak w edialog w połączeniu z subactor/subllm można:
1. Zdefiniować profile aktorów i ich relacji (dystans społeczny, poziom zaufania, historia).
2. Wprowadzić zmienne środowiska (pogoda, pora dnia, otoczenie).
3. Generować diametralnie różne odpowiedzi za pośrednictwem author_brief i FictionEngine.
"""
from edialog import Dialogue, Participant, FictionEngine, FictionRequest, CallableFictionBackend, SubLLMJSON


def test_trust_and_environmental_distance():
    transport = SubLLMJSON(application="autogrammar-tillm", function="invoke", timeout=40)

    scenarios = [
        {
            "trust": "zerowe (obcy ludzie, pierwszy kontakt)",
            "social_distance": "duży / formalny dystans nieznajomych (per 'Pani')",
            "history": "Nigdy wcześniej się nie widzieli, przypadkowe spotkanie na ulicy.",
            "environment": "Zimna listopadowa ulewa, puste skrzyżowanie, migające żółte światło.",
            "request": FictionRequest(target={"nothing": 0.7, "happy": 0.1}, strategies=("quiet",)),
            "boundary_rules": [
                "Pełny szacunek do granic osobistych nieznajomej osoby.",
                "Forma grzecznościowa 'Pani', spokojny ton, zero narzucania się i zero wydawania poleceń."
            ]
        },
        {
            "trust": "niskie / ostrożne (znajomość z widzenia w biurowcu)",
            "social_distance": "uprzejmy dystans z nutą niedopowiedzenia (bez spoufalania się)",
            "history": "Mijają się w biurowcu, dotychczas zamienili tylko zdawkowe 'cześć' w windzie.",
            "environment": "Koniec pracy, ulewa, stoją pod zadaszeniem wejścia do biurowca.",
            "request": FictionRequest(target={"nothing": 0.65, "excited": 0.35}, strategies=("quiet", "anticipation")),
            "boundary_rules": [
                "Szanuj granice osobiste: zero rozkazów, zero presji, zero inwazyjności.",
                "Unikaj banalnego small-talku o pogodzie.",
                "Zastosuj subtelną, lekko ironiczną uwagę nawiązującą do wyjścia z pracy — zostawiając jej 100% swobody podjęcia rozmowy."
            ]
        },
        {
            "trust": "wysokie (zbudowana zażyłość, wzajemne zaufanie)",
            "social_distance": "bliski / intymny (per 'Ty', czułość, bezpośredniość)",
            "history": "Para po kilku randkach, duża chemia i wzajemne poczucie bezpieczeństwa.",
            "environment": "Ciepły letni deszcz o północy, puste uliczki starego miasta po wspólnej kolacji.",
            "request": FictionRequest(target={"happy": 0.7, "excited": 0.6}, strategies=("reunion", "anticipation")),
            "boundary_rules": [
                "Ciepły, bezpośredni ton wynikający z obopólnej zgody i bliskości.",
                "Naturalna swoboda i wspólnota doświadczenia ('my')."
            ]
        }
    ]

    for sc in scenarios:
        print(f"\n{'='*75}")
        print(f"POZIOM ZAUFANIA: {sc['trust'].upper()}")
        print(f"Dystans relacji: {sc['social_distance']}")
        print(f"Historia: {sc['history']}")
        print(f"Środowisko: {sc['environment']}")
        print(f"{'='*75}")

        def complete_with_brief(payload, sc=sc):
            enriched = dict(payload)
            if payload.get("task") == "generate_fiction_candidates":
                enriched["author_brief"] = {
                    "relationship_trust": sc["trust"],
                    "interpersonal_distance": sc["social_distance"],
                    "relationship_history": sc["history"],
                    "environment_context": sc["environment"],
                    "boundary_rules": sc["boundary_rules"],
                }
            return transport(enriched)

        custom_engine = FictionEngine(backend=CallableFictionBackend(complete_with_brief))
        d = Dialogue((Participant("tomasz", "Tomasz (40 l.)"), Participant("klaudia", "Klaudia (25 l.)")))
        d.add_turn("klaudia", f"Klaudia zatrzymuje się przed ścianą deszczu i spogląda na zegarek. {sc['environment']}", recipients=("tomasz",))

        prop = custom_engine.generate(
            d,
            actor="tomasz",
            recipients=("klaudia",),
            request=sc["request"],
        )

        print(f"\nWybrana kwestia Tomasza: \"{prop.text}\"")
        print("Kandydaci ocenieni przez model afektu:")
        for c in prop.candidates:
            print(f"  - [{c['distance']:.4f}]: \"{c['text']}\"")


if __name__ == "__main__":
    test_trust_and_environmental_distance()
