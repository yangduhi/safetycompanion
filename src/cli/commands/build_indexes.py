from __future__ import annotations

import argparse

from src.cli.shared import finalize_command, load_runtime_context
from src.workflows.indexes import run_build_indexes


def run(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    return finalize_command(ctx, manifest, "build-indexes", run_build_indexes(ctx))
