from __future__ import annotations

import argparse

from src.cli.shared import finalize_command, load_runtime_context
from src.workflows.ingest import run_ingest


def run(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config, pdf_override=args.pdf)
    manifest = ctx.init_run_manifest()
    return finalize_command(ctx, manifest, "ingest", run_ingest(ctx))
