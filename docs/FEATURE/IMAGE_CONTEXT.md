---
{
  "schema": "edialog.docs/document/v1",
  "id": "image-context",
  "kind": "feature",
  "version": 1,
  "title": "Obraz jako kontekst atmosfery sceny",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "86c18b79f14d7d74dbdcab58dbe17b7722d42d8ab594a2cd4bd49c7efe7128eb",
  "priority": "P2",
  "evidence": [
    "src/edialog/vision.py",
    "examples/image_context.py"
  ]
}
---

# Obraz jako kontekst atmosfery sceny

<!-- docs:section summary -->
## Cel i rezultat

Obraz może dostarczyć cech palety lub sygnałów semantycznych z modelu wizyjnego. Wynik wpływa na ocenę bieżącego kroku dialogu.

<!-- docs:section details -->
## Zakres i rozwiązanie

Zainstaluj opcjonalną zależność z katalogu projektu:

```bash
python3 -m pip install '.[images]'
python3 examples/image_context.py
```

Domyślny plik jest syntetyczną próbką koloru, nie sceną literacką. `analyze_image` mierzy jasność, kontrast, nasycenie i ciepło. Umowne, słabe skojarzenia palety można wyłączyć przez `pixel_heuristics=False`.

```python
from edialog import analyze_image, CallableVisionBackend, OllamaJSON

visual = analyze_image(
    "scena.png",
    backend=CallableVisionBackend(OllamaJSON("TWOJ_MODEL_WIZYJNY")),
)
```

Model otrzymuje rzeczywiste piksele PNG i zwraca opis oraz sygnały `threat`, `loss`, `conflict`, `reunion`, `celebration`, `anticipation`, `quiet`. W `engine.generate(...)` przekaż `image=visual`. Obsługiwane są PNG/JPEG/WebP, pierwsza klatka, do 10 MiB i 16 mln pikseli; przezroczystość jest składana na bieli.

<!-- docs:section validation -->
## Weryfikacja

Testy używają rzeczywistego dekodera Pillow, obejmują przezroczystość, uszkodzony plik, limit pikseli i wpływ obrazu na replay. Callback wizyjny sprawdzono z kontrolowaną odpowiedzią, bez rzeczywistego modelu.

<!-- docs:section risks -->
## Ryzyka i następny krok

Ciemny obraz nie dowodzi grozy. Model nie przypisuje emocji ani cech osobom na podstawie twarzy. `continue_scene` zachowuje tekst, nie obraz; dla stałej ilustracji przekaż ją ponownie. Do serwera trafiają piksele, dlatego wybierz właściwy endpoint.
