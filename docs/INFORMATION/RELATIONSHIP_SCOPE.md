---
{
  "schema": "edialog.docs/document/v1",
  "id": "relationship-scope",
  "kind": "information",
  "version": 1,
  "title": "Adresaci, relacje i granice celu emocjonalnego",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "86c18b79f14d7d74dbdcab58dbe17b7722d42d8ab594a2cd4bd49c7efe7128eb",
  "priority": "P2",
  "evidence": [
    "src/edialog/fiction.py",
    "src/edialog/nl.py",
    "examples/group_dialogue.py"
  ]
}
---

# Adresaci, relacje i granice celu emocjonalnego

<!-- docs:section summary -->
## Cel i rezultat

Adresaci określają kontekst wypowiedzi. Cel liczbowy w `FictionRequest` dotyczy tonu sceny, a nie niezależnej prognozy dla każdej osoby.

<!-- docs:section details -->
## Zakres i rozwiązanie

| Pojęcie | Znaczenie |
|---|---|
| `actor` | Postać wypowiadająca kolejną kwestię |
| `recipients` | Osoby, do których kierowana jest kwestia |
| `target` | Docelowy wektor `reader_proxy` dla widocznej sceny |
| `character_expression_proxies` | Analiza języka własnych wypowiedzi postaci |
| Relacje z briefu | Autorski opis przekazywany LLM |

Pusta lista adresatów zapisanej kwestii oznacza wypowiedź publiczną. Prywatna kwestia może być kontekstem kolejnej odpowiedzi tylko wtedy, gdy widzą ją autor i wszyscy nowi adresaci.

`recipients=("anna",)` wybiera jedną osobę; `("anna", "piotr")` grupę. Nie oznacza to modelowania dwóch osobnych reakcji. Wersja 0.4 nie ma kierunkowego stanu zaufania, różnic wiedzy ani oddzielnych celów emocjonalnych postaci. LLM może dostać takie informacje w [briefie](STRATEGY_BRIEFS.md), ale ranking ich osobno nie waliduje.

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/group_dialogue.py` potwierdza, że prywatna kwestia Anny nie trafia do kontekstu odpowiedzi dla Anny i Piotra. Testy sprawdzają także kontekst przekazany callbackowi.

<!-- docs:section risks -->
## Ryzyka i następny krok

Nie utożsamiaj tonu słów z przeżyciem postaci lub człowieka. Rozbudowa o cele jednostkowe wymaga nowego kontraktu i walidacji; nie wystarczy dodatkowy identyfikator w `recipients`. Obecne ograniczenie jest jawne, bez zmiany istniejących danych.
