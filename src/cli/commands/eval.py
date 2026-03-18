from __future__ import annotations

import argparse

from src.cli.shared import finalize_command, load_runtime_context
from src.workflows.evaluation import run_evaluation


def run(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    return finalize_command(ctx, manifest, "eval", run_evaluation(ctx, baseline_label=args.baseline_label))
