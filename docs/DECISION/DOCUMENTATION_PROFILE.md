---
{
  "schema": "edialog.docs/document/v1",
  "id": "documentation-profile",
  "kind": "decision",
  "version": 1,
  "title": "Lokalny profil dokumentacji na bazie wellmanifest/docs",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "b0efc20fcab2658f4547bde8a613575c63cc4a5ddf7866de2de3c48ffde45b49",
  "priority": "P2",
  "evidence": [
    "docs/profile.json",
    "scripts/check_docs.py",
    "https://github.com/wellmanifest/docs/tree/f4cb34926d7369d74b0a1fe09e896a35b72c016c"
  ]
}
---

# Lokalny profil dokumentacji na bazie wellmanifest/docs

<!-- docs:section summary -->
## Cel i rezultat

Projekt przyjmuje układ i limity profilu kompaktowego wellmanifest/docs. Jest to jawna lokalna adaptacja dla pakietu źródłowego bez potwierdzonej tożsamości repozytorium GitHub.

<!-- docs:section details -->
## Zakres i rozwiązanie

Punkt odniesienia to pełna rewizja wskazana w [profile.json](../profile.json), wraz z SHA-256 `policy.json`. Zachowano stabilne identyfikatory, katalogi rodzajów, nazwy UPPER_SNAKE_CASE, indeks oraz sekcje `summary`, `details`, `validation`, `risks`. Limit całego dokumentu: 120 linii, 600 słów, 12288 bajtów.

Nie wymyślamy `org/repo`, zdalnego origin ani dowodu wdrożenia CI. Dlatego metadane mają własny schemat `edialog.docs/document/v1`, `owner: edialog`, `scope: project` i `source_digest` rzeczywistej migawki kodu. To zastępuje wymagania upstream dotyczące właściciela repozytorium i pełnego SHA badanego commitu. Oryginalny checker jest napisany dla tej adaptacji i nie jest checkerem upstream.

Decyzja pozwala dostarczyć użyteczną dokumentację teraz, zachowując możliwość późniejszej formalnej adopcji. Nie kopiujemy infrastruktury governance ani instrukcji agentów z repozytorium wzorcowego.

<!-- docs:section validation -->
## Weryfikacja

`python3 scripts/check_docs.py` sprawdza lokalny profil bez sieci i wykonywania kodu z dokumentów. Powiązanie źródłowe to digest plików kodu, testów, skryptów i przykładów; źródła standardu są przypięte osobno.

<!-- docs:section risks -->
## Ryzyka i następny krok

Pełna adopcja wymaga potwierdzonego repozytorium, przypięcia standardu przez właściwy proces, śledzenia plików w Git i wdrożenia bramy CI. Nie deklarujemy tych etapów jako wykonanych. Opiekun przyszłego repozytorium powinien jawnie przenieść profil; formaty danych emocjonalnych nie zależą od tej decyzji.
