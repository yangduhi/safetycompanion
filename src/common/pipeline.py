from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.common.config import LoadedConfig
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
        pdf_path = root / (pdf_override or config.get("document", "pdf_path"))
        source_hash = sha256_file(pdf_path)
        run_id = generate_run_id(source_hash)
        output_root = root / config.get("runtime", "output_root", default="outputs")
        output_dir = ensure_dir(output_root / run_id)
        return cls(root=root, config=config, pdf_path=pdf_path, source_hash=source_hash, run_id=run_id, output_dir=output_dir)

    def path_from_config(self, *keys: str) -> Path:
        rel = self.config.get("paths", *keys)
        if rel is None:
            raise KeyError(f"Missing config path for keys={keys!r}")
        return self.root / rel

    def output_path(self, relative: str) -> Path:
        return self.output_dir / relative

    def init_run_manifest(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "source_file": str(self.pdf_path.relative_to(self.root)),
            "source_hash": self.source_hash,
            "config_file": str(self.config.path.relative_to(self.root)),
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
