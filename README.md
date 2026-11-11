# LangDuck
<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/d5915671-cc1b-4095-a54b-2db84612410b" />

**Make your agents quack.**

LangDuck ist das Konzept für ein leichtgewichtiges Python-Framework, mit dem sich KI-Agenten erstellen, kombinieren, evaluieren und überwachen lassen. Der Schwerpunkt liegt auf sicheren Anwendungen rund um Daten und GovTech.

## Ziel und Zielgruppe

LangDuck richtet sich an Entwicklerinnen und Entwickler sowie Teams, die Agenten nicht nur einzeln prototypisieren, sondern als nachvollziehbare und überprüfbare Anwendungen aufbauen möchten. Das Konzept verbindet wiederverwendbare Werkzeuge und komponierbare Abläufe mit dem Anspruch, Berechtigungen, Zustand und Qualität von Anfang an mitzudenken.

## Leitprinzipien

- **Leichtgewichtig:** Agenten sollen sich ohne unnötige Komplexität erstellen und zusammensetzen lassen.
- **Sicherheitsbewusst:** Berechtigungen, Eingabevalidierung und Freigaben sind als eigene Aufgaben vorgesehen.
- **Komponierbar:** Wiederverwendbare Tools und Flows sollen den Aufbau größerer Abläufe aus klar abgegrenzten Teilen ermöglichen.
- **Überprüfbar:** Evaluation und Beobachtbarkeit sollen helfen, Verhalten und Qualität von Agenten nachvollziehbar zu machen.
- **Geeignet für sensible Datenanwendungen:** Sicherheit und Governance sind besonders für Data- und GovTech-Szenarien relevant.

## Geplante Module

Die folgende Übersicht beschreibt das angestrebte Konzept, nicht den Nachweis bereits verfügbarer Funktionen.

| Modul | Vorgesehene Aufgabe |
| --- | --- |
| `langduck.agents` | Agenten erstellen und konfigurieren |
| `langduck.tools` | Wiederverwendbare Werkzeuge für beispielsweise Datenbanken und APIs bereitstellen |
| `langduck.guardrails` | Berechtigungen, Eingabevalidierung und Freigaben behandeln |
| `langduck.memory` | Kontext und persistenten Zustand verwalten |
| `langduck.observability` | Anbindungen an OpenTelemetry und Langfuse ermöglichen |
| `langduck.evaluation` | Automatisierte Tests und Qualitätsmessungen unterstützen |
| `langduck.flows` | Mehrere Agenten zu Workflows kombinieren |

## Projektstatus und Umfang

LangDuck ist derzeit ein Framework-Konzept. Die Modulnamen und Aufgaben skizzieren eine mögliche Architektur; sie sind keine Aussage darüber, dass diese Module, APIs oder Integrationen bereits implementiert oder einsatzbereit sind. Dieses Repository dokumentiert aktuell die Projektidee. Installationsanleitungen, Nutzungsbeispiele und Aussagen zu Releases oder Stabilität folgen erst, wenn es eine entsprechende Implementierung gibt.

## DuckOps Entenhausen: erster Framework-Prototyp

Die konkrete Planung verwendet vollständig synthetische Stadtwerkedaten: Gebäude, Verbrauch, Wartungsaufträge und Störungen. Sie verbindet direkte SQLite-Tools, eine REST API und einen lokalen MCP Server mit dem geplanten LangDuck-Agentenkern.

- [Projektplan, Architektur und Diagramme](docs/duckops-plan.md)
- [Epic und priorisierte Aufgaben](https://github.com/nakicam/LangDuck/issues/2)

Status: Planung; die beschriebenen Funktionen sind noch nicht implementiert.
