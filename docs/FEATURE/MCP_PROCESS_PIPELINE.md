---
{
  "schema": "edialog.docs/document/v1",
  "id": "mcp-process-pipeline",
  "kind": "feature",
  "version": 1,
  "title": "Procesowy serwer MCP, potok URI i raporty wykonania",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-27",
  "source_digest": "b0efc20fcab2658f4547bde8a613575c63cc4a5ddf7866de2de3c48ffde45b49",
  "priority": "P1",
  "evidence": [
    "src/edialog/pipeline.py",
    "src/edialog/mcp.py",
    "dockuri.json",
    "dockuri.yaml",
    "uriprocess.json",
    "policies/edialog-trust-boundaries.policy",
    "standard/edialog-pipeline.lifecycle",
    "examples/mcp_process_pipeline.py",
    "tests/test_mcp_pipeline.py"
  ]
}
---

# Procesowy serwer MCP, potok URI i raporty wykonania

<!-- docs:section summary -->
## Cel i rezultat

Moduły `edialog.pipeline` i `edialog.mcp` udostępniają 6-etapowy potok procesowy (`proc://edialog/...`), serwer MCP (`edialog-mcp`) oraz kontrakt `uri()`. Każde wywołanie zwraca pełny ślad wykonanych procesów, tabelę punktacji kandydatów, kwit `CompositeExecutionReceipt`, łańcuch logów i snippety reużycia.

<!-- docs:section details -->
## Zakres i rozwiązanie

Potok dzieli generowanie i ocenę kwestii na 6 adresowalnych procesów URI zadeklarowanych w `dockuri.json` (`dockuri/workflow-v1`):

1. `proc://edialog/nl/parse/v1` — tłumaczy instrukcję NL, poziom zaufania (`trust_level`: `zero`, `low`, `high`, `rebuilding`) i `author_brief` na `FictionRequest` oraz kanoniczny Action URI.
2. `proc://edialog/context/filter/v1` — filtruje kwestie widoczne dla mówiącego i adresatów oraz oblicza bazowy wektor `reader_proxy`.
3. `proc://edialog/candidates/generate/v1` — pobiera kandydatów z szablonów deterministycznych, `SubLLMJSON` lub `OllamaJSON`.
4. `proc://edialog/affect/score/v1` — ocenia afekt każdego kandydata i szereguje warianty według `rank_loss`.
5. `proc://edialog/dsl/compile/v1` — kompiluje plan `affect-fiction 0.3` i weryfikuje deterministyczny `replay()`.
6. `proc://edialog/report/emit/v1` — emituje `CompositeExecutionReceipt`, łańcuch logów SHA-256 i raport z gotowymi wywołaniami `uri()`.

```python
from edialog import uri

res = uri("proc://edialog/pipeline/run/v1", {
    "dialogue": dialogue.to_dict(),
    "actor": "tomasz",
    "recipients": ["klaudia"],
    "trust_level": "low",
})
print(res["proposal"]["text"], res["receipt"]["receipt_id"])
```

Serwer `EDialogMCPServer` (`edialog-mcp serve`) obsługuje narzędzia `registry_search`, `task_plan`, `task_execute`, `task_status`, `edialog_pipeline_run`, `edialog_uri_call` i `edialog_explain_architecture`.

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/mcp_process_pipeline.py` prezentuje odkrywanie procesów, planowanie DAG, ślad 6 kroków, tabelę rankingu i snippety reużycia. Testy jednostkowe znajdują się w `tests/test_mcp_pipeline.py`.

<!-- docs:section risks -->
## Ryzyka i następny krok

Kwit `CompositeExecutionReceipt` potwierdza determinizm obliczeń i spójność skrótów SHA-256 poszczególnych etapów, ale nie zastępuje oceny literackiej tekstu wygenerowanego przez zewnętrzny model LLM.
