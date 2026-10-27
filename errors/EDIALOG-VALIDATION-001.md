# EDIALOG-VALIDATION-001: Błąd walidacji wejścia lub niejednoznaczna instrukcja NL

## Przyczyna
Proces `proc://edialog/nl/parse/v1` lub walidator modelu otrzymał niepoprawny wektor emocji (wartości poza zakresem `0.0..1.0`), więcej niż 3 strategie narracyjne, nieznany poziom `trust_level` lub swobodną instrukcję NL bez włączonego presetu zaufania bądź backendu LLM.

## Diagnostyka
1. Sprawdź podsumowanie wejścia w kroku `step1_nl_parse`.
2. Zweryfikuj dozwolone kody emocji (`scared`, `sad`, `angry`, `nothing`, `happy`, `h-cited`, `excited`) oraz strategie (`suspense`, `loss`, `confrontation`, `reunion`, `celebration`, `anticipation`, `quiet`, `release`).
3. Jeśli używasz poziomu zaufania, upewnij się, że `trust_level` należy do `{"zero", "low", "high", "rebuilding"}`.

## Rozwiązanie
Podaj ustrukturyzowany format `Cel: neutralnosc=0,65; ekscytacja=0,35; strategia: quiet, anticipation`, ustaw `trust_level="low"` lub włącz backend `backend="subllm"`.
