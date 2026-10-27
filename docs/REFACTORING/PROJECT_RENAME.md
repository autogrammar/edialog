---
{
  "schema": "edialog.docs/document/v1",
  "id": "project-rename",
  "kind": "refactoring-plan",
  "version": 1,
  "title": "Migracja nazwy AffectDialog do edialog",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "db31b877f2b96dde1ce458e11207ea989f3500c55ffe960370ef141f04a942bc",
  "priority": "P2",
  "evidence": [
    "pyproject.toml",
    "src/edialog/__init__.py",
    "src/edialog/errors.py"
  ]
}
---

# Migracja nazwy AffectDialog do edialog

<!-- docs:section summary -->
## Cel i rezultat

Projekt i dystrybucja Python nazywają się edialog od wersji 0.4.0. Zmieniono importy, polecenia, zasoby pakietu, testy i przykłady.

<!-- docs:section details -->
## Zakres i rozwiązanie

| Poprzednio | Teraz |
|---|---|
| `pip install` lokalnego wheel affectdialog | lokalny wheel `edialog-0.4.0-py3-none-any.whl` |
| `import affectdialog` | `import edialog` |
| `from affectdialog import ...` | `from edialog import ...` |
| `AffectDialogError` | `EDialogError` |
| `affectdialog` CLI | `edialog` CLI |
| `affectfiction` CLI | `edialog-fiction` CLI |

Najpierw zainstaluj nowy wheel, potem zmień importy i uruchom własne testy. Publiczne klasy, takie jak `FictionEngine` i `Dialogue`, zachowują nazwy oraz zachowanie. Nie dodano pakietu aliasowego `affectdialog`.

Formaty danych pozostają: `affect-fiction` 0.3, `affect-dialogue` 0.2 i AffectScript 0.1. Nie wykonuj globalnej podmiany słowa „affect” w zapisanych planach. Stare ścieżki dokumentów zachowują nagłówki i odsyłają do kanonicznych stron.

<!-- docs:section validation -->
## Weryfikacja

156 testów wykonano na importach `edialog`. Dodatkowo sprawdzana jest instalacja wheel, dostęp do leksykonu jako zasobu pakietu, nowe entry pointy i 11 przykładów offline.

<!-- docs:section risks -->
## Ryzyka i następny krok

Zmiana importu jest zmianą niezgodną wstecz. W razie regresji użyj wcześniejszego archiwum oraz poprzednich importów. Nie publikowano projektu do PyPI ani nie tworzono zdalnego repozytorium. Warunkiem zakończenia migracji u użytkownika są jego własne testy integracyjne.
