"""Street romance dialogue scenarios: 20yo vs 40yo approaching a 25yo woman.

Tested via edialog FictionEngine and subactor/subllm.
"""
from edialog import Dialogue, Participant, FictionEngine, FictionRequest, CallableFictionBackend, SubLLMJSON


def run_romance_street_scenarios():
    transport = SubLLMJSON(application="autogrammar-tillm", function="invoke", timeout=30)
    backend = CallableFictionBackend(transport)
    engine = FictionEngine(backend=backend)

    scenarios = [
        {
            "title": "20-letni chłopak (student) zagaduje 25-letnią kobietę na ulicy",
            "actor_id": "mateusz",
            "actor_name": "Mateusz (20 l.)",
            "actor_desc": "20-letni student, bezpośredni, spontaniczny, lekki, z młodzieńczym entuzjazmem",
            "woman_id": "klaudia",
            "woman_name": "Klaudia (25 l.)",
            "context_line": "Klaudia idzie powolnym krokiem ulicą z książką w dłoni, rozglądając się po witrynach kawiarni.",
            "instruction": "Nawiąż kontakt romantyczny na ulicy z 25-letnią nieznajomą. Mężczyzna 20 lat, student. Zwróć uwagę na książkę i kawiarnię. Ton lekki, uroczy, niewymuszony."
        },
        {
            "title": "40-letni dojrzały mężczyzna zagaduje 25-letnią kobietę na ulicy",
            "actor_id": "tomasz",
            "actor_name": "Tomasz (40 l.)",
            "actor_desc": "40-letni mężczyzna, elegancki, opanowany, z klasą i dystansem, kulturalny dżentelmen",
            "woman_id": "klaudia",
            "woman_name": "Klaudia (25 l.)",
            "context_line": "Klaudia zatrzymuje się na rogu ulicy przed przejściem dla pieszych w deszczowe popołudnie.",
            "instruction": "Nawiąż elegancki kontakt z 25-letnią nieznajomą na przejściu dla pieszych. Mężczyzna 40 lat z klasą. Kulturalny dżentelmen, bezpieczny ton z subtelnym uśmiechem."
        }
    ]

    results = []
    for sc in scenarios:
        d = Dialogue((
            Participant(sc["actor_id"], sc["actor_name"]),
            Participant(sc["woman_id"], sc["woman_name"]),
        ))
        d.add_turn(sc["woman_id"], sc["context_line"], recipients=(sc["actor_id"],))

        proposal = engine.generate(
            d,
            actor=sc["actor_id"],
            recipients=(sc["woman_id"],),
            instruction=sc["instruction"]
        )
        results.append({
            "scenario": sc["title"],
            "chosen_text": proposal.text,
            "candidates": proposal.candidates,
        })

    return results


if __name__ == "__main__":
    results = run_romance_street_scenarios()
    for res in results:
        print(f"\n=== {res['scenario']} ===")
        print(f"Wybrana: {res['chosen_text']}")
        for c in res['candidates']:
            print(f"  - [{c['distance']:.4f}] {c['text']}")
