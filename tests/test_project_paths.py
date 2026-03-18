from pathlib import Path

from src.common.config import load_config
from src.common.paths import ProjectPaths


ROOT = Path(__file__).resolve().parents[1]


def test_project_paths_use_config_and_default_index_locations():
    config = load_config(ROOT / "configs" / "project.yaml")
    paths = ProjectPaths(ROOT, config)

    assert paths.document_pdf() == ROOT / "data" / "SafetyCompanion-2026.pdf"
    assert paths.dense_entry_index == ROOT / "indexes" / "dense_entry" / "index.joblib"
    assert paths.calendar_lookup_store == ROOT / "indexes" / "lookup" / "calendar.json"
