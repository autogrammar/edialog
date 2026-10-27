# EDIALOG-MCP-001: Nieznany adres procesu URI (`NO_MATCHING_PROCEDURE`)

## Przyczyna
Wywołano `uri('<adres>', payload)` lub narzędzie MCP `edialog_uri_call` z adresem URI, który nie znajduje się w `PROCESS_CATALOG` ani na liście aliasów w `dockuri.json`.

## Diagnostyka
Uruchom `edialog-mcp registry` lub wywołaj narzędzie MCP `registry_search` z pustym zapytaniem `{"query": ""}`, aby wylistować wszystkie zarejestrowane procedury `proc://edialog/...`.

## Rozwiązanie
Zastąp błędny adres jednym z kanonicznych URI, np. `proc://edialog/pipeline/run/v1` lub `proc://edialog/affect/score/v1`.
