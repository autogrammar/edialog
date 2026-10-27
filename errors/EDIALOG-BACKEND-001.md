# EDIALOG-BACKEND-001: Błąd transportu lub schematu odpowiedzi LLM

## Przyczyna
Proces `proc://edialog/candidates/generate/v1` wywołał transport `SubLLMJSON` (`subactor/subllm`) lub `OllamaJSON`, ale model zwrócił niepoprawny JSON, pominął pole `candidates` lub przypisał nieistniejące identyfikatory `evidence_turn_ids`.

## Diagnostyka
1. Sprawdź konfigurację providera `subllm` lub dostępność lokalnego serwera Ollama (`http://127.0.0.1:11434`).
2. Zweryfikuj listę widocznych kwestii z kroku `step2_context_filter` (`visible_context.turns`).

## Rozwiązanie
Użyj trybu deterministycznego (`backend="offline"`) do szybkiej weryfikacji potoku lub upewnij się, że środowisko `subllm` posiada poprawne poświadczenia i model obsługujący `response_schema`.
