"""Offline tests for eval/ (no network, no API key)."""
import importlib.util
from pathlib import Path

import pytest

from validator import loaders

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "eval" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


score = _load("score")


def test_golden_lines_point_into_document():
    lines = (ROOT / "docs" / "requirements.md").read_text(encoding="utf-8").splitlines()
    golden = score.load_golden()
    assert len(golden) >= 25
    assert sum(d.key for d in golden) == 5
    assert len({d.id for d in golden}) == len(golden)
    for d in golden:
        for n in d.lines:
            assert 1 <= n <= len(lines) and lines[n - 1].strip(), f"{d.id}: line {n} is empty or outside"


def test_match_needs_line_and_keyword():
    d = score.Defect(id="X", title="", lines=[104], keywords=["get"])
    assert score.matches({"line": 104, "quote": "REST type GET"}, d)
    assert not score.matches({"line": 105, "quote": "REST type GET"}, d)  # wrong line
    assert not score.matches({"line": 104, "quote": "Authorization"}, d)  # no keyword
    assert not score.matches({"line": None, "quote": "GET"}, d)  # ungrounded finding


def test_keyword_matches_word_start_only():
    d = score.Defect(id="X", title="", lines=[1], keywords=["дат"])
    assert score.matches({"line": 1, "problem": "по дате покупки"}, d)
    assert not score.matches({"line": 1, "problem": "кандидат"}, d)


def test_score_counts_found_key_and_unmatched():
    golden = score.load_golden()
    report = {"findings": [
        {"id": "F-001", "line": 104, "quote": "REST type GET", "problem": "сохранение через GET"},
        {"id": "F-002", "line": 189, "quote": "Для чужой карты возвращается 404", "problem": "противоречит 403"},
        {"id": "F-003", "line": 1, "quote": "# Уведомление о расходах по карте", "problem": "заголовок"},
    ]}
    s = score.score(report, golden, name="t")
    assert s.hits["G03"] == ["F-001"]
    assert s.hits["G05"] == ["F-002"]
    assert s.unmatched == ["F-003"]
    assert s.found == 2
    out = score.render([s], golden)
    assert "найдено 2/" in out and "ключевых 2/5" in out


def test_score_cli_min_recall(tmp_path):
    p = tmp_path / "r.json"
    p.write_text('{"findings": []}', encoding="utf-8")
    assert score.main([str(p)]) == 0
    assert score.main([str(p), "--min-recall", "0.5"]) == 1


def test_baseline_locates_quotes():
    baseline = _load("baseline")
    doc = loaders.load(str(ROOT / "docs" / "requirements.md"))
    assert baseline.locate(doc, "REST type** | GET") == 104
    assert baseline.locate(doc, "Для чужой карты возвращается 404") == 189
    assert baseline.locate(doc, "такой фразы в документе нет") is None


@pytest.mark.parametrize("name", ["requirements.pdf", "requirements.docx"])
def test_sample_inputs_keep_key_text(name):
    text = loaders.load(str(ROOT / "samples" / name)).text
    for needle in ["Ф-1", "Ф-3", "Ф-4", "saveLimit", "31 января", "Карта не найдена"]:
        assert needle in text, f"{name}: lost {needle!r}"


def test_pdf_tidy_removes_run_split_spaces():
    assert loaders._tidy_pdf_text("Алматы . Ф -2. версия /дата Да / Нет") == "Алматы. Ф-2. версия/дата Да / Нет"
