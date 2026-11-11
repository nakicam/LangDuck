"""Verträge von LangDuck (LD-01), aufgebaut auf langchain-core.

Nachrichten, Toolaufrufe, Tools und Chatmodelle kommen direkt aus LangChain
(AIMessage, ToolMessage, BaseTool, BaseChatModel). Diese Datei ergänzt nur, was LangChain
nicht mitbringt: Lauf-Grenzen, Status, Fehlerklassifikation, Quellen und den Wartungsentwurf.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.messages.ai import UsageMetadata
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Frozen(BaseModel):
    """Basis der LangDuck-Verträge: unveränderlich, unbekannte Felder werden abgelehnt."""

    model_config = ConfigDict(frozen=True, extra="forbid")


# --- Fehler und Quellen -------------------------------------------------------------------


class ErrorCode(StrEnum):
    """Fehlercodes für Toolaufrufe und Modellantworten."""
    UNKNOWN_TOOL = "unknown_tool"
    TOOL_NOT_ALLOWED = "tool_not_allowed"
    INVALID_ARGUMENTS = "invalid_arguments"
    TOOL_FAILED = "tool_failed"
    TIMEOUT = "timeout"
    EMPTY_RESPONSE = "empty_response"
    MODEL_ERROR = "model_error"
    PROTOCOL_ERROR = "protocol_error"


class RunError(Frozen):
    """Repräsentiert einen Fehler während eines Laufs."""
    code: ErrorCode
    message: str
    # recoverable: der Loop darf mit dem Fehler als Toolergebnis weiterlaufen; sonst fatal -> failed.
    recoverable: bool


class SourceRef(Frozen):
    """Verweis auf einen Datensatz, der aus genau einem Toolaufruf stammt."""

    call_id: str  # entspricht ToolMessage.tool_call_id
    source_id: str  # z. B. die Verbrauchs-ID aus assets.db


class ToolArtifact(Frozen):
    """Maschinenlesbarer Teil eines Toolergebnisses.

    Wird mit response_format="content_and_artifact" als ToolMessage.artifact transportiert;
    der Text in ToolMessage.content geht ans Modell, das Artifact nicht.
    """

    sources: tuple[SourceRef, ...] = ()
    error: RunError | None = None


# --- Antwort des Modells ------------------------------------------------------------------


def is_empty_response(msg: AIMessage) -> bool:
    """Prüft, ob die Antwort des Modells leer ist."""
    # Weder Text noch Toolaufrufe: der Runner bricht mit failed ab.
    return not msg.text.strip() and not msg.tool_calls


def is_final_response(msg: AIMessage) -> bool:
    """Prüft, ob die Antwort des Modells final ist (kein Toolaufruf und Text vorhanden)."""
    # Bei gemischter Antwort haben die Toolaufrufe Vorrang; der Text ist noch nicht final.
    return not msg.tool_calls and bool(msg.text.strip())


# --- Lauf ---------------------------------------------------------------------------------


class RunStatus(StrEnum):
    """Status eines Laufs."""
    # completed meint reguläres Laufende, nicht fachliche Richtigkeit.
    COMPLETED = "completed"
    FAILED = "failed"
    LIMIT_REACHED = "limit_reached"


class RunConfig(Frozen):
    """Konfiguration für einen Lauf."""
    max_model_calls: int = Field(default=5, gt=0)
    max_tool_calls: int = Field(default=10, gt=0)
    deadline_seconds: float = Field(default=60.0, gt=0)


class MaintenanceDraft(Frozen):
    """Lokaler Entwurf; wird nie als Wartungsauftrag gespeichert."""

    building_id: str
    title: str
    priority: str
    rationale: str
    source_ids: tuple[str, ...] = Field(min_length=1)
    draft: Literal[True] = True

    @field_validator("building_id", "title", "priority", "rationale")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        """Lehnt leere und nur aus Leerraum bestehende Texte ab."""
        if not value.strip():
            raise ValueError("darf nicht leer sein")
        return value


class RunResult(Frozen):
    """Ergebnis eines Laufs."""
    status: RunStatus
    answer: str = ""
    steps: int = 0
    error: RunError | None = None
    usage: UsageMetadata | None = None
    # Letzter validierter Entwurf; getrennt von status, da Erfolg fachlich bewertet wird.
    draft: MaintenanceDraft | None = None
    messages: Sequence[BaseMessage] = ()
