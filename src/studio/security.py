from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

ASSET_CATEGORIES = [
    "assets", "characters", "datasets", "prompts", "models",
    "credentials", "publishing_accounts", "finances",
]

ACCESS_LEVELS = ["viewer", "editor", "admin"]


@dataclass
class AuditEvent:
    event_id: str = ""
    actor: str = ""
    action: str = ""
    resource: str = ""
    result: str = ""
    details: str = ""
    timestamp: str = ""


class AccessControl:
    def __init__(self):
        self._roles: dict[str, str] = {}
        self._permissions: dict[str, dict[str, bool]] = {}

    def assign_role(self, user: str, role: str) -> None:
        self._roles[user] = role

    def role_of(self, user: str) -> str:
        return self._roles.get(user, "")

    def grant(self, role: str, resource: str, allowed: bool = True) -> None:
        self._permissions.setdefault(role, {})[resource] = allowed

    def can_access(self, user: str, resource: str) -> bool:
        role = self.role_of(user)
        if not role:
            return False
        return self._permissions.get(role, {}).get(resource, False)

    def allowed_resources(self, user: str) -> list[str]:
        role = self.role_of(user)
        perms = self._permissions.get(role, {})
        return [r for r, allowed in perms.items() if allowed]


class AuditLog:
    def __init__(self):
        self._events: list[AuditEvent] = []
        self._counter = 0

    def log(self, actor: str, action: str, resource: str, result: str, details: str = "") -> AuditEvent:
        self._counter += 1
        event = AuditEvent(
            event_id=f"AUDIT_{self._counter}",
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            details=details,
            timestamp=datetime.now().isoformat(),
        )
        self._events.append(event)
        return event

    def events_for(self, actor: str) -> list[AuditEvent]:
        return [e for e in self._events if e.actor == actor]

    def events_on(self, resource: str) -> list[AuditEvent]:
        return [e for e in self._events if e.resource == resource]

    def all_events(self) -> list[AuditEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)


class SecurityManager:
    def __init__(self):
        self.access = AccessControl()
        self.audit = AuditLog()
        self._secrets: dict[str, str] = {}
        for category in ASSET_CATEGORIES:
            self.access.grant("admin", category)

    def protect(self, actor: str, resource: str, action: str, details: str = "") -> bool:
        allowed = self.access.can_access(actor, resource)
        self.audit.log(actor, action, resource, "allowed" if allowed else "denied", details)
        return allowed

    def store_secret(self, key: str, value: str, actor: str) -> None:
        self._secrets[key] = value
        self.audit.log(actor, "store_secret", "credentials", "allowed")

    def get_secret(self, key: str, actor: str) -> str:
        allowed = self.protect(actor, "credentials", "read_secret")
        if not allowed:
            return ""
        return self._secrets.get(key, "")

    def list_categories(self) -> list[str]:
        return list(ASSET_CATEGORIES)
