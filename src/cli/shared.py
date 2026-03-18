from __future__ import annotations

import sys
from pathlib import Path

from src.common.config import load_config
from src.common.pipeline import RunContext
from src.common.runtime import now_utc_iso
from src.workflows.result import WorkflowResult


ROOT = Path(__file__).resolve().parents[2]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def default_config_path() -> Path:
    prod = ROOT / "configs" / "prod.yaml"
    return prod if prod.exists() else ROOT / "configs" / "project.yaml"


def load_runtime_context(config_path: str | None, pdf_override: str | None = None) -> RunContext:
    config = load_config(config_path or default_config_path())
    return RunContext.create(ROOT, config, pdf_override=pdf_override)


def write_manifest_status(
    ctx: RunContext,
    manifest: dict,
    status: str,
    step_name: str,
    artifacts: list[Path] | None = None,
    metrics: dict | None = None,
) -> None:
    manifest["status"] = status
    manifest["finished_at"] = now_utc_iso()
    manifest.setdefault("steps_completed", []).append(step_name)
    if artifacts:
        manifest.setdefault("artifacts", []).extend(str(path.relative_to(ROOT)) for path in artifacts)
    if metrics:
        manifest.setdefault("metrics", {}).update(metrics)
    ctx.write_run_manifest(manifest)


def finalize_command(ctx: RunContext, manifest: dict, step_name: str, result: WorkflowResult) -> int:
    status = "success" if result.success else "failed"
    write_manifest_status(ctx, manifest, status, step_name, artifacts=result.artifacts, metrics=result.metrics)
    if result.output_text:
        print(result.output_text)
    return 0 if result.success else 1
