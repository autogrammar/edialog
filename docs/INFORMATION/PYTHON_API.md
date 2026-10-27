---
{
  "schema": "edialog.docs/document/v1",
  "id": "python-api",
  "kind": "information",
  "version": 1,
  "title": "Publiczne API Python",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "1d62c806549f71bc4a1ed3c9001e64a9b5613b7db3c369528d826d71278b7f26",
  "priority": "P2",
  "evidence": [
    "src/edialog/__init__.py",
    "src/edialog/models.py"
  ]
}
---

# Publiczne API Python

<!-- docs:section summary -->
## Cel i rezultat

Pakiet importuje się przez `edialog`. Wspólna historia dialogu zasila niezależny tryb literacki i wcześniejszy tryb wspierającej komunikacji.

<!-- docs:section details -->
## Zakres i rozwiązanie

| API | Zastosowanie |
|---|---|
| `Participant(id, name, aliases=(), address=None)` | Stała tożsamość postaci i jawne aliasy |
| `Dialogue(participants)` | Historia 2–50 postaci, do 200 kwestii |
| `add_turn(speaker, content, recipients=..., kind=...)` | Dopisanie obserwowanej lub syntetycznej kwestii |
| `TextEmotionAnalyzer.analyze(text, history=...)` | Wagi i ślad dopasowań słów |
| `EmotionLexicon.with_weights(phrase, weights)` | Nowy słownik z jawną zmianą wag |
| `FictionRequest(target, strategies, tolerance)` | Cel tonu i strategie |
| `FictionEngine.generate(...)` | Warianty następnej kwestii, ranking, DSL |
| `FictionEngine.replay(source, dialogue)` | Ponowne obliczenie planu z migawki |
| `FictionEngine.continue_scene(dialogue, proposal)` | Kopia sceny z syntetyczną kwestią |
| `analyze_image(path, backend=...)` | Cechy obrazu i opcjonalne sygnały sceny |
| `evaluate_annotations(records)` | MAE względem dostarczonych ocen |

`Proposal` i `FictionProposal` to różne typy. Tryb wspierający używa `DialogueEngine`, `Request`, `Goal`; [opis](SUPPORTIVE_DIALOGUES.md). Błędy dziedziczą po `EDialogError`: `ValidationError`, `NeedsClarification`, `UnsupportedObjective`, `BackendError`.

<!-- docs:section validation -->
## Weryfikacja

`python3 -m unittest discover -s tests -v` obejmuje eksporty używane przez API, walidację, serializację i historię. Końcowa kontrola instalacji importuje pakiet z wheel poza katalogiem źródłowym.

<!-- docs:section risks -->
## Ryzyka i następny krok

Zmiana nazwy importu jest niezgodna ze starym `affectdialog`; zastosuj [migrację](../REFACTORING/PROJECT_RENAME.md). Obiekty nie wysyłają wiadomości do uczestników. Sekwencja kolejnych wywołań pozostaje pod kontrolą autora.
