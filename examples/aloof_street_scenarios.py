"""Aloof/enigmatic street encounter scenarios: 20yo vs 40yo male with a 25yo woman.

Tested via edialog FictionEngine and subactor/subllm.
Demonstrates suspense, emotional tension, ambivalence and non-needy attraction.
"""
from edialog import Dialogue, Participant, FictionEngine, CallableFictionBackend, SubLLMJSON


def run_aloof_scenarios():
    transport = SubLLMJSON(application="autogrammar-tillm", function="invoke", timeout=30)
    backend = CallableFictionBackend(transport)
    engine = FictionEngine(backend=backend)

    scenarios = [
        {
            "name": "20-letni chłopak (kawiarnia) — pozorny chłód i niejednoznaczność",
            "actor_id": "mateusz",
            "actor_name": "Mateusz (20 l.)",
            "woman_id": "klaudia",
            "woman_name": "Klaudia (25 l.)",
            "context": "Klaudia stoi przed kawiarnią z książką, zerka na wolny stolik, po czym jej wzrok spotyka się ze spojrzeniem Mateusza.",
            "instruction": "Mężczyzna 20 lat (student). Strategia: suspense / obojętność / niejednoznaczność. Mężczyzna zachowuje pozorny chłód, obojętność lub lekki dystans, rzuca jedną intrygującą uwagę bez przymilania się, budząc u 25-letniej kobiety niepewność i zaciekawienie.",
        },
        {
            "name": "40-letni mężczyzna (deszcz) — magnetyczny dystans i enigmatyczność",
            "actor_id": "tomasz",
            "actor_name": "Tomasz (40 l.)",
            "woman_id": "klaudia",
            "woman_name": "Klaudia (25 l.)",
            "context": "Klaudia zatrzymuje się na światłach w deszczu, zerka na eleganckiego 40-latka pod parasolem, licząc że zaoferuje schronienie. Tomasz patrzy przed siebie, ignorując jej spojrzenie.",
            "instruction": "Mężczyzna 40 lat. Styl: opanowany, chłodny, tajemniczy i niedostępny. Nie proponuje parasola jak petent. Rzuca jedno celne, obojętne, ale magnetyczne zdanie w przestrzeń lub do niej, które burzy jej pewność siebie i budzi fascynację.",
        }
    ]

    for sc in scenarios:
        print(f"\n==========================================")
        print(f"SCENARIUSZ: {sc['name']}")
        print(f"Kontekst: {sc['context']}")
        print(f"==========================================")

        d = Dialogue((
            Participant(sc["actor_id"], sc["actor_name"]),
            Participant(sc["woman_id"], sc["woman_name"]),
        ))
        d.add_turn(sc["woman_id"], sc["context"], recipients=(sc["actor_id"],))

        male_proposal = engine.generate(
            d,
            actor=sc["actor_id"],
            recipients=(sc["woman_id"],),
            instruction=sc["instruction"],
        )
        print(f"\nKwestia męska (wybrana): \"{male_proposal.text}\"")
        print("Wszystkie warianty ocenione przez model afektu:")
        for c in male_proposal.candidates:
            print(f"  - [{c['distance']:.4f}]: \"{c['text']}\"")

        # Symulacja reakcji Klaudii
        d.add_turn(sc["actor_id"], male_proposal.text, recipients=(sc["woman_id"],))
        woman_reaction = engine.generate(
            d,
            actor=sc["woman_id"],
            recipients=(sc["actor_id"],),
            instruction=f"Klaudia (25 l.). Reakcja na słowa mężczyzny. Jest zbita z tropu, zaintrygowana, nie wie co on naprawdę myśli, ale to ona podejmuje grę.",
        )
        print(f"\nReakcja Klaudii: \"{woman_reaction.text}\"")


if __name__ == "__main__":
    run_aloof_scenarios()
