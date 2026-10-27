# edialog


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.4.4-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.24-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.6h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.2387 (9 commits)
- 👤 **Human dev:** ~$263 (2.6h @ $100/h, 30min dedup)

Generated on 2026-10-27 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

Biblioteka Python do generowania i oceny dialogów literackich: historia rozmowy, strategia, cel tonu emocjonalnego, opcjonalny obraz i odtwarzalny DSL. Wersja 0.4.0 zastępuje nazwę AffectDialog.

Domyślnie działa lokalnie na szablonach i regułach. Model LLM można dołączyć przez Ollama lub własny callback. Wagi są ilustracyjne; wynik tonu sceny nie jest prognozą emocji poszczególnych osób.

## Instalacja

Python 3.10+; po rozpakowaniu przejdź do katalogu projektu:

```bash
python3 -m pip install dist/edialog-0.4.0-py3-none-any.whl
python3 examples/quickstart.py
```

Z kodu źródłowego: `python3 -m pip install .`. Opcjonalna obsługa obrazów: `python3 -m pip install '.[images]'`. Nie zakładamy publikacji tego projektu w PyPI.

## Użycie

```python
from edialog import Dialogue, Participant, FictionEngine

d = Dialogue((Participant("anna", "Anna"), Participant("jan", "Jan")))
d.add_turn("anna", "Słyszę kroki. Ktoś jest za drzwiami.")
p = FictionEngine().generate(
    d, actor="jan", recipients=("anna",),
    instruction="Cel: strach=0,8; strategia: suspense",
)
print(p.text)
```

## Dokumentacja i przykłady

- [Dokumentacja](docs/README.md) — indeks instrukcji, funkcji, ograniczeń i decyzji.
- [Procesowy serwer MCP i potok URI](docs/FEATURE/MCP_PROCESS_PIPELINE.md) — 6-etapowy potok `proc://edialog/...`, `CompositeExecutionReceipt`, logi SHA-256 i reużycie przez `uri()`.
- [Manifest DockURI](dockuri.json) oraz [katalog błędów i runbooków](errors/README.md).
- [Przykłady](examples/README.md) — uruchamialne scenariusze offline i live.
- [Podłączenie LLM](docs/INFORMATION/LLM_CONNECTION.md) — model, transport i granice oceny.
- [Migracja nazwy](docs/REFACTORING/PROJECT_RENAME.md) — importy, wyjątki, CLI i zgodność DSL.
- [Changelog](CHANGELOG.md).

CLI: `edialog-mcp` dla serwera MCP i procesów URI (`proc://edialog/...`), `edialog-fiction` dla literatury, `edialog` dla wcześniejszego trybu wspierającego.

## Weryfikacja

```bash
python3 -m unittest discover -s tests -v
python3 examples/run_offline.py --images
python3 scripts/check_docs.py
```

Dokumentacja używa lokalnej adaptacji profilu kompaktowego [wellmanifest/docs](https://github.com/wellmanifest/docs). Zakres adaptacji i przypiętą rewizję opisuje [decyzja](docs/DECISION/DOCUMENTATION_PROFILE.md).


## License

Licensed under Apache-2.0.
