from __future__ import annotations

import argparse

from src.cli.shared import finalize_command, load_runtime_context
from src.workflows.query import run_query


def run(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    return finalize_command(ctx, manifest, "query", run_query(ctx, args.question))
