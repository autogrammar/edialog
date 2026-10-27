# Przykłady edialog

Najpierw zainstaluj projekt według [quickstart](../docs/INFORMATION/QUICKSTART.md). Polecenia poniżej uruchamiaj z katalogu projektu. Wszystkie pliki importują `edialog`.

## Offline

| Plik | Co pokazuje | Dodatkowe wymagania |
|---|---|---|
| [quickstart.py](quickstart.py) | Najmniejszy dialog i replay | brak |
| [context_weights.py](context_weights.py) | Te same słowa w różnych kontekstach | brak |
| [group_dialogue.py](group_dialogue.py) | Jedna osoba, grupa i widoczność prywatnej kwestii | brak |
| [custom_lexicon.py](custom_lexicon.py) | Jawne wagi własnego motywu | brak |
| [dsl_roundtrip.py](dsl_roundtrip.py) | Zapis planu, replay i kopia sceny | brak |
| [reader_evaluation.py](reader_evaluation.py) | MAE na danych syntetycznych | brak |
| [strategy_fixture.py](strategy_fixture.py) | Kontrakt callbacku na stałych wariantach | brak |
| [fiction_demo.py](fiction_demo.py) | Pełniejszy scenariusz literacki | brak |
| [demo.py](demo.py) | Wcześniejszy model wspierającego dialogu | brak |
| [backend_fixture.py](backend_fixture.py) | Wcześniejszy adapter JSON | brak |
| [image_context.py](image_context.py) | Piksele, atmosfera i kontekst obrazu | Pillow |

```bash
python3 examples/run_offline.py
python3 examples/run_offline.py --images
python3 examples/dsl_roundtrip.py --out plan.json
```

Runner wykonuje dziesięć przykładów bez obrazów lub jedenaście z `--images`. Nie wywołuje LLM ani sieci. Błąd któregokolwiek przykładu daje niezerowy kod wyjścia.

## LLM i wizja — jawne uruchomienie

| Plik | Co pokazuje |
|---|---|
| [subllm_dialogue.py](subllm_dialogue.py) | Integracja z `subactor/subllm` (SubLLM routing, klucze i modele) |
| [romance_street_scenarios.py](romance_street_scenarios.py) | Spotkanie uliczne: 20-letni chłopak vs 40-letni mężczyzna zagadujący 25-letnią kobietę |
| [aloof_street_scenarios.py](aloof_street_scenarios.py) | Strategia obojętności, emocjonalnej niejednoznaczności i budowania napięcia (`suspense`) |
| [four_turns_dialogues.py](four_turns_dialogues.py) | 4 pełne kolejki dialogowe z dynamiczną reakcją kobiety na chłodny dystans mężczyzny |
| [llm_strategy.py](llm_strategy.py) | Ollama, fakty autorskie, relacje i konkretny brief strategii |
| [ollama_fiction.py](ollama_fiction.py) | Swobodne NL i opcjonalny obraz |
| [image_context.py](image_context.py) z `--model` | Model wizyjny zamiast samej analizy palety |

```bash
python3 examples/subllm_dialogue.py
python3 examples/romance_street_scenarios.py
python3 examples/aloof_street_scenarios.py
python3 examples/four_turns_dialogues.py
python3 examples/llm_strategy.py --model TWOJ_MODEL --strategy suspense
python3 examples/ollama_fiction.py --model TWOJ_MODEL
python3 examples/image_context.py --image scena.png --model TWOJ_MODEL_WIZYJNY
```

Zastąp nazwy modeli rzeczywistymi nazwami z lokalnej Ollama. Te polecenia wymagają uruchomionego serwera i pobranych wag. Przykład obrazowy wymaga modelu obsługującego wizję. Nie zostały wykonane z rzeczywistym modelem w ramach weryfikacji wydania.

## Dane

- [fiction_scene.json](fiction_scene.json) i [threat_history.json](threat_history.json) — sceny fikcyjne dla CLI.
- [ratings.synthetic.json](ratings.synthetic.json) — wymyślone oceny do demonstracji metryki.
- [palette_fixture.png](palette_fixture.png) — syntetyczna próbka koloru; nie ma treści sceny.
- [dialogue.json](dialogue.json) i [request.json](request.json) — wcześniejszy tryb wspierający.

Opis zakresu adresatów i ograniczeń: [relacje i cele](../docs/INFORMATION/RELATIONSHIP_SCOPE.md). Żaden przykład nie wysyła wiadomości do uczestników dialogu.
