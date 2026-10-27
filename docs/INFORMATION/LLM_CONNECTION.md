---
{
  "schema": "edialog.docs/document/v1",
  "id": "llm-connection",
  "kind": "information",
  "version": 1,
  "title": "Podłączenie modelu LLM",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "479642698df4827c3f922a7c4c94823ea67ffead01d4f5d5954534e9750e74bd",
  "priority": "P2",
  "evidence": [
    "src/edialog/backends.py",
    "examples/llm_strategy.py",
    "examples/ollama_fiction.py"
  ]
}
---

# Podłączenie modelu LLM

<!-- docs:section summary -->
## Cel i rezultat

Domyślnie edialog działa bez LLM. Opcjonalny model interpretuje swobodne polecenia i generuje warianty; końcowa punktacja pozostaje leksykalna.

<!-- docs:section details -->
## Zakres i rozwiązanie

Ollama musi już działać, a model musi być pobrany. `ollama ls` pokazuje modele. `ollama serve` uruchamia serwer, jeśli nie jest aktywny.

```python
from edialog import OllamaJSON, CallableFictionBackend, FictionEngine

transport = OllamaJSON("NAZWA_ZAINSTALOWANEGO_MODELU", timeout=120)
engine = FictionEngine(backend=CallableFictionBackend(transport))
```

`NAZWA_ZAINSTALOWANEGO_MODELU` jest instrukcją do zastąpienia, nie domyślnym modelem. Transport używa `http://localhost:11434/api/chat`, `stream=false` i schematu JSON w `format`. Nie pobiera wag ani nie uruchamia serwera.

Przykład z argumentem modelu i konkretną strategią:

```bash
python3 examples/llm_strategy.py --model TWOJ_MODEL --strategy suspense
```

Własny dostawca może implementować synchroniczne `complete(payload: dict) -> dict`. Zadania: `parse_fiction_request` i `generate_fiction_candidates`. Schemat wyniku jest w `payload["response_schema"]`. Dodatkowy kontekst autorski pokazuje [opis briefów](STRATEGY_BRIEFS.md).

<!-- docs:section validation -->
## Weryfikacja

Offline `examples/strategy_fixture.py` testuje kontrakt callbacku. Testy transportu przechwytują HTTP i sprawdzają JSON oraz błędy. Nie uruchomiono prawdziwego LLM; uruchomienie przykładu live wymaga własnego modelu.

<!-- docs:section risks -->
## Ryzyka i następny krok

Adapter przekazuje dane do wskazanego serwera. Domyślnie jest to localhost. Wybór innego serwera zmienia odbiorcę danych. Schemat JSON nie gwarantuje sensu, spójności fabuły ani jakości prozy. Brak zależności od konkretnego dostawcy umożliwia zastąpienie transportu.
