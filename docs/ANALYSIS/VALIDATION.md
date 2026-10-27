---
{
  "schema": "edialog.docs/document/v1",
  "id": "validation",
  "kind": "analysis",
  "version": 1,
  "title": "Weryfikacja wydania edialog 0.4",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "58af1ea0ba5b57009e39050849a22eb9a95b5fddbf11c11fc79333b16015023f",
  "priority": "P2",
  "evidence": [
    "tests/test_core.py",
    "tests/test_dialogue.py",
    "tests/test_fiction.py",
    "examples/run_offline.py",
    "scripts/check_docs.py"
  ]
}
---

# Weryfikacja wydania edialog 0.4

<!-- docs:section summary -->
## Cel i rezultat

Wydanie zachowuje zachowanie biblioteki po zmianie nazwy. Sprawdzane są testy, uruchamialne przykłady, dokumentacja i instalacja z wheel.

<!-- docs:section details -->
## Zakres i rozwiązanie

Zakres kontroli:

- 156 testów regresji: wcześniejszy silnik, NL, grupy, wagi, obrazy, DSL i adapter HTTP;
- 11 przykładów offline z opcjonalną ścieżką Pillow;
- instalacja wheel i import `edialog` poza katalogiem źródeł;
- entry pointy `edialog` i `edialog-fiction`;
- lokalny checker metadanych, limitów, indeksu, linków i migawki źródeł dokumentacji.

```bash
python3 -m unittest discover -s tests -v
python3 examples/run_offline.py --images
python3 scripts/check_docs.py
```

Środowisko sprawdzenia: Python 3.12.14, Pillow 12.3.0. JSON z końcowymi rezultatami znajduje się w katalogu artefaktów `results/` archiwum; nie jest kanoniczną dokumentacją ani dowodem publikacji CI.

<!-- docs:section validation -->
## Weryfikacja

Przed zapakowaniem wszystkie wymienione kontrole muszą zwrócić powodzenie. Osobne negatywne próby checkera obejmują uszkodzony link i brak sekcji. Log testów i raport przykładów zachowują rzeczywiste wyniki uruchomienia.

<!-- docs:section risks -->
## Ryzyka i następny krok

Nie sprawdzono każdego interpretera od 3.10 ani rzeczywistego LLM. Odpowiedzi HTTP w testach są kontrolowane. Sukces lokalnego checkera nie oznacza pełnej adopcji wellmanifest/docs w chronionym CI.
