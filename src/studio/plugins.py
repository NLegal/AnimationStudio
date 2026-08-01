from __future__ import annotations
from dataclasses import dataclass, field

PLUGIN_CATEGORIES = [
    "image_model", "video_model", "music_model", "voice_model",
    "publishing_platform", "analytics_provider", "translation_engine",
    "storage_provider", "rendering_backend",
]


@dataclass
class Plugin:
    plugin_id: str = ""
    name: str = ""
    category: str = ""
    version: str = "1.0"
    status: str = "active"
    interface: dict = field(default_factory=dict)


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}

    def register(self, name: str, category: str, version: str = "1.0", interface: dict | None = None) -> Plugin | None:
        if category not in PLUGIN_CATEGORIES:
            return None
        plugin = Plugin(
            plugin_id=f"PLUGIN_{name}",
            name=name,
            category=category,
            version=version,
            status="active",
            interface=interface or {},
        )
        self._plugins[plugin.plugin_id] = plugin
        return plugin

    def get(self, plugin_id: str) -> Plugin:
        return self._plugins.get(plugin_id, Plugin())

    def by_category(self, category: str) -> list[Plugin]:
        return [p for p in self._plugins.values() if p.category == category]

    def replace(self, plugin_id: str, new_plugin_id: str) -> bool:
        if plugin_id not in self._plugins or new_plugin_id not in self._plugins:
            return False
        self._plugins[plugin_id].status = "inactive"
        self._plugins[new_plugin_id].status = "active"
        return True

    def disable(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if plugin is None:
            return False
        plugin.status = "inactive"
        return True

    def active(self) -> list[Plugin]:
        return [p for p in self._plugins.values() if p.status == "active"]

    def all_plugins(self) -> list[Plugin]:
        return list(self._plugins.values())

    def count(self) -> int:
        return len(self._plugins)

    def categories(self) -> list[str]:
        return list(PLUGIN_CATEGORIES)
