---
{
  "schema": "edialog.docs/document/v1",
  "id": "strategy-briefs",
  "kind": "information",
  "version": 1,
  "title": "Konkretny brief strategii dla LLM",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "479642698df4827c3f922a7c4c94823ea67ffead01d4f5d5954534e9750e74bd",
  "priority": "P2",
  "evidence": [
    "examples/llm_strategy.py",
    "examples/strategy_fixture.py",
    "src/edialog/fiction.py"
  ]
}
---

# Konkretny brief strategii dla LLM

<!-- docs:section summary -->
## Cel i rezultat

Nazwa strategii może być uzupełniona o fakty, perspektywę, relacje i operację narracyjną. To instrukcja autorska dla LLM; nie osobny model reakcji odbiorców.

<!-- docs:section details -->
## Zakres i rozwiązanie

W [przykładzie live](../../examples/llm_strategy.py) funkcja pośrednicząca dodaje `author_brief` do zadania generowania. Obejmuje on:

- fakty: Jan zna źródło kroków; pozostali go nie znają;
- relacje: Anna ufa Janowi, Piotr podejrzewa zatajenie informacji;
- strategię: przy `suspense` pozostaw jedną niejednoznaczność;
- formę: jeden polski wariant zdania wypowiadanego przez Jana.

```python
def complete(payload):
    enriched = dict(payload)
    if payload["task"] == "generate_fiction_candidates":
        enriched["author_brief"] = {
            "strategy": "Nawiąż do kroków i pozostaw jedną niejednoznaczność.",
            "form": "Jedno zdanie po polsku.",
        }
    return transport(enriched)
```

`transport` to skonfigurowany `OllamaJSON` albo własna funkcja modelu. Zainstaluj wrapper przez `CallableFictionBackend(complete)`. Wybrane strategie i cele nadal znajdują się w `payload["request"]`. Nie dopisuj faktów do historii jako wypowiedzi postaci tylko po to, by były instrukcjami modelu.

<!-- docs:section validation -->
## Weryfikacja

`examples/strategy_fixture.py` sprawdza przekazanie strategii i ocenę dwóch wariantów bez sieci. Przykład live wymaga osobnego uruchomienia; jego jakość nie została zmierzona.

<!-- docs:section risks -->
## Ryzyka i następny krok

Formę jednego zdania i zgodność z briefem trzeba ocenić autorsko. Punktacja nie sprawdza ich automatycznie. Kolejne fazy strategii realizuj przez osobne wywołania i `continue_scene`; kilka strategii w żądaniu nie oznacza wykonanej sekwencji.
