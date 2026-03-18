from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.config import LoadedConfig


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    config: LoadedConfig

    def resolve(self, value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def path_from_config(self, *keys: str, default: str | None = None) -> Path:
        rel = self.config.get("paths", *keys, default=default)
        if rel is None:
            raise KeyError(f"Missing config path for keys={keys!r}")
        return self.resolve(rel)

    def document_pdf(self, override: str | None = None) -> Path:
        rel = override or self.config.get("document", "pdf_path")
        if rel is None:
            raise KeyError("Missing document.pdf_path in config")
        return self.resolve(rel)

    @property
    def output_root(self) -> Path:
        return self.resolve(self.config.get("runtime", "output_root", default="outputs"))

    @property
    def index_root(self) -> Path:
        return self.path_from_config("index_root", default="indexes")

    @property
    def dense_entry_index(self) -> Path:
        return self.index_root / "dense_entry" / "index.joblib"

    @property
    def dense_field_index(self) -> Path:
        return self.index_root / "dense_field" / "index.joblib"

    @property
    def bm25_index(self) -> Path:
        return self.index_root / "bm25" / "index.joblib"

    @property
    def lookup_dir(self) -> Path:
        return self.index_root / "lookup"

    def lookup_store(self, name: str) -> Path:
        return self.lookup_dir / f"{name}.json"

    @property
    def abbreviation_lookup_store(self) -> Path:
        return self.lookup_store("abbreviations")

    @property
    def back_index_lookup_store(self) -> Path:
        return self.lookup_store("back_index")

    @property
    def calendar_lookup_store(self) -> Path:
        return self.lookup_store("calendar")

    @property
    def route_policy_path(self) -> Path:
        return self.path_from_config("route_field_priority", default="configs/route_field_priority.yaml")

    @property
    def graph_nodes_path(self) -> Path:
        return self.path_from_config("graph_nodes", default="data/graph/nodes.jsonl")

    @property
    def graph_edges_path(self) -> Path:
        return self.path_from_config("graph_edges", default="data/graph/edges.jsonl")
