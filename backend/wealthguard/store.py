"""In-memory demo state and append-only audit trail."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from typing import Any

from .models import AuditEvent, UserProfile


class SessionStore:
    def __init__(self) -> None:
        self._profiles: dict[str, UserProfile] = {}
        self._audit: list[AuditEvent] = []
        self._lock = RLock()

    def profile(self, session_id: str) -> UserProfile:
        with self._lock:
            return self._profiles.get(session_id, UserProfile()).model_copy(deep=True)

    def update_profile(
        self, session_id: str, incoming: UserProfile | None
    ) -> tuple[UserProfile, dict[str, dict[str, Any]]]:
        with self._lock:
            previous = self._profiles.get(session_id, UserProfile())
            if incoming is None:
                return previous.model_copy(deep=True), {}
            changes: dict[str, dict[str, Any]] = {}
            update = incoming.model_dump(
                exclude={"current_task", "missing_information", "confidence", "last_updated_at"}
            )
            merged = previous.model_dump()
            for field, value in update.items():
                if value != merged.get(field):
                    changes[field] = {"from": merged.get(field), "to": value}
                    merged[field] = value
            merged["last_updated_at"] = datetime.now(UTC)
            result = UserProfile(**merged)
            self._profiles[session_id] = result
            return result.model_copy(deep=True), deepcopy(changes)

    def save_profile(self, session_id: str, profile: UserProfile) -> UserProfile:
        with self._lock:
            saved = profile.model_copy(update={"last_updated_at": datetime.now(UTC)}, deep=True)
            self._profiles[session_id] = saved
            return saved.model_copy(deep=True)

    def reset_profile(self, session_id: str) -> UserProfile:
        with self._lock:
            profile = UserProfile()
            self._profiles[session_id] = profile
            return profile.model_copy(deep=True)

    def append_audit(self, event: AuditEvent) -> None:
        with self._lock:
            self._audit.append(event)

    def audit(self, session_id: str | None = None, limit: int = 100) -> list[AuditEvent]:
        with self._lock:
            events = self._audit
            if session_id:
                events = [event for event in events if event.session_id == session_id]
            return [event.model_copy(deep=True) for event in reversed(events[-limit:])]
