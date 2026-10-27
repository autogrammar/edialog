---
{
  "schema": "edialog.docs/document/v1",
  "id": "cli-commands",
  "kind": "information",
  "version": 1,
  "title": "Polecenia edialog i edialog-fiction",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "4018be11ee81ac0a84d4d7c6e88da0d6d22af0d256d70e9ee86911c977c30b49",
  "priority": "P2",
  "evidence": [
    "src/edialog/cli.py",
    "src/edialog/fiction_cli.py"
  ]
}
---

# Polecenia edialog i edialog-fiction

<!-- docs:section summary -->
## Cel i rezultat

Dostępne są dwa polecenia: `edialog-fiction` dla literatury i `edialog` dla wcześniejszego trybu wspierającego. Polecenia pracują na lokalnym JSON.

<!-- docs:section details -->
## Zakres i rozwiązanie

Uruchamiaj z rozpakowanego katalogu projektu po instalacji:

```bash
edialog-fiction map
edialog-fiction analyze --text "Słyszę kroki." --history examples/threat_history.json
edialog-fiction generate examples/fiction_scene.json --actor jan --to anna piotr \
  --instruction "Cel: strach=0,85; strategia: suspense" --out result.json --dsl-out plan.json
edialog-fiction replay examples/fiction_scene.json --plan plan.json
edialog-fiction timeline examples/fiction_scene.json --actor jan --to anna piotr
edialog-fiction image examples/palette_fixture.png --features-only
edialog-fiction evaluate examples/ratings.synthetic.json
edialog strategies
```

Odpowiedniki modułowe: `python3 -m edialog.fiction_cli` i `python3 -m edialog`. `generate` przyjmuje alternatywnie `--request`, a tryb literacki również `--candidates`, `--image` i `--lexicon`. Wszystkie te argumenty wskazują lokalne pliki. CLI nie konfiguruje LLM; użyj [API lub przykładu](LLM_CONNECTION.md).

<!-- docs:section validation -->
## Weryfikacja

Testy CLI sprawdzają generowanie i replay. Po instalacji sprawdzane są również rzeczywiste entry pointy `edialog` oraz `edialog-fiction`, nie tylko uruchomienie modułu.

<!-- docs:section risks -->
## Ryzyka i następny krok

Kod 0 oznacza wykonanie programu. Osiągnięcie celu modelu odczytaj z `target_met_in_model`; w starym trybie z `simulations` i `checks_passed`. Pliki podane przez `--out` są zapisywane, dlatego wybieraj ścieżkę świadomie.
