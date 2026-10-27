"""4-turn street romance dialogue simulations: 20yo vs 40yo male with a 25yo woman.

Demonstrates:
- 4 full dialogue turns per character.
- Aloof, non-needy, ambiguous masculine strategy (suspense / emotional tension).
- Feminine reactions (curiosity, challenge, engagement).
- Integration with subactor/subllm and edialog.
"""
from edialog import Dialogue, Participant, FictionEngine, CallableFictionBackend, SubLLMJSON


def run_four_turn_dialogue(title, male_id, male_name, male_style, female_id, female_name, starting_situation):
    print(f"\n{'='*70}")
    print(f"=== {title} ===")
    print(f"Kontekst: {starting_situation}")
    print(f"{'='*70}\n")

    transport = SubLLMJSON(application="autogrammar-tillm", function="invoke", timeout=40)
    backend = CallableFictionBackend(transport)
    engine = FictionEngine(backend=backend)

    d = Dialogue((Participant(male_id, male_name), Participant(female_id, female_name)))
    d.add_turn(female_id, starting_situation, recipients=(male_id,))

    for turn_num in range(1, 5):
        # Kolejka Mężczyzny
        m_instr = (
            f"{male_style}. "
            f"Kolejka {turn_num}/4. Zachowaj magnetyczny chłód, powściągliwość, brak usłużności. "
            f"Nie odkrywaj intencji. Rzuć celną uwagę, która intryguje i zmusza kobietę do zastanawiania się, co myślisz."
        )
        prop_m = engine.generate(d, actor=male_id, recipients=(female_id,), instruction=m_instr)
        d.add_turn(male_id, prop_m.text, recipients=(female_id,))
        print(f"[{turn_num}A] {male_name}: \"{prop_m.text}\"")

        # Kolejka Kobiety
        f_instr = (
            f"{female_name} (25 l.). Kolejka {turn_num}/4. "
            f"Reakcja na słowa mężczyzny. Nie wiesz, na czym stoisz. Czujesz napięcie i zaciekawienie, "
            f"odpowiadasz z charakterem, podejmując grę słowną."
        )
        prop_f = engine.generate(d, actor=female_id, recipients=(male_id,), instruction=f_instr)
        d.add_turn(female_id, prop_f.text, recipients=(male_id,))
        print(f"[{turn_num}B] {female_name}: \"{prop_f.text}\"\n")


if __name__ == "__main__":
    # Dialog 1: 20-letni student i 25-latka
    run_four_turn_dialogue(
        title="SCENARIUSZ 1: 20-letni Mateusz i 25-letnia Klaudia (Kawiarnia)",
        male_id="mateusz",
        male_name="Mateusz (20 l.)",
        male_style="Mężczyzna 20 lat (student). Styl: nonszalancki chłód, zadziorność, bezczelny urok, brak podlizywania",
        female_id="klaudia",
        female_name="Klaudia (25 l.)",
        starting_situation="Klaudia stoi przed kawiarnią z książką pod pachą, rozgląda się za wolnym stolikiem i napotyka obojętne spojrzenie Mateusza siedzącego przy stoliku z jednym wolnym krzesłem."
    )

    # Dialog 2: 40-letni dojrzały mężczyzna i 25-latka
    run_four_turn_dialogue(
        title="SCENARIUSZ 2: 40-letni Tomasz i 25-letnia Klaudia (Przejście dla pieszych w deszczu)",
        male_id="tomasz",
        male_name="Tomasz (40 l.)",
        male_style="Mężczyzna 40 lat. Styl: opanowany, chłodny dżentelmen, magnetyczny dystans, tajemniczość, brak desperacji",
        female_id="klaudia",
        female_name="Klaudia (25 l.)",
        starting_situation="Klaudia stoi na światłach na rogu ulicy, marznąc w ulewnym deszczu. Obok stoi Tomasz z dużym czarnym parasolem, patrząc przed siebie obojętnie."
    )
