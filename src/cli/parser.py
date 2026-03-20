from __future__ import annotations

import argparse

from src.cli.commands import build_indexes, eval as eval_command, ingest, preflight, query
from src.cli.shared import default_config_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SafetyCompanion RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight_parser = subparsers.add_parser("preflight")
    preflight_parser.add_argument("--config", default=None)
    preflight_parser.set_defaults(func=preflight.run)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--pdf", required=True)
    ingest_parser.add_argument("--config", default=str(default_config_path()))
    ingest_parser.set_defaults(func=ingest.run)

    build_indexes_parser = subparsers.add_parser("build-indexes")
    build_indexes_parser.add_argument("--config", default=str(default_config_path()))
    build_indexes_parser.set_defaults(func=build_indexes.run)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("question", nargs="?")
    query_parser.add_argument("--question-file", default=None)
    query_parser.add_argument("--config", default=str(default_config_path()))
    query_parser.set_defaults(func=query.run)

    eval_parser = subparsers.add_parser("eval")
    eval_parser.add_argument("--config", default=str(default_config_path()))
    eval_parser.add_argument("--baseline-label", default=None)
    eval_parser.set_defaults(func=eval_command.run)
    return parser
