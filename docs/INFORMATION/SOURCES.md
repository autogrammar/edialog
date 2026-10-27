---
{
  "schema": "edialog.docs/document/v1",
  "id": "sources",
  "kind": "information",
  "version": 1,
  "title": "Źródła projektu i granice inspiracji",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "5e398dda0c6813a90271c3767636fc17da533316945b0775bd82974aa708f2fa",
  "priority": "P2",
  "evidence": [
    "docs/profile.json",
    "src/edialog/data/lexicon.json"
  ]
}
---

# Źródła projektu i granice inspiracji

<!-- docs:section summary -->
## Cel i rezultat

Źródła opisują inspiracje i interfejsy. Autorskie współczynniki edialog nie dziedziczą wyników walidacji innych projektów.

<!-- docs:section details -->
## Zakres i rozwiązanie

- [wellmanifest/docs](https://github.com/wellmanifest/docs) — układ dokumentacji i profil kompaktowy; dokładny pin oraz digest w [profile.json](../profile.json).
- [emotions, PyPI](https://pypi.org/project/emotions/) — nazwy siedmiu etykiet i ich kody. W edialog kody są identyfikatorami, nie skalą do uśredniania.
- [VADER, Hutto i Gilbert, 2014](https://ojs.aaai.org/index.php/ICWSM/article/view/14550) — przykład połączenia leksykonu z regułami językowymi. Nie kopiowano kodu ani wag VADER.
- [NRC Emotion Lexicon](https://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm) — przykład skojarzeń słów z wieloma kategoriami. Nie dołączono jego danych ani tłumaczeń.
- [Mohammad, Best Practices, 2023](https://aclanthology.org/2023.findings-eacl.136/) — rozdzielanie skojarzeń słów od wniosków o ludziach.
- [Pillow Image](https://pillow.readthedocs.io/en/stable/reference/Image.html) — dekodowanie i limity obrazów.
- [Ollama chat](https://docs.ollama.com/api/chat), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [vision](https://docs.ollama.com/capabilities/vision) — transport modelu i schematy odpowiedzi.

Wagi tekstu, palety, akumulacji i sygnałów sceny są ilustracyjne. `h-cited` jest umowną etykietą radosnego podekscytowania.

<!-- docs:section validation -->
## Weryfikacja

Repozytorium standardu odczytano z przypiętej rewizji. Interfejsy modelu sprawdzono względem dokumentacji i testów kontrolowanego transportu. Słownik zawiera jawne pole pochodzenia danych.

<!-- docs:section risks -->
## Ryzyka i następny krok

Nie wykonano empirycznej walidacji reakcji czytelników. Dodanie zewnętrznego leksykonu wymaga osobnego sprawdzenia licencji i jakości. Nowe źródła powinny wskazywać zakres faktycznie użytych danych lub metod.
