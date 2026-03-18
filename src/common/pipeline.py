from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.common.config import LoadedConfig
from src.common.paths import ProjectPaths
from src.common.runtime import ensure_dir, generate_run_id, now_utc_iso, sha256_file, write_json


@dataclass
class RunContext:
    root: Path
    config: LoadedConfig
    pdf_path: Path
    source_hash: str
    run_id: str
    output_dir: Path

    @classmethod
    def create(cls, root: Path, config: LoadedConfig, pdf_override: str | None = None) -> "RunContext":
        project_paths = ProjectPaths(root, config)
        pdf_path = project_paths.document_pdf(pdf_override)
        source_hash = sha256_file(pdf_path)
        run_id = generate_run_id(source_hash)
        output_root = project_paths.output_root
        output_dir = ensure_dir(output_root / run_id)
        return cls(root=root, config=config, pdf_path=pdf_path, source_hash=source_hash, run_id=run_id, output_dir=output_dir)

    @property
    def paths(self) -> ProjectPaths:
        return ProjectPaths(self.root, self.config)

    def path_from_config(self, *keys: str) -> Path:
        return self.paths.path_from_config(*keys)

    def output_path(self, relative: str) -> Path:
        return self.output_dir / relative

    def read_jsonl(self, *keys: str) -> list[dict[str, Any]]:
        from src.common.runtime import read_jsonl

        return read_jsonl(self.path_from_config(*keys))

    def _display_path(self, path: Path) -> str:
        if path.is_relative_to(self.root):
            return str(path.relative_to(self.root))
        return str(path)

    def init_run_manifest(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "source_file": self._display_path(self.pdf_path),
            "source_hash": self.source_hash,
            "config_file": self._display_path(self.config.path),
            "config_hash": self.config.hash,
            "git_commit": None,
            "started_at": now_utc_iso(),
            "finished_at": None,
            "status": "partial",
            "steps_completed": [],
            "artifacts": [],
            "metrics": {},
            "notes": None,
        }

    def write_run_manifest(self, manifest: dict[str, Any]) -> None:
        write_json(self.output_path("run_manifest.json"), manifest)
