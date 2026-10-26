---
{
  "schema": "edialog.docs/document/v1",
  "id": "contextual-emotion-weights",
  "kind": "feature",
  "version": 1,
  "title": "Wagi emocji zależne od słów i kontekstu",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "8ab58943e2919955b804983a73c79b315795ee03d4e886df632464bbac4481b7",
  "priority": "P2",
  "evidence": [
    "src/edialog/affect.py",
    "src/edialog/data/lexicon.json",
    "examples/context_weights.py"
  ]
}
---

# Wagi emocji zależne od słów i kontekstu

<!-- docs:section summary -->
## Cel i rezultat

Analizator przypisuje siedem niezależnych wag tekstowi i pokazuje źródła każdego wkładu. Kody kategorii nie są skalą liczbową do uśredniania.

<!-- docs:section details -->
## Zakres i rozwiązanie

| Etykieta | Kod |
|---|---:|
| scared | 0 |
| sad | 2 |
| angry | 4 |
| nothing | 5 |
| happy | 6 |
| h-cited | 7 |
| excited | 8 |

Każde natężenie jest osobną wartością 0–1. Wagi mogą współwystępować; suma nie musi wynosić 1. `nothing` oznacza jawne sygnały neutralnego tonu; brak dopasowania daje `unknown`.

Słownik zawiera 138 autorskich haseł PL/EN i 18 reguł kontekstowych. Efektywny wkład zmieniają prosta negacja, intensyfikatory, kontrast, wielkie litery i wykrzykniki. Kontekst obejmuje do czterech poprzednich kwestii z wygaszaniem.

```python
from edialog import TextEmotionAnalyzer
r = TextEmotionAnalyzer().analyze("Słyszę kroki.", history=["Ktoś nas śledzi."])
print(r.scores)
print(r.evidence)
```

`EmotionLexicon.with_weights(...)` tworzy nowy słownik. [Przykład motywu](../../examples/custom_lexicon.py) nadaje czerwonej wstążce autorskie znaczenie.

<!-- docs:section validation -->
## Weryfikacja

Testy sprawdzają odmienne wyniki słowa „kroki” po zagrożeniu i po powitaniu, działanie negacji oraz malejący wkład powtórzeń. `examples/context_weights.py` wypisuje pełne dowody.

<!-- docs:section risks -->
## Ryzyka i następny krok

Wagi są ilustracyjne, nie wyuczone. Słownik nie obejmuje całej fleksji, ironii ani metafor. Nie uczy się automatycznie z wygenerowanego tekstu. Strojenie wymaga niezależnych danych; szczegóły w [ograniczeniach](../ANALYSIS/MODEL_LIMITATIONS.md).
