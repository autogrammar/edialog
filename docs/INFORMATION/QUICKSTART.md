---
{
  "schema": "edialog.docs/document/v1",
  "id": "quickstart",
  "kind": "information",
  "version": 1,
  "title": "Pierwszy dialog w edialog",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "86c18b79f14d7d74dbdcab58dbe17b7722d42d8ab594a2cd4bd49c7efe7128eb",
  "priority": "P2",
  "evidence": [
    "examples/quickstart.py",
    "pyproject.toml"
  ]
}
---

# Pierwszy dialog w edialog

<!-- docs:section summary -->
## Cel i rezultat

Zainstaluj edialog 0.4.0 i wygeneruj fikcyjną kwestię bez modelu ani połączenia sieciowego. Wersja bazowa nie ma zależności wykonawczych.

<!-- docs:section details -->
## Zakres i rozwiązanie

Po rozpakowaniu archiwum przejdź do katalogu projektu:

```bash
python3 -m pip install dist/edialog-0.4.0-py3-none-any.whl
python3 examples/quickstart.py
```

Kod źródłowy można zainstalować przez `python3 -m pip install .`. Nie zakładamy, że ten projekt jest opublikowany w PyPI pod nazwą edialog.

```python
from edialog import Dialogue, Participant, FictionEngine

d = Dialogue((Participant("anna", "Anna"), Participant("jan", "Jan")))
d.add_turn("anna", "Słyszę kroki. Ktoś jest za drzwiami.")
p = FictionEngine().generate(
    d, actor="jan", recipients=("anna",),
    instruction="Cel: strach=0,8; strategia: suspense",
)
print(p.text)
```

`actor` wybiera mówiącą postać. `recipients` wybiera adresatów. `instruction` opisuje cel tonu sceny. [Przykłady](../../examples/README.md) obejmują grupę, obrazy i model językowy.

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/quickstart.py` sprawdza także odtworzenie DSL. Wszystkie przykłady offline: `python3 examples/run_offline.py`; z Pillow: `python3 examples/run_offline.py --images`.

<!-- docs:section risks -->
## Ryzyka i następny krok

Python 3.10+; uruchomiono na 3.12.14. Wynik jest szkicem literackim. Szablony i punktacja nie gwarantują przeżycia czytelnika. Zewnętrzny model dołącz według [instrukcji LLM](LLM_CONNECTION.md).
