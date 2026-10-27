---
{
  "schema": "edialog.docs/document/v1",
  "id": "fiction-dialogues",
  "kind": "feature",
  "version": 1,
  "title": "Generowanie i ranking dialogów literackich",
  "status": "implemented",
  "owner": "edialog",
  "scope": "project",
  "updated": "2026-10-26",
  "source_digest": "2f23943f0ba9f5c5c73de6b5f45f398973a52591ee5f1d84a40e93c7b37ab438",
  "priority": "P2",
  "evidence": [
    "src/edialog/fiction.py",
    "examples/fiction_demo.py"
  ]
}
---

# Generowanie i ranking dialogów literackich

<!-- docs:section summary -->
## Cel i rezultat

Silnik tworzy warianty kolejnej kwestii i porównuje ich ton z celem autora. Przyjmuje historię 2–50 postaci oraz opcjonalny obraz.

<!-- docs:section details -->
## Zakres i rozwiązanie

`FictionRequest` przyjmuje cel, strategię albo oba naraz. Dostępne strategie: `suspense`, `loss`, `confrontation`, `reunion`, `celebration`, `anticipation`, `quiet`, `release`. Przykładowe NL: `Cel: strach=0,85; strategia: suspense`.

```python
from edialog import FictionRequest

request = FictionRequest({"scared": 0.8, "sad": 0.3}, ("suspense", "loss"))
p = engine.generate(dialogue, actor="jan", recipients=("anna",), request=request)
print(p.text)
print(p.candidates[0]["distance"])
```

`engine` i `dialogue` utwórz jak w [quickstart](../INFORMATION/QUICKSTART.md). Możesz podać `candidates=[...]`, aby ocenić własne warianty. Bez modelu silnik korzysta z szablonów i krótkiego cytatu wcześniejszej kwestii; z LLM otrzymuje pulę wygenerowanych odpowiedzi.

Ranking uwzględnia rzeczywiste słowa kandydatów, wcześniejszy kontekst, akumulację i karę za powtarzanie fraz. `target_met_in_model` sprawdza tolerancję celu. Zapis DSL umożliwia [replay](DSL_REPLAY.md).

<!-- docs:section validation -->
## Weryfikacja

`python3 examples/fiction_demo.py` pokazuje różne konteksty, ranking i rozładowanie napięcia. Testy potwierdzają, że dwa różne teksty mogą uzyskać inne wyniki przy tej samej strategii.

<!-- docs:section risks -->
## Ryzyka i następny krok

Punktacja leksykalna nie mierzy jakości literackiej. Cytat w szablonie również wpływa na wynik. Cel może pozostać niespełniony. Zachowano semantykę wcześniejszego DSL; rename pakietu nie zmienia danych planu.
