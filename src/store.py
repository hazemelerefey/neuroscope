"""
Shared in-memory graph store.

This module provides a single shared store for parsed model graphs,
used by upload, analyze, compare, and export routes.
"""

import threading
from typing import Dict, Optional
from src.graph import NeuroScopeGraph


class GraphStore:
    """Thread-safe in-memory store for parsed model graphs."""

    def __init__(self) -> None:
        self._store: Dict[str, NeuroScopeGraph] = {}
        self._lock = threading.Lock()

    def put(self, model_id: str, graph: NeuroScopeGraph) -> None:
        """Store a graph with the given model_id."""
        with self._lock:
            self._store[model_id] = graph

    def get(self, model_id: str) -> Optional[NeuroScopeGraph]:
        """Retrieve a graph by model_id. Returns None if not found."""
        with self._lock:
            return self._store.get(model_id)

    def has(self, model_id: str) -> bool:
        """Check if a model_id exists in the store."""
        with self._lock:
            return model_id in self._store

    def remove(self, model_id: str) -> bool:
        """Remove a graph by model_id. Returns True if removed."""
        with self._lock:
            if model_id in self._store:
                del self._store[model_id]
                return True
            return False

    def list_models(self) -> list[str]:
        """List all stored model IDs."""
        with self._lock:
            return list(self._store.keys())

    def clear(self) -> None:
        """Remove all stored graphs."""
        with self._lock:
            self._store.clear()


# Singleton instance shared across all routes
graph_store = GraphStore()
