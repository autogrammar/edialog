"""Demonstracja modelowania dystansu relacji, poziomu zaufania i zmiennych środowiskowych.

Pokazuje, jak w edialog w połączeniu z subactor/subllm można:
1. Zdefiniować profile aktorów i ich relacji (dystans społeczny, poziom zaufania, historia).
2. Wprowadzić zmienne środowiska (pogoda, pora dnia, otoczenie).
3. Generować diametralnie różne odpowiedzi za pośrednictwem author_brief i FictionEngine.
"""
from edialog import Dialogue, Participant, FictionEngine, CallableFictionBackend, SubLLMJSON


def test_trust_and_environmental_distance():
    transport = SubLLMJSON(application="autogrammar-tillm", function="invoke", timeout=40)

    scenarios = [
        {
            "trust": "zerowe (obcy ludzie, pierwszy kontakt)",
            "social_distance": "duży / formalny dystans nieznajomych (per 'Pani')",
            "history": "Nigdy wcześniej się nie widzieli, przypadkowe spotkanie na ulicy.",
            "environment": "Zimna listopadowa ulewa, puste skrzyżowanie, migające żółte światło.",
            "prompt_goal": "Tomasz (40 l.) do Klaudii (25 l.). Dystans chłodny, z klasą, bez spoufalania się."
        },
        {
            "trust": "niskie / ostrożne (znajomość ze słyszenia, niepewność)",
            "social_distance": "średni dystans / badanie gruntu / ostrożność",
            "history": "Mijają się w biurowcu, Klaudia uważa go za człowieka tajemniczego i niedostępnego.",
            "environment": "Godzina szczytu, tłum pod wiatą przystanku, gęsty deszcz.",
            "prompt_goal": "Tomasz (40 l.) do Klaudii (25 l.). Ton intrygujący, zbijający z tropu, rzucający wyzwanie."
        },
        {
            "trust": "wysokie (zbudowana zażyłość, wzajemne sekrety)",
            "social_distance": "bliski / intymny (per 'Ty', czułość, bezpośredniość)",
            "history": "Para po kilku randkach, duża chemia i wzajemne zaufanie.",
            "environment": "Ciepły letni deszcz o północy, puste uliczki starego miasta po wspólnej kolacji.",
            "prompt_goal": "Tomasz (40 l.) do Klaudii (25 l.). Ciepły, magnetyczny ton, głębokie zaufanie i flirt."
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
                    "rule": "Dostosuj dobór słów, formę gramatyczną (Pani vs Ty) i intymność do podanego zaufania."
                }
            return transport(enriched)

        custom_engine = FictionEngine(backend=CallableFictionBackend(complete_with_brief))
        d = Dialogue((Participant("tomasz", "Tomasz (40 l.)"), Participant("klaudia", "Klaudia (25 l.)")))
        d.add_turn("klaudia", f"Klaudia stoi na światłach na rogu ulicy. {sc['environment']}", recipients=("tomasz",))

        prop = custom_engine.generate(
            d,
            actor="tomasz",
            recipients=("klaudia",),
            instruction=sc["prompt_goal"]
        )

        print(f"\nWybrana kwestia Tomasza: \"{prop.text}\"")
        print("Kandydaci ocenieni przez model afektu:")
        for c in prop.candidates:
            print(f"  - [{c['distance']:.4f}]: \"{c['text']}\"")


if __name__ == "__main__":
    test_trust_and_environmental_distance()
