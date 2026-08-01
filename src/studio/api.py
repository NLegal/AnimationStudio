from __future__ import annotations
from datetime import datetime

API_DOMAINS = [
    "studio", "creative", "production", "rendering",
    "publishing", "analytics", "automation", "administration",
]

METHODS = ["get", "post", "put", "patch", "delete"]


class StudioAPI:
    def __init__(self):
        self._routes: dict[tuple[str, str], str] = {}
        self._calls: dict[str, int] = {}
        self._responses: dict[str, dict] = {}

    def register_route(self, domain: str, endpoint: str, handler: str, method: str = "get") -> bool:
        if domain not in API_DOMAINS or method not in METHODS:
            return False
        self._routes[(method, f"/{domain}{endpoint}")] = handler
        return True

    def call(self, method: str, endpoint: str, **params) -> dict:
        key = (method.lower(), endpoint)
        handler = self._routes.get(key)
        self._calls[key[1]] = self._calls.get(key[1], 0) + 1
        if handler is None:
            return {"ok": False, "error": "route_not_found", "handler": ""}
        return {"ok": True, "handler": handler, "params": params}

    def call_count(self, endpoint: str) -> int:
        return self._calls.get(endpoint, 0)

    def routes(self) -> list[str]:
        return [f"{method.upper()} {endpoint}" for (method, endpoint) in self._routes]

    def routes_for_domain(self, domain: str) -> list[str]:
        return [f"{method.upper()} {endpoint}"
                for (method, endpoint) in self._routes
                if endpoint.startswith(f"/{domain}/")]

    def endpoint_exists(self, method: str, endpoint: str) -> bool:
        return (method.lower(), endpoint) in self._routes

    def count(self) -> int:
        return len(self._routes)

    def expose(self, domain: str, prefix: str = "") -> dict:
        return {
            "domain": domain,
            "base_path": f"/api/{domain}",
            "endpoints": self.routes_for_domain(domain),
            "registered_at": datetime.now().isoformat(),
        }
