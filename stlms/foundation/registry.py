"""
ST-LMS v3 — Foundation Registry
Foundation Core — Phase 1

Central registry for all layers, components, workers, artifacts.
"""

from typing import Any

class FoundationRegistry:
    def __init__(self):
        self._layers: dict = {}
        self._components: dict = {}
        self._workers: dict = {}
        self._artifacts: dict = {}
        self._schemas: dict = {}
        self._validators: dict = {}

    def register_layer(self, name: str, info: dict) -> None:
        self._layers[name] = info

    def register_component(self, name: str, info: dict) -> None:
        self._components[name] = info

    def register_worker(self, name: str, info: dict) -> None:
        self._workers[name] = info

    def register_artifact(self, name: str, info: dict) -> None:
        self._artifacts[name] = info

    def register_schema(self, name: str, info: dict) -> None:
        self._schemas[name] = info

    def register_validator(self, name: str, info: dict) -> None:
        self._validators[name] = info

    def get_layer(self, name: str) -> dict:
        return self._layers.get(name, {})

    def get_component(self, name: str) -> dict:
        return self._components.get(name, {})

    def list_layers(self) -> list[str]:
        return sorted(self._layers.keys())

    def list_components(self) -> list[str]:
        return sorted(self._components.keys())

    def list_workers(self) -> list[str]:
        return sorted(self._workers.keys())

    def layer_count(self) -> int:
        return len(self._layers)

    def component_count(self) -> int:
        return len(self._components)

    def worker_count(self) -> int:
        return len(self._workers)

    def artifact_count(self) -> int:
        return len(self._artifacts)

    def summary(self) -> dict:
        return {
            "layers": self.layer_count(),
            "components": self.component_count(),
            "workers": self.worker_count(),
            "artifacts": self.artifact_count(),
            "schemas": len(self._schemas),
            "validators": len(self._validators),
        }
