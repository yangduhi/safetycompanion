from __future__ import annotations

import shutil

from src.common.pipeline import RunContext
from src.common.runtime import write_text
from src.workflows.result import WorkflowResult


def run_preflight(ctx: RunContext) -> WorkflowResult:
    lines = ["# Preflight Report", ""]
    required_commands = ["python", "pdfinfo", "pdftotext"]
    success = True
    for command in required_commands:
        found = shutil.which(command) is not None
        lines.append(f"- {command}: {'ok' if found else 'missing'}")
        success = success and found
    pdf_exists = ctx.pdf_path.exists()
    lines.append(f"- pdf exists: {pdf_exists}")
    success = success and pdf_exists

    report_path = ctx.output_path("preflight_report.md")
    write_text(report_path, "\n".join(lines) + "\n")
    return WorkflowResult(
        artifacts=[report_path],
        output_text=report_path.read_text(encoding="utf-8"),
        success=success,
    )
