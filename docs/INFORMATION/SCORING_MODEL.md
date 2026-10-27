---
{
  "schema": "edialog.docs/document/v1",
  "id": "scoring-model",
  "kind": "information",
  "version": 1,
  "title": "Matematyka punktacji tonu sceny",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "58af1ea0ba5b57009e39050849a22eb9a95b5fddbf11c11fc79333b16015023f",
  "priority": "P2",
  "evidence": [
    "src/edialog/affect.py",
    "src/edialog/fiction.py",
    "src/edialog/vision.py"
  ]
}
---

# Matematyka punktacji tonu sceny

<!-- docs:section summary -->
## Cel i rezultat

Punktacja jest jawnym modelem heurystycznym. Oddziela sygnał aktualnego tekstu od akumulowanego tonu sceny i celu autora.

<!-- docs:section details -->
## Zakres i rozwiązanie

Dla kategorii `e` wkłady słów są sumowane po zastosowaniu modyfikatorów:

```text
text[e] = 1 - exp(-sum(contributions[e]))
fused[e] = 1 - (1-text[e]) * (1-image_weight*image[e])
next[e] = retention*previous[e] + (1-retention*previous[e])*fused[e]
```

Domyślnie `retention=0.55`, `image_weight=0.35`. Bez obrazu `fused=text`. Brak sygnału powoduje modelowe wygaszanie; nie dowodzi zaniku emocji człowieka.

Kontekst dla reguł słownych bierze maksimum wyników ostatnich czterech kwestii, z mnożnikiem `0.75 ** age`. Te kwestie są oceniane bez rekurencyjnego kontekstu. Powtarzanie pojedynczego hasła ma malejący wkład.

Dla jawnie zadanych wymiarów:

```text
distance = mean(abs(next[e] - target[e]))
rank_loss = distance + 0.15 * repeated_fourgram_fraction
```

Wygrywa najniższy wynik. Domyślna tolerancja wynosi 0.15 dla każdego celu. Wymiary pominięte przez autora nie są karane. `reader_proxy` jest wynikiem widocznej sceny, a `character_expression_proxies` dotyczą własnych słów każdej postaci.

<!-- docs:section validation -->
## Weryfikacja

Testy potwierdzają zakres 0–1, kontekstowe zmiany, akumulację i różne rankingi wariantów. Odtwarzanie DSL kontroluje powtarzalność obliczeń. Parametry nie były kalibrowane na czytelnikach.

<!-- docs:section risks -->
## Ryzyka i następny krok

Wynik nie jest prawdopodobieństwem ani miarą jakości prozy. Dobór słów kluczowych może zawyżyć ocenę. Przed interpretacją jako prognozy przeżycia potrzebna jest walidacja na innych scenach i czytelnikach.
