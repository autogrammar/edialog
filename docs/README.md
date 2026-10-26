# Dokumentacja edialog

Dokumenty mają stabilne ścieżki i opisują jeden temat. Metadane stosują [lokalną adaptację profilu](DECISION/DOCUMENTATION_PROFILE.md) na bazie wellmanifest/docs.

## Instrukcje i kontrakty

- [Pierwszy dialog w edialog](INFORMATION/QUICKSTART.md) — `quickstart`.
- [Publiczne API Python](INFORMATION/PYTHON_API.md) — `python-api`.
- [Polecenia edialog i edialog-fiction](INFORMATION/CLI_COMMANDS.md) — `cli-commands`.
- [Podłączenie modelu LLM](INFORMATION/LLM_CONNECTION.md) — `llm-connection`.
- [Konkretny brief strategii dla LLM](INFORMATION/STRATEGY_BRIEFS.md) — `strategy-briefs`.
- [Adresaci, relacje i granice celu emocjonalnego](INFORMATION/RELATIONSHIP_SCOPE.md) — `relationship-scope`.
- [Matematyka punktacji tonu sceny](INFORMATION/SCORING_MODEL.md) — `scoring-model`.
- [Wcześniejszy tryb wspierającego dialogu](INFORMATION/SUPPORTIVE_DIALOGUES.md) — `supportive-dialogues`.
- [Źródła projektu i granice inspiracji](INFORMATION/SOURCES.md) — `sources`.

## Funkcje

- [Generowanie i ranking dialogów literackich](FEATURE/FICTION_DIALOGUES.md) — `fiction-dialogues`.
- [Wagi emocji zależne od słów i kontekstu](FEATURE/CONTEXTUAL_EMOTION_WEIGHTS.md) — `contextual-emotion-weights`.
- [Obraz jako kontekst atmosfery sceny](FEATURE/IMAGE_CONTEXT.md) — `image-context`.
- [Odtwarzanie planu i kontynuacja sceny](FEATURE/DSL_REPLAY.md) — `dsl-replay`.

## Analiza i weryfikacja

- [Co można wnioskować z wyniku modelu](ANALYSIS/MODEL_LIMITATIONS.md) — `model-limitations`.
- [Weryfikacja wydania edialog 0.4](ANALYSIS/VALIDATION.md) — `validation`.

## Decyzje

- [Lokalny profil dokumentacji na bazie wellmanifest/docs](DECISION/DOCUMENTATION_PROFILE.md) — `documentation-profile`.

## Migracja

- [Migracja nazwy AffectDialog do edialog](REFACTORING/PROJECT_RENAME.md) — `project-rename`.

## Schematy i przykłady

- [Katalog przykładów](../examples/README.md) — offline, obrazy i opt-in LLM.
- [Schemat planu literackiego](fiction.schema.json) — affect-fiction 0.3.
- [Schemat żądania](request.schema.json) i [odpowiedzi](reply.schema.json) — wcześniejszy tryb wspierający.
- [Mapa emocji](emotion_map.json) — kody oraz semantyka natężeń.
- [Profil dokumentacji](profile.json) — przypięcie standardu, zakres lokalnej adaptacji.
- [Changelog](../CHANGELOG.md) — krótki skutek zmian.
