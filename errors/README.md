# Katalog błędów i runbooków diagnostycznych (`edialog`)

Zgodnie ze standardem `wellmanifest/logs`, katalog `errors/` opisuje kody błędów domenowych oraz procedury naprawcze dla potoku procesowego i serwera MCP `edialog`.

## Indeks kodów błędów

| Kod błędu | Klasa wyjątku | Proces URI | Opis i runbook |
| :--- | :--- | :--- | :--- |
| [`EDIALOG-VALIDATION-001`](EDIALOG-VALIDATION-001.md) | `ValidationError` / `NeedsClarification` | `proc://edialog/nl/parse/v1`, `proc://edialog/affect/score/v1` | Błąd walidacji kontraktu wejściowego, nieznana strategia lub niejednoznaczna instrukcja NL. |
| [`EDIALOG-BACKEND-001`](EDIALOG-BACKEND-001.md) | `BackendError` | `proc://edialog/candidates/generate/v1` | Błąd komunikacji lub schematu JSON z transportem LLM (`SubLLMJSON`, `OllamaJSON`). |
| [`EDIALOG-MCP-001`](EDIALOG-MCP-001.md) | `ValidationError` | `proc://edialog/pipeline/run/v1` | Brak dopasowanej procedury URI (`NO_MATCHING_PROCEDURE`) lub nieznane narzędzie MCP. |
