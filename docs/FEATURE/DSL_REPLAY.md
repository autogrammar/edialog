---
{
  "schema": "edialog.docs/document/v1",
  "id": "dsl-replay",
  "kind": "feature",
  "version": 1,
  "title": "Odtwarzanie planu i kontynuacja sceny",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "db31b877f2b96dde1ce458e11207ea989f3500c55ffe960370ef141f04a942bc",
  "priority": "P2",
  "evidence": [
    "src/edialog/fiction.py",
    "docs/fiction.schema.json",
    "examples/dsl_roundtrip.py"
  ]
}
---

# Odtwarzanie planu i kontynuacja sceny

<!-- docs:section summary -->
## Cel i rezultat

DSL przechowuje plan, kandydatów i migawkę modelu, aby odtworzyć wynik bez kolejnego wywołania LLM. Kontynuacja tworzy nową kopię dialogu.

<!-- docs:section details -->
## Zakres i rozwiązanie

```python
replayed = engine.replay(proposal.dsl, dialogue)
assert replayed.to_dict() == proposal.to_dict()
continued = engine.continue_scene(dialogue, proposal)
```

Pełny [przykład](../../examples/dsl_roundtrip.py) można uruchomić z `--out plan.json`. Plan `affect-fiction` 0.3 zawiera cel, strategie, hash historii, widoczne kwestie, pełny słownik, parametry i pulę kandydatów. Obraz jest zapisany jako migawka analizy i hash źródła, bez pikseli base64.

Replay waliduje zakres i historię, odtwarza parametry, a następnie ponownie ocenia teksty. Nie ufa zewnętrznej tabeli wyników. Zmiana historii unieważnia plan. Dopisana kwestia ma `kind="synthetic"`; nie jest reakcją zaobserwowaną u człowieka.

[JSON Schema](../fiction.schema.json) opisuje strukturę. Walidacja Python dodatkowo sprawdza tożsamości, zakres widoczności i aktualność historii. Po zmianie nazwy pakietu zachowano identyfikatory wcześniejszych DSL.

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/dsl_roundtrip.py` sprawdza równość replay i brak mutacji oryginału. Testy obejmują migawkę niestandardowego słownika, obraz, nieaktualny plan i nieznane odwołania.

<!-- docs:section risks -->
## Ryzyka i następny krok

DSL nie jest podpisany kryptograficznie. Jego świadoma edycja tworzy nowy wariant modelu. Wyniki LLM mogą różnić się między generacjami; deterministyczne jest odtworzenie zapisanej puli. Nie zmieniaj nazwy języka planu podczas migracji importów.
