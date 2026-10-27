---
{
  "schema": "edialog.docs/document/v1",
  "id": "supportive-dialogues",
  "kind": "information",
  "version": 1,
  "title": "Wcześniejszy tryb wspierającego dialogu",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "db31b877f2b96dde1ce458e11207ea989f3500c55ffe960370ef141f04a942bc",
  "priority": "P2",
  "evidence": [
    "src/edialog/engine.py",
    "src/edialog/models.py",
    "examples/demo.py"
  ]
}
---

# Wcześniejszy tryb wspierającego dialogu

<!-- docs:section summary -->
## Cel i rezultat

`DialogueEngine` zachowuje wcześniejsze API planów wspierającej komunikacji i symulacji. Jego model różni się od literackiego `FictionEngine`.

<!-- docs:section details -->
## Zakres i rozwiązanie

```python
from edialog import Dialogue, Participant, DialogueEngine

d = Dialogue((Participant("anna", "Anna", aliases=("Anny",)),
              Participant("jan", "Jan")))
d.add_turn("anna", "Nie wiem, co przygotować.")
d.set_state("anna", {"tension": 0.7}, origin="synthetic_fixture")
p = DialogueEngine().propose(
    d, actor="jan", recipients=("anna",),
    instruction="Zmniejsz napięcie u Anny do 0,4; strategia: empatia",
)
```

Strategie: `empathy`, `clarify`, `explain`, `invite`, `summarize`, `deescalate`. Cele dotyczą zmniejszania napięcia, frustracji i dezorientacji oraz zwiększania ciekawości, ulgi i spokoju.

Odczyty `Reading` mają pochodzenie `synthetic_fixture`, `self_report` albo `simulation`. Brak aktualnych danych daje `insufficient_state`. `advance_simulation` tworzy nową kopię i oznacza zapis jako symulację. Plan `affect-dialogue` 0.2 oraz wykonawczy AffectScript 0.1 zachowują format.

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/demo.py` i `python3 examples/backend_fixture.py` działają po zmianie importu. Testy wersji 0.2 pozostały w suite regresji.

<!-- docs:section risks -->
## Ryzyka i następny krok

W tym trybie efekt strategii jest z góry przypisaną wartością, niezależną od rzeczywistych słów renderera. Nie utożsamiaj go z nową analizą leksykalną. W dialogach literackich wybierz `FictionEngine`.
