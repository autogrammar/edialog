---
{
  "schema": "edialog.docs/document/v1",
  "id": "model-limitations",
  "kind": "analysis",
  "version": 1,
  "title": "Co można wnioskować z wyniku modelu",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "58af1ea0ba5b57009e39050849a22eb9a95b5fddbf11c11fc79333b16015023f",
  "priority": "P2",
  "evidence": [
    "src/edialog/affect.py",
    "src/edialog/fiction.py",
    "examples/reader_evaluation.py"
  ]
}
---

# Co można wnioskować z wyniku modelu

<!-- docs:section summary -->
## Cel i rezultat

Wagi opisują założenia modelu tekstu i obrazu. Nie przeprowadzono badania potwierdzającego wywoływanie określonych emocji u czytelników.

<!-- docs:section details -->
## Zakres i rozwiązanie

Fakty techniczne: analiza ma mały, jawny leksykon; reguły uwzględniają uproszczony kontekst; DSL pozwala powtórzyć obliczenia. Dostarczenie LLM rozszerza generowanie, ale nie zmienia automatycznie jakości punktacji.

Hipotezą wymagającą danych jest związek `reader_proxy` z przeżyciem konkretnej osoby. Brakuje modelu ironii, pełnej fleksji, koreferencji, wiarygodności postaci i kierunkowych relacji. Cytowane lub negowane słowa mogą być interpretowane niedokładnie. Punktacja nie sprawdza fabuły ani zgodności stylu.

Walidacja na czytelnikach powinna oddzielać strojenie od oceny według scen i osób. Zbieraj oceny konkretnych fragmentów oraz rozrzut odpowiedzi. Porównuj analizę bez kontekstu, z kontekstem i z obrazem. `evaluate_annotations` oblicza MAE; brakujące kategorie są pomijane, nie zamieniane na zera.

Przykład [reader_evaluation.py](../../examples/reader_evaluation.py) korzysta wyłącznie z danych syntetycznych.

<!-- docs:section validation -->
## Weryfikacja

Testy weryfikują obliczenie metryki i obsługę brakujących wymiarów. Nie stanowią walidacji psychologicznej. Nie dostarczono ocen rzeczywistych czytelników ani pomiaru skuteczności LLM.

<!-- docs:section risks -->
## Ryzyka i następny krok

Nie używaj własnych przewidywań jako etykiet prawdy. Strojenie na tym samym zbiorze, na którym raportujesz błąd, zawyży ocenę. Odpowiedzialność za wybór próby i kryterium literackiego pozostaje po stronie autora badania.
