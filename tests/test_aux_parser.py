from pathlib import Path

from src.common.config import LoadedConfig
from src.parse.opendataloader_parser import extract_page_texts_from_odl_json
from src.parse.pdf_parser import build_page_records, select_auxiliary_pages


def _config(**auxiliary: object) -> LoadedConfig:
    return LoadedConfig(
        path=Path("test-config.yaml"),
        data={
            "parse": {
                "auxiliary": {
                    "enabled": True,
                    "engine": "opendataloader",
                    "page_types": ["knowledge"],
                    "min_word_count": 80,
                    "strict": False,
                    **auxiliary,
                }
            }
        },
    )


def test_select_auxiliary_pages_filters_by_page_type_and_word_count():
    manifest = [
        {"pdf_page": 7, "page_type": "knowledge", "word_count": 210},
        {"pdf_page": 15, "page_type": "event", "word_count": 300},
        {"pdf_page": 60, "page_type": "knowledge", "word_count": 42},
    ]

    assert select_auxiliary_pages(manifest, _config()) == [7]


def test_select_auxiliary_pages_respects_whitelist():
    manifest = [
        {"pdf_page": 60, "page_type": "knowledge", "word_count": 210},
        {"pdf_page": 61, "page_type": "knowledge", "word_count": 230},
        {"pdf_page": 84, "page_type": "knowledge", "word_count": 240},
    ]

    assert select_auxiliary_pages(manifest, _config(page_numbers=[60, 84])) == [60, 84]


def test_extract_page_texts_from_odl_json_flattens_nested_content():
    payload = {
        "kids": [
            {"type": "heading", "page number": 7, "content": "Current Dummy Landscape"},
            {
                "type": "table",
                "page number": 7,
                "rows": [
                    {"cells": [{"content": "THOR 50 %"}, {"content": "WorldSID"}]},
                    {"cells": [{"content": "HIII 50 %"}, {"content": "BioRID-II"}]},
                ],
            },
            {"type": "paragraph", "page number": 8, "content": "Dummy Trainings"},
        ]
    }

    assert extract_page_texts_from_odl_json(payload) == {
        7: "Current Dummy Landscape\nTHOR 50 %\nWorldSID\nHIII 50 %\nBioRID-II",
        8: "Dummy Trainings",
    }


def test_build_page_records_replaces_selected_pages_with_auxiliary_output(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "src.parse.pdf_parser.extract_text_pages",
        lambda pdf_path, temp_dir: [
            "Passive Safety\nSafetyWissen.com Wissen\nOriginal Knowledge Title\nLine one\nLine two\nLine three",
            "Active & Passive Safety\nEvent\nAutomotive Safety Summit",
        ],
    )
    monkeypatch.setattr(
        "src.parse.pdf_parser.parse_pages_with_opendataloader",
        lambda pdf_path, pages, temp_dir, config: {
            1: "Passive Safety\nSafetyWissen.com Wissen\nImproved Knowledge Title\nHeader A\nHeader B\nHeader C\nHeader D"
        },
    )

    manifest, blocks, diagnostics = build_page_records(
        pdf_path=tmp_path / "dummy.pdf",
        document_id="doc-1",
        temp_dir=tmp_path,
        config=_config(min_word_count=0),
    )

    assert manifest[0]["parser_engine"] == "opendataloader"
    assert manifest[0]["title"] == "SafetyWissen.com Wissen Improved Knowledge Title"
    assert manifest[1]["parser_engine"] == "pdftotext"
    assert blocks[0]["parser_engine"] == "opendataloader"
    assert diagnostics["candidate_pages"] == [1]
    assert diagnostics["reparsed_pages"] == [1]


def test_build_page_records_falls_back_to_pdftotext_when_auxiliary_parser_fails(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "src.parse.pdf_parser.extract_text_pages",
        lambda pdf_path, temp_dir: [
            "Passive Safety\nSafetyWissen.com Wissen\nOriginal Knowledge Title\nLine one\nLine two\nLine three"
        ],
    )
    monkeypatch.setattr(
        "src.parse.pdf_parser.parse_pages_with_opendataloader",
        lambda pdf_path, pages, temp_dir, config: (_ for _ in ()).throw(FileNotFoundError("opendataloader-pdf is not available")),
    )

    manifest, blocks, diagnostics = build_page_records(
        pdf_path=tmp_path / "dummy.pdf",
        document_id="doc-2",
        temp_dir=tmp_path,
        config=_config(min_word_count=0),
    )

    assert manifest[0]["parser_engine"] == "pdftotext"
    assert blocks[0]["parser_engine"] == "pdftotext"
    assert diagnostics["reparsed_pages"] == []
    assert "not available" in str(diagnostics["fallback_reason"])
