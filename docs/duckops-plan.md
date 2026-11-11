# DuckOps Entenhausen – Projektplan für LangDuck

Stand: 11. November 2026. Status: Planung, keine implementierten Funktionen.
Tracking: [Epic #2](https://github.com/nakicam/LangDuck/issues/2).

## Ziel und Referenzdemo

LangDuck erhält einen eigenen kleinen Python-Agentenkern, inspiriert von der LangChain-Idee aus Modell, Tools und iterativer Ausführung. LangChain/LangGraph sind keine Voraussetzung des geplanten Kerns. Die fiktive Stadtwerke-Demo DuckOps bleibt vom Framework getrennt.

Referenzauftrag: **„Finde den erhöhten Wasserverbrauch im Entenbad, prüfe die offenen Störungen und erstelle einen begründeten Wartungsentwurf.“**

Der Agent liest Verbrauch über Datenbanktools, korreliert eine Störung über MCP und REST und liefert einen lokal erzeugten Entwurf mit Zahlen und Quellen. Er legt keinen echten Wartungsauftrag an.

## Architektur

```mermaid
flowchart TD
 A["CLI / Python API"] --> B["LangDuck Agent Runner"]
 B --> C["ModelAdapter: Fake / ein Provider"]
 B --> D["Registry, Validierung und Limits"]
 D --> E["Lokale Datenbanktools"]
 E --> F[("assets.db")]
 D --> G["MCP Client über stdio"]
 G --> H["Lokaler MCP Server"]
 H --> I["FastAPI auf localhost"]
 I --> J[("operations.db")]
 D --> K["Lokaler Wartungsentwurf"]
 B -.-> L["JSONL-Ereignisse und Evaluation"]
```

| Modul | MVP-Verantwortung |
| --- | --- |
| langduck.agents | Agentenkonfiguration und eigener Ausführungsloop |
| langduck.models | Providerunabhängiger Vertrag, Fake-Modell und ein echter Adapter |
| langduck.tools | ToolSpec, Registry, Schema-Prüfung und ToolResult |
| langduck.guardrails | Allowlist, Grenzen, Deadline und Eingabevalidierung |
| langduck.memory | Nachrichten und Toolergebnisse eines Laufs, nur im Speicher |
| langduck.observability | Strukturierte JSONL-Ereignisse |
| langduck.evaluation | Offline-Tests und getrennte fachliche Live-Evaluation |
| langduck.flows | Nach MVP, noch keine Umsetzung |

Vorgeschlagene Ablage: src/langduck/ für Frameworkcode, examples/duckops/ für Generator, Datenzugriff, API, MCP Server und CLI, tests/ für deterministische Tests, evals/duckops/ für Aufgaben und Ground Truth, docs/ für Architektur und Anleitung. Generierte Datenbanken und Logs gehören in ignorierte Laufzeitverzeichnisse.

## Verträge und Ausführungsregeln

- Agent arbeitet gegen eigene Typen: ModelAdapter, ToolSpec, ToolResult, RunConfig und RunResult.
- ToolSpec enthält Namen, Beschreibung, Eingabeschema und ausführbaren Adapter. Ergebnisse enthalten Daten, Quellen-IDs und einen definierten Fehlerstatus.
- ModelAdapter übersetzt Tool-Calling einschließlich Call-IDs; Providerobjekte bleiben im Adapter.
- RunResult enthält Antwort, Status, Schrittzahl, Fehler und vorhandene Nutzungsdaten.
- Status: completed, failed oder limit_reached. Mehrere Aufrufe pro Modellrunde werden sequenziell abgearbeitet.
- Standard: maximal 5 Modellrunden, 10 Toolaufrufe und 60 Sekunden Gesamtlaufzeit. I/O benötigt eigene Timeouts; blockierte Aufrufe müssen sauber beendet beziehungsweise ihre Prozesse geschlossen werden.
- Keine automatischen Retries im MVP. Fehlerbehandlung bleibt nachvollziehbar und innerhalb der Grenzen.
- MCP: ein lokaler Server, stdio, Initialisierung und Tool-Discovery; nur zwei explizit erlaubte Tools. Schemas werden validiert, Namen kollisionsfrei zugeordnet. Protokolldaten auf stdout, Diagnose auf stderr.
- Toolinhalte sind Daten und vergeben keine Berechtigungen. Die Allowlist ersetzt keine allgemeine Absicherung gegen alle Prompt-Injection-Angriffe.

## Datenmodell und Testdaten

Alle Daten sind synthetisch. Seed 42 und Referenzdatum 2026-11-01 sind festgelegt. Datenfenster: November 2025 bis Oktober 2026.

| Entität | Anzahl | Wesentliche Felder |
| --- | ---: | --- |
| Gebäude | 20 | id, name, type |
| Verbrauch | 720 | id, building_id, month, metric, value, unit |
| Dienstleister | 10 | id, name, trade |
| Wartungsauftrag | 100 | id, building_id, supplier_id, status, priority, due_date, description |
| Störung | 30 | id, building_id, status, reported_at, description |

720 Verbrauchswerte = 20 Gebäude × 12 Monate × 3 Metriken. Einheiten: Strom/Wärme in kWh, Wasser in m³. Assets und Verbrauch liegen in assets.db; Betriebsdaten in operations.db. Gemeinsame Gebäude-IDs werden vom Generator geprüft; es gibt keine datenbankübergreifenden Foreign Keys.

```mermaid
erDiagram
 BUILDING ||--o{ CONSUMPTION : besitzt
 BUILDING ||--o{ INCIDENT : betrifft
 BUILDING ||--o{ MAINTENANCE_ORDER : betrifft
 SUPPLIER ||--o{ MAINTENANCE_ORDER : betreut
```

Bewusst eingebaute Fälle:
1. Entenbad: Wasserverbrauch Oktober gegenüber September +80 %.
2. Offene Leckmeldung am selben Gebäude.
3. Überfälliger dringender Heizungsauftrag.
4. Zwei inhaltlich doppelte Wartungsaufträge.

Ein getrenntes Ground-Truth-Manifest beschreibt erwartete IDs und Werte; der Agent erhält keinen Zugriff darauf. Auch Beschreibungen mit irreführenden Anweisungen werden als Fehlerfall getestet.

## Tools und API

| Tool | Zugang | Wesentliche Eingaben | Ergebnis |
| --- | --- | --- | --- |
| list_buildings | SQLite read-only | optionale Namens-/Typfilter, limit | Gebäude mit IDs |
| get_consumption | SQLite read-only | Gebäude, Zeitraum, Metrik | Werte, Einheiten, Vormonatsvergleich und Quellen |
| list_maintenance_orders | MCP → REST | Gebäude, Status, Priorität, Pagination | Aufträge samt Dienstleister |
| list_incidents | MCP → REST | Gebäude, Status, Pagination | Störungsmeldungen |
| draft_maintenance_order | lokal | Gebäude, Titel, Priorität, Begründung, Quellen | validierter Entwurf ohne Persistenz |

FastAPI bietet GET /maintenance-orders, GET /incidents und GET /health. Nur localhost, nur lesende Geschäftsoperationen, begrenzte Antworten und klare Fehlerverträge. SQL ausschließlich parametrisiert und vordefiniert; keine freie SQL-Ausführung durch das Modell.

Vormonatsabweichungen berechnet das Datenbanktool deterministisch. Fehlende beziehungsweise nullwertige Vergleichsgrößen werden ausdrücklich gekennzeichnet.

## Ablauf der Referenzdemo

```mermaid
sequenceDiagram
 participant U as Nutzer
 participant L as LangDuck
 participant D as Datenbanktools
 participant M as MCP Server
 participant A as Wartungs-API
 U->>L: Wasserauffälligkeit und Wartungsentwurf
 L->>D: Gebäude und Verbrauch abrufen
 D-->>L: Entenbad +80 % mit Quellen
 L->>M: list_incidents / list_maintenance_orders
 M->>A: GET mit Gebäude-ID
 A-->>M: Offene Störung und Aufträge
 M-->>L: Ergebnisse mit Quellen
 Note over L: Entwurf lokal validieren, kein Auftrag wird angelegt
 L-->>U: Begründung, Quellen und Entwurf
```

## MVP-Abgrenzung

Enthalten: ein Agent, ein Fake-Modell, ein echter Modellprovider, vier lesende Tools und ein lokales Entwurfstool; SQLite, REST, ein MCP-Server über stdio; CLI, per-run Memory, strukturierte Ereignisse und Evaluation.

Später: Langfuse oder OpenTelemetry, zweiter Provider, PostgreSQL, persistenter Zustand, Freigaben und einfache Flows.

Nicht enthalten: Weboberfläche, Multi-Agent-System, freies SQL, MCP über mehrere Transporte, Benutzerverwaltung, Vektordatenbank, Deployment oder autonome externe Schreibaktionen.

## Priorisiertes Backlog

Alle verlinkten Aufgaben enthalten Checklisten, Abnahmekriterien und ein eigenes Mermaid-Diagramm. Prioritäten stehen im Titel und in der Beschreibung; Verantwortliche sind noch nicht zugewiesen.

| Aufgabe | Priorität | Inhalt | Stunden | Abhängigkeiten |
| --- | --- | --- | ---: | --- |
| [LD-01](https://github.com/nakicam/LangDuck/issues/3) | P0 | API-Verträge und Entenhausen-Abnahmefälle festlegen | 4 | – |
| [LD-02](https://github.com/nakicam/LangDuck/issues/4) | P0 | Synthetische Entenhausen-Daten reproduzierbar erzeugen | 5 | LD-01 |
| [LD-03](https://github.com/nakicam/LangDuck/issues/5) | P0 | Lesende SQLite-Tools für Gebäude und Verbrauch implementieren | 4 | LD-01, LD-02 |
| [LD-04](https://github.com/nakicam/LangDuck/issues/6) | P0 | FastAPI für Wartung und Störungen bereitstellen | 4 | LD-01, LD-02 |
| [LD-05](https://github.com/nakicam/LangDuck/issues/7) | P0 | Lokalen MCP Server und LangDuck-MCP-Adapter bauen | 6 | LD-01, LD-04 |
| [LD-06](https://github.com/nakicam/LangDuck/issues/8) | P0 | Eigenen Agentenloop mit Fake-Modell implementieren | 6 | LD-01, LD-03, LD-05 |
| [LD-07](https://github.com/nakicam/LangDuck/issues/9) | P0 | Ausführungsgrenzen und Tool-Berechtigungen durchsetzen | 5 | LD-06 |
| [LD-08](https://github.com/nakicam/LangDuck/issues/10) | P0 | Einen echten Modellprovider integrieren | 5 | LD-06, LD-07 |
| [LD-09](https://github.com/nakicam/LangDuck/issues/11) | P0 | Tracing, Evaluation und automatisierte Qualitätsprüfung einführen | 7 | LD-02, LD-07, LD-08 |
| [LD-10](https://github.com/nakicam/LangDuck/issues/12) | P0 | CLI, lokale Startanleitung und MVP-Abnahme fertigstellen | 4 | LD-09 |
| [LD-11](https://github.com/nakicam/LangDuck/issues/13) | P1 | Observability-Adapter für Langfuse oder OpenTelemetry ergänzen | offen | LD-09, LD-10 |
| [LD-12](https://github.com/nakicam/LangDuck/issues/14) | P1 | Zweiten Modellprovider und PostgreSQL-Adapter erproben | offen | LD-10 |
| [LD-13](https://github.com/nakicam/LangDuck/issues/15) | P2 | Freigaben, persistente Zustände und einfache Flows konzipieren | offen | LD-10 |

P0: **50 Stunden**, zusätzlich **4 Stunden Integrationsreserve** = **54 Stunden**. Planungskorridor 48–60 Stunden; etwa sieben Wochen bei acht Stunden/Woche, mit Puffer sechs bis acht Wochen. P1/P2 werden erst nach der MVP-Abnahme geschätzt.

## Etappen und Reihenfolge

| Etappe | Zeitbudget | Ergebnis |
| --- | ---: | --- |
| A: Verträge, Daten, DB-Tools | 13 h | Fachlich prüfbare Daten und lesende lokale Tools |
| B: REST und MCP | 10 h | API sowie unabhängig getestete MCP-Verbindung |
| C: Agentenkern und Grenzen | 11 h | Deterministischer Gesamtablauf mit Fake-Modell |
| D: Modell und Evaluation | 12 h | Echter Agentenlauf und Qualitätsbericht |
| E: CLI und Abnahme | 4 h + 4 h Reserve | Installation und Demo in frischer Umgebung |

```mermaid
flowchart TD
 A["LD-01 Verträge"] --> B["LD-02 Daten"]
 B --> C["LD-03 Datenbanktools"]
 B --> D["LD-04 REST API"]
 D --> E["LD-05 MCP"]
 C --> F["LD-06 Agentenkern"]
 E --> F
 F --> G["LD-07 Grenzen"]
 G --> H["LD-08 Modellprovider"]
 H --> I["LD-09 Evaluation"]
 I --> J["LD-10 Demo-Abnahme"]
```

## Qualität und Definition of Done

- Frische Installation und Offline-Demo funktionieren ohne Modellschlüssel.
- Referenzdemo verbindet direkten Datenbankzugriff und echte lokale MCP-Kommunikation.
- Mindestens 8 von 10 festgelegten fachlichen Live-Fällen bestehen.
- Zahlen, fachliche Belegbarkeit und Gültigkeit der Quellen-IDs werden getrennt geprüft.
- Alle deterministischen Grenz- und Fehlerfälle bestehen: Loop, Toolanzahl, Deadline, Timeouts, unbekanntes Tool, ungültige Parameter, MCP-Ausfall und Zustandsisolation.
- JSONL enthält Run-ID, Call-ID, Dauer, Status und Fehlercode; pro Run genau ein Abschlussereignis.
- Prompts und vollständige Toolinhalte sind standardmäßig nicht im Log; Geheimnisse niemals.
- Offline-Prüfungen sind für CI geeignet; Live-Evaluation bleibt explizit und berichtet Modell-ID, Datum und Datensatzversion.
- Entwürfe erzeugen keine Aufträge. Bekannte Grenzen werden dokumentiert.
- SDK-Versionen werden bei der Umsetzung anhand offizieller Dokumentation geprüft und per Lockdatei festgehalten.

## Risiken und Entscheidungen

| Risiko | Entscheidung |
| --- | --- |
| Scope wächst zum vollständigen Framework | P0 konsequent begrenzen; P1/P2 separat |
| Tool-Calling unterscheidet sich je Provider | Eigene Typen, Fake-Antworten und Adaptertests |
| MCP-Schemas oder Prozesslebenszyklus verursachen Fehler | Nur zwei erlaubte Tools, ein Transport und frühe Integrationstests |
| Modell erfindet Werte oder Quellen | Berechnungen in Tools; Ground Truth und Belegprüfung |
| Abbruch wartet nur statt Operation zu stoppen | I/O-Timeouts, Deadlines und Prozessbereinigung testen |
| Demo wirkt bereits produktionsreif | Synthetische lokale Demo klar benennen; kein Auth-/Deployment-Versprechen |

## Nächste Schritte

1. LD-01: Verträge und zehn fachliche Aufgaben festlegen.
2. LD-02: Generator mit festen IDs und Ground Truth bauen.
3. LD-03/04: Datenbanktools und API unabhängig vom Agenten testen.
4. LD-05: MCP-Verbindung unabhängig validieren.
5. LD-06: ersten Fake-Durchlauf über Datenbank und MCP ausführen.

Technische Führung: Architektur, API-Entscheidungen und Abnahme durch den Projektverantwortlichen. Keine Beteiligung oder Verfügbarkeit weiterer Personen vorausgesetzt. Die Issues enthalten noch keine Zusage zu einem Kalenderstart.
