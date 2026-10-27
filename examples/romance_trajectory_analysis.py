"""Analysis of emotional trajectory and tension in 4-turn romance dialogues.

Demonstrates how edialog's FictionEngine tracks:
1. Reader proxy (overall scene atmosphere)
2. Character expression proxies (individual speaker tone)
3. Dynamic tension accumulation between an aloof male and an intrigued female.
"""
from edialog import Dialogue, Participant, FictionEngine, EmotionLexicon, TextEmotionAnalyzer


def analyze_romance_dialogues():
    # Extend lexicon with romance, tension, and ambiguity tokens
    romance_tokens = {
        'pułapka': {'scared': 0.7, 'excited': 0.3},
        'ostrzeżenie': {'scared': 0.65, 'excited': 0.25},
        'ostrzegałam': {'scared': 0.6, 'excited': 0.2},
        'zaryzykuję': {'excited': 0.7, 'scared': 0.4},
        'odwagi': {'excited': 0.6, 'scared': 0.3},
        'wyzwanie': {'excited': 0.75, 'happy': 0.2},
        'tajemnica': {'excited': 0.6, 'scared': 0.4},
        'niebezpieczny': {'scared': 0.75, 'excited': 0.35},
        'geometria': {'nothing': 0.5, 'excited': 0.3},
        'błąd': {'scared': 0.5, 'excited': 0.4},
        'wciągnie': {'scared': 0.6, 'excited': 0.5},
        'rekwizyt': {'nothing': 0.6, 'excited': 0.2},
    }

    base_cfg = EmotionLexicon().to_dict()
    merged_cfg = {
        'version': 'romance-tension-v1',
        'provenance': 'Romance tension & ambiguity extensions for edialog',
        'entries': {**base_cfg['entries'], **romance_tokens},
        'context_rules': base_cfg['context_rules']
    }

    custom_lexicon = EmotionLexicon(merged_cfg)
    analyzer = TextEmotionAnalyzer(custom_lexicon)
    engine = FictionEngine(analyzer=analyzer)

    # 40-letni Tomasz & 25-letnia Klaudia
    d = Dialogue((Participant('tomasz', 'Tomasz (40 l.)'), Participant('klaudia', 'Klaudia (25 l.)')))
    d.add_turn('klaudia', 'Klaudia stoi na światłach na rogu ulicy, marznąc w ulewnym deszczu. Obok stoi Tomasz z dużym czarnym parasolem, patrząc przed siebie obojętnie.')
    d.add_turn('tomasz', 'Zaraz zmieni się światło. Jeśli zrobi pani krok w lewo, przestanie padać.')
    d.add_turn('klaudia', 'Krok w lewo? Brzmi jak obietnica albo pułapka... ale zmarzłam za bardzo, żeby wybierać.')
    d.add_turn('tomasz', 'To tylko kwestia geometrii. Zielone zapali się za pięć sekund.')
    d.add_turn('klaudia', 'Pięć sekund? Odlicza pan na głos czy mam zgadywać, w którą stronę ruszymy, gdy zapali się zielone?')
    d.add_turn('tomasz', 'Trzy. Dwa. Kierunek jest jeden – przynajmniej dopóki nie staniemy po drugiej stronie.')
    d.add_turn('klaudia', 'Jeden. Zobaczymy, czy dotrzyma pan kroku, zanim zapytam, dokąd właściwie prowadzi ta pańska geometria.')
    d.add_turn('tomasz', 'Zielone. Proszę iść równo, kałuża przy krawężniku jest głębsza, niż się wydaje.')
    d.add_turn('klaudia', 'Ostrzega mnie pan przed kałużą, a ja wciąż nie wiem, czy po drugiej stronie nie wciągnie mnie pan w coś znacznie głębszego.')

    res = engine.analyze_dialogue(d, actor='tomasz', recipients=('klaudia',))
    print("=== RAPORT TRAJEKTORII AFEKTU DLA DIALOGU 4-KOLEJKOWEGO ===")
    print(f"Status: {res['status']}")
    print(f"Końcowy ton sceny (reader_proxy):")
    for k, v in res['reader_proxy'].items():
        if v > 0.01:
            print(f"  - {k}: {v:.4f}")

    print("\nEkspresja postaci (kobieta vs mężczyzna):")
    for char, vec in res['character_expression_proxies'].items():
        active = {k: round(v, 4) for k, v in vec.items() if v > 0.01}
        print(f"  - {char}: {active}")

    print("\nEwolucja napięcia i dynamiki według tur:")
    for turn in res['timeline']:
        sig = {k: round(v, 3) for k, v in turn['reader_proxy'].items() if v > 0.01}
        print(f"  [{turn['turn_id']}] {turn['speaker']:7s} -> {sig}")


if __name__ == '__main__':
    analyze_romance_dialogues()
