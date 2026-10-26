# edialog

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
- [Przykłady](examples/README.md) — uruchamialne scenariusze offline i live.
- [Podłączenie LLM](docs/INFORMATION/LLM_CONNECTION.md) — model, transport i granice oceny.
- [Migracja nazwy](docs/REFACTORING/PROJECT_RENAME.md) — importy, wyjątki, CLI i zgodność DSL.
- [Changelog](CHANGELOG.md).

CLI: `edialog-fiction` dla literatury, `edialog` dla wcześniejszego trybu wspierającego.

## Weryfikacja

```bash
python3 -m unittest discover -s tests -v
python3 examples/run_offline.py --images
python3 scripts/check_docs.py
```

Dokumentacja używa lokalnej adaptacji profilu kompaktowego [wellmanifest/docs](https://github.com/wellmanifest/docs). Zakres adaptacji i przypiętą rewizję opisuje [decyzja](docs/DECISION/DOCUMENTATION_PROFILE.md).
