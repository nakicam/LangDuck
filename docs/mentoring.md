# Mentoring-Leitfaden

Lernprojekt: Ich schreibe den Code selbst, langsam und mit einfachen Mitteln. Der Mentor gibt
Gedankenanstöße und reviewt. Er schreibt keine Lösung, außer ich bitte ausdrücklich darum.

## Arbeitsweise

1. Eine Aufgabe (siehe [Projektplan](duckops-plan.md)) und eine Datei auswählen.
2. Gedankenanstoß lesen, selbst versuchen.
3. Test schreiben oder laufen lassen (`pytest`).
4. "Review" anfordern: Fragen, Risiken, Verbesserungsideen.
5. Erst überarbeiten, dann nächste Aufgabe.

Regel: Jede Zeile muss ich erklären können. Nichts einfügen, was ich nicht verstehe.

## Einstieg

Reihenfolge für den kleinen Anfang (vor MCP und REST):

| Schritt | Aufgabe | Datei | Leitfrage |
| --- | --- | --- | --- |
| 1 | LD-01 Verträge | `src/langduck/types.py` | Welche Daten ergänzt LangDuck zu den LangChain-Typen (Limits, Status, Quellen, Draft)? |
| 2 | LD-03 Tool | `src/langduck/tools.py` | Was passiert bei ungültigen Argumenten, und wie landen Quellen im Artifact? |
| 3 | LD-06 Fake-Modell und Schleife | `src/langduck/agents.py` | Woran erkenne ich, dass der Agent nicht endlos läuft? |
| 4 | LD-07 Grenzen | `src/langduck/guardrails.py` | Welche Grenze greift zuerst, und wie sieht der Fehler aus? |
| 5 | Erste Tests | `tests/test_agent.py` | Kann ich den kompletten Lauf ohne Modellschlüssel prüfen (LangChain-Fake-Chatmodell)? |

Danach: LD-02 Daten, LD-04 REST, LD-05 MCP, LD-08 echter Provider, LD-09 Evaluation.
Optional am Ende: dieselbe Demo mit LangGraph nachbauen und vergleichen.

## Review-Fragen (Dauerliste)

- Was passiert bei Fehler, Timeout, leerer Antwort?
- Ist das Verhalten ohne Modell testbar?
- Welche Annahme steckt im Code, und wo steht sie?
- Was würde ein Reviewer hier fragen?
